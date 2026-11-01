# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Face test, each painting nudged into agreement with the others before projection - Floating Textures (Eisemann et
al., Computer Graphics Forum 27(2), Eurographics 2008; Dellepiane et al., IEEE TVCG 2012): projected pictures that
disagree by a few pixels blur and ghost where they blend and jump where one camera's part meets another's; optical flow
between them, applied before blending, fixes it. The approved alignment rec (TASKS, 2026-10-31): flow on top of the
coarse landmark warp, OpenCV's DIS first.

Per view i:
1. every other view j's light-free colours (delight_views.py) re-projected into camera i through our mesh - each pixel
   of i unprojected by its depth picture, projected into j, kept where j's depth picture sees the same point and away
   from its outlines;
2. optical flow from i to each (OpenCV's DIS, Kroeger et al., ECCV 2016), on brightness levelled per picture;
3. i warped by the weighted mean of those flows, its own zero flow included - each view moves to where the views that
   see a spot well agree it is. The weights: each view's facing, cos^4 of the angle to its camera (the projection's
   broad band).
Writes flowed_albedo_<view>.npy and flowed_nworld_<view>.npy (test_face_project.py reads them with FACETEST_FLOW=1).

The judge (`--judge VIEW ...`): each named view is left out of the flows; the others' colours re-projected to its camera
and blended, before the flow and after, are compared with its own painting on structure (correlation of the detail
band, difference of Gaussians 1.5 - 4 px, over the face); their sharpness is printed apart, since agreement alone would
reward blur. Nothing is written.

Run (the tool environment): .dev/venv-rdf/Scripts/python -I tools/face_test/flow_views.py [--judge VIEW ...]
(FACETEST_FLOW_METHOD=raft for RAFT instead of DIS: judged 2026-10-31, no better.)
"""

import json
import os
import sys
from pathlib import Path

import cv2
import numpy as np
import OpenEXR

DIR = Path("E:/Dev/3D/just-stage/.dev/facetest")
VIEWS = ("front", "left40", "right40", "left90", "right90", "above", "below", "face", "faceleft30", "faceright30")
LUMA = np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
MAX_FLOW = 15.0  # px: the landmark warp already took the large moves (residuals 3.5-10 px); more is a wrong match
SMOOTH = 3.0  # px: the mean flow blurred, so the warp can't tear fine detail
#: the judge's detail bands (difference of Gaussians, px): pores - each painting invents its own (round 50: the
#: close view against the others correlates 0.05 there) - then features (lids, nostrils, the lips' line)
BANDS = ((1.5, 4.0), (3.0, 8.0), (6.0, 16.0))
FINEST = 2  # DIS stops at a quarter of the resolution: features, not the pores no two paintings share


def depth(view):
    with OpenEXR.File(str(DIR / f"depth_{view}.exr")) as exr:
        ch = exr.channels()
        px = (ch.get("RGB", ch.get("RGBA")) or next(iter(ch.values()))).pixels
    return (px[..., 0] if px.ndim == 3 else px).astype(np.float64)


class View:
    """One camera: its depth picture's surface points and normals in world space, what it covers, its colours."""

    def __init__(self, name, cam):
        self.name, self.size = name, cam["size"]
        self.mw = np.array(cam["matrix_world"], dtype=np.float64)
        self.f = cam["lens"] / cam["sensor_width"] * self.size
        self.dist = depth(name)
        jj, ii = np.meshgrid(np.arange(self.size), np.arange(self.size))
        ray = np.stack([(jj + 0.5 - self.size / 2) / self.f, -(ii + 0.5 - self.size / 2) / self.f,
                        -np.ones_like(jj, float)], axis=2)
        ray /= np.linalg.norm(ray, axis=2, keepdims=True)
        p = ray * self.dist[..., None]
        n = np.cross(np.gradient(p, axis=0), np.gradient(p, axis=1))
        n /= np.maximum(np.linalg.norm(n, axis=2, keepdims=True), 1e-12)
        n[n[..., 2] < 0] *= -1
        self.covered = self.dist < 0.999  # the background reads 1.0 in the view-distance picture
        # away from outlines and depth jumps (a jaw in front of the neck): those pixels blend two surfaces
        near = np.where(self.covered, self.dist, 1.0).astype(np.float32)
        k = np.ones((5, 5), np.uint8)
        smooth = self.covered & (cv2.dilate(near, k) - cv2.erode(near, k) < 0.01)
        self.inner = cv2.erode(smooth.astype(np.uint8), k).astype(bool)
        self.points = p @ self.mw[:3, :3].T + self.mw[:3, 3]
        self.normals = n @ self.mw[:3, :3].T
        self.facing = self._facing(self.points, self.normals)
        self.albedo = np.load(DIR / f"albedo_{name}.npy").astype(np.float32)
        self.nworld = np.load(DIR / f"nworld_{name}.npy").astype(np.float32)

    def _facing(self, points, normals):
        to_cam = self.mw[:3, 3] - points
        to_cam /= np.maximum(np.linalg.norm(to_cam, axis=-1, keepdims=True), 1e-12)
        return np.clip((normals * to_cam).sum(-1), 0.0, 1.0) ** 4

    def seen_from(self, other):
        """Where `other`'s pixels land in this camera (column, row maps) and how much this view counts there: visible
        (its depth picture sees the same point within 3 mm), clear of its outlines, its facing."""
        inv = np.linalg.inv(self.mw)
        cam = other.points @ inv[:3, :3].T + inv[:3, 3]
        d = -cam[..., 2]
        with np.errstate(divide="ignore", invalid="ignore"):
            col = (self.size / 2 + self.f * cam[..., 0] / d - 0.5).astype(np.float32)
            row = (self.size / 2 - self.f * cam[..., 1] / d - 0.5).astype(np.float32)
        col, row = np.nan_to_num(col, nan=-1.0), np.nan_to_num(row, nan=-1.0)
        seen = cv2.remap(self.dist.astype(np.float32), col, row, cv2.INTER_LINEAR, borderValue=1.0)
        clear = cv2.remap(self.inner.astype(np.float32), col, row, cv2.INTER_LINEAR, borderValue=0.0)
        ok = other.inner & (d > 0) & (np.abs(seen - np.linalg.norm(cam, axis=-1)) < 0.003) & (clear > 0.99)
        return col, row, np.where(ok, self._facing(other.points, other.normals), 0.0)


def grey(albedo, mask):
    """Brightness for the flow: luminance levelled to its median over `mask`, gamma'd, 8-bit."""
    lum = albedo @ LUMA
    lum = lum / max(float(np.median(lum[mask])), 1e-6)
    return np.clip(lum ** (1 / 2.2) * 110.0, 0, 255).astype(np.uint8)


def masked_blur(a, w, sigma):
    num = cv2.GaussianBlur((a * w[..., None]).astype(np.float32), (0, 0), sigma)
    den = cv2.GaussianBlur(w.astype(np.float32), (0, 0), sigma)
    return num / np.maximum(den[..., None], 1e-6)


def flow_for(view, others, dis):
    """The weighted mean flow that brings `view` to where `others` agree its pixels are (H x W x 2, pixels)."""
    total = np.zeros(view.albedo.shape[:2] + (2,), np.float32)
    weight = np.where(view.inner, view.facing, 0.0).astype(np.float32)  # its own zero flow
    for other in others:
        col, row, w = other.seen_from(view)
        if (w > 0.05).sum() < 2000:
            continue
        theirs = cv2.remap(other.albedo, col, row, cv2.INTER_LINEAR)
        overlap = (w > 0.05) & view.inner
        mine_g, theirs_g = grey(view.albedo, overlap), grey(theirs, overlap)
        theirs_g = np.where(w > 0.05, theirs_g, mine_g)  # elsewhere nothing to match: the flow stays near zero
        f = dis.calc(theirs_g, mine_g, None)  # theirs(x) ~ mine(x + f(x))
        back = warp(dis.calc(mine_g, theirs_g, None), f, cv2.INTER_LINEAR)  # the reverse flow, where f lands
        # forward-backward consistency (Sundaram, Brox & Keutzer, ECCV 2010): kept only where the reverse flow returns
        # - on smooth skin whose shading differs between paintings DIS matches noise (round 52: raw flows 20-37 px at
        # the median, the mean at its 15 px cap over half the face)
        ok = (f + back) ** 2 @ np.ones(2) < 0.01 * ((f**2) @ np.ones(2) + (back**2) @ np.ones(2)) + 0.5
        kept = w * ok
        total += f * kept[..., None]
        weight += kept
    mean = total / np.maximum(weight[..., None], 1e-6)
    mean *= np.minimum(1.0, MAX_FLOW / np.maximum(np.linalg.norm(mean, axis=2, keepdims=True), 1e-6))
    return masked_blur(mean, view.inner.astype(np.float32), SMOOTH) * view.inner[..., None]


def warp(img, flow, interpolation=cv2.INTER_LANCZOS4):
    """`img` resampled at each pixel plus its flow - Lanczos by default: bilinear softened the pores ~20% (round 52)."""
    h, w = img.shape[:2]
    jj, ii = np.meshgrid(np.arange(w, dtype=np.float32), np.arange(h, dtype=np.float32))
    return cv2.remap(img, jj + flow[..., 0], ii + flow[..., 1], interpolation, borderMode=cv2.BORDER_REPLICATE)


def blended_at(view, others, attr):
    """The others' colours re-projected into `view`'s camera and blended by their facing, and the weight there."""
    num = np.zeros(view.albedo.shape, np.float32)
    den = np.zeros(view.albedo.shape[:2], np.float32)
    for other in others:
        col, row, w = other.seen_from(view)
        num += cv2.remap(getattr(other, attr), col, row, cv2.INTER_LINEAR) * w[..., None]
        den += w
    return num / np.maximum(den[..., None], 1e-6), den


def detail(g, lo=1.5, hi=4.0):
    g = g.astype(np.float32)
    return cv2.GaussianBlur(g, (0, 0), lo) - cv2.GaussianBlur(g, (0, 0), hi)


def judge(names, views, dis):
    for name in names:
        held = views[name]
        others = [v for k, v in views.items() if k != name]
        before, den = blended_at(held, others, "albedo")
        for v in others:
            v.flowed = warp(v.albedo, flow_for(v, [o for o in others if o is not v], dis))
        after, _ = blended_at(held, others, "flowed")
        # away from where the others see nothing (outlines, depth jumps): a band's blur would carry those edges in
        seen = held.inner & (den > 0.2 * np.percentile(den[held.inner], 99))
        face = cv2.erode(seen.astype(np.uint8), np.ones((25, 25), np.uint8)).astype(bool)
        for lo, hi in BANDS:
            mine = detail(grey(held.albedo, face), lo, hi)[face]
            rows = []
            for tag, img in (("before", before), ("after", after)):
                d = detail(grey(np.where(seen[..., None], img, held.albedo), face), lo, hi)[face]
                rows.append(f"{tag} {np.corrcoef(mine, d)[0, 1]:.3f} (sharpness {d.var():.1f})")
            print(f"judge {name}, band {lo:g}-{hi:g} px over {face.mean():.0%} of the picture: " + ", ".join(rows)
                  + f"; the painting's {mine.var():.1f}")


class Raft:
    """RAFT (Teed & Deng, ECCV 2020; torchvision's `raft_large`, code and weights BSD-3) with DIS's `calc`: flow from
    the first grey picture to the second, run at half size and scaled back (on the CPU while the card is lent)."""

    def __init__(self):
        os.environ.setdefault("TORCH_HOME", str(Path("E:/Dev/3D/just-stage/.dev/cache/torch")))
        import torch
        from torchvision.models.optical_flow import Raft_Large_Weights, raft_large

        self.torch = torch
        torch.set_num_threads(os.cpu_count() or 4)
        self.model = raft_large(weights=Raft_Large_Weights.C_T_SKHT_V2).eval()

    def calc(self, first, second, _flow=None):
        torch = self.torch
        h, w = first.shape

        def batch(g):
            small = cv2.resize(g, (w // 2, h // 2), interpolation=cv2.INTER_AREA).astype(np.float32) / 127.5 - 1.0
            return torch.from_numpy(np.repeat(small[None, None], 3, axis=1))

        with torch.no_grad():
            flow = self.model(batch(first), batch(second), num_flow_updates=12)[-1][0].permute(1, 2, 0).numpy()
        return cv2.resize(flow, (w, h), interpolation=cv2.INTER_LINEAR) * 2.0


def main(argv) -> int:
    cams = json.load(open(DIR / "cameras.json"))
    views = {name: View(name, cams[name]) for name in VIEWS}
    if os.environ.get("FACETEST_FLOW_METHOD", "dis") == "raft":
        dis = Raft()
    else:
        dis = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
        dis.setFinestScale(FINEST)
    if argv[:1] == ["--judge"]:
        judge(argv[1:] or ["face"], views, dis)
        return 0
    for name, view in views.items():
        flow = flow_for(view, [v for k, v in views.items() if k != name], dis)
        mag = np.linalg.norm(flow, axis=2)[view.inner]
        np.save(DIR / f"flowed_albedo_{name}.npy", warp(view.albedo, flow).astype(np.float16))
        n = warp(view.nworld, flow)
        np.save(DIR / f"flowed_nworld_{name}.npy", (n / np.maximum(np.linalg.norm(n, axis=2, keepdims=True), 1e-6)).astype(np.float16))
        print(f"{name}: moved {mag.mean():.1f} px on average (95th percentile {np.percentile(mag, 95):.1f})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Face test, the shape (research rec 4): our head made the painted person.

1. `infer`: RealDenseFace (LinzhouLi/RealDenseFace, MIT; ViT-B weights) reads each painting AND each clay view of our
   head and predicts, for every FLAME vertex, where it lies in the picture and how sure it is - RealDenseFace's own
   inference: the face box (here from MediaPipe's points) enlarged 1.3x and squared, a 512 px crop, its UV-space maps
   sampled at FLAME's vertex UVs.
2. `fit`: FLAME 2023 Open (CC-BY-4.0) fitted to the paintings' predictions in every view at once, through the views'
   own cameras - one identity and expression shared by all views, the head's pose and scale free (the earlier landmark
   fit failed because only identity was free - RESEARCH section 10) - and, the same way, to the clay views'
   predictions. Both go through the same network, so its own leanings cancel in their difference: what the AI changed
   from our head (the first version fitted our head in 3D instead, and the network's leaning landed on the head as
   shape - its eyes drifted 18 -> 28 px from the paintings). The difference (identity, expression, jaw; not the pose)
   is carried to our head through FLAME fitted to our head's surface in 3D (each head vertex follows its nearest FLAME
   points), faded out beyond FLAME's face. Written to fit_offsets.npz, which face_shape.apply_fit adds as a shape key.

Run (the tool environment with PyTorch; `infer` needs the card, `fit` runs on the processor):
  .dev/venv-rdf/Scripts/python -I tools/face_test/flame_fit.py infer
  .dev/venv-rdf/Scripts/python -I tools/face_test/flame_fit.py fit
"""

import importlib
import json
import pickle
import sys
import time
from pathlib import Path

import cv2
import numpy as np
import torch
import yaml
from scipy.spatial import cKDTree

DIR = Path("E:/Dev/3D/just-stage/.dev/facetest")
CACHE = Path("E:/Dev/3D/just-stage/.dev/cache")
RDF_REPO = CACHE / "src" / "RealDenseFace"  # 4dbdf1de
RDF = CACHE / "realdenseface"
FLAME_OPEN = CACHE / "flame" / "open" / "flame2023_Open.pkl"
FLAME_MASKS = CACHE / "flame" / "masks" / "FLAME_masks.pkl"
VIEWS = ("front", "left40", "right40", "above", "below", "face", "faceleft30", "faceright30")
#: the pictures read: the paintings, and the clay views of our head with its mouth and lid keys but no fit (the shape
#: the fit's offsets are added to)
SOURCES = {"painted": lambda v: DIR / f"painted_{v}.png", "clay": lambda v: DIR / "clay_nofit" / f"clay_{v}.png"}
N_ID, N_EX = 300, 100  # FLAME 2023 Open: 400 directions, the last 100 expressions (its supr_expression_metadata)
FACE_PARTS = ("face", "nose", "lips", "eye_region", "forehead")  # what the pictures show well
SKIN = 13380  # hm08's body vertices; the rest are helpers (eyes, teeth, ...) inside the head
ALLOWED = {("numpy", "dtype"), ("numpy", "ndarray"), ("numpy.core.numeric", "_frombuffer"),
           ("numpy.core.multiarray", "_reconstruct"), ("scipy.sparse._csc", "csc_matrix")}
DT = torch.float64


class _Safe(pickle.Unpickler):
    """The FLAME files hold only numpy arrays and one scipy matrix (read with pickletools): nothing else may load."""

    def find_class(self, module, name):
        if (module, name) not in ALLOWED:
            raise pickle.UnpicklingError(f"refused {module}.{name}")
        return getattr(importlib.import_module(module), name)


def load_pickle(path):
    with open(path, "rb") as f:
        return _Safe(f, encoding="latin1").load()


def rodrigues(r):
    """Axis-angle (..., 3) to rotation matrices (..., 3, 3)."""
    angle = torch.linalg.norm(r + 1e-8, dim=-1, keepdim=True)
    k = r / angle
    kx, ky, kz = k[..., 0], k[..., 1], k[..., 2]
    zero = torch.zeros_like(kx)
    K = torch.stack([zero, -kz, ky, kz, zero, -kx, -ky, kx, zero], dim=-1).reshape(*r.shape[:-1], 3, 3)
    eye = torch.eye(3, dtype=r.dtype).expand(K.shape)
    s, c = torch.sin(angle)[..., None], torch.cos(angle)[..., None]
    return eye + s * K + (1 - c) * (K @ K)


class Flame:
    """FLAME's forward model (Li et al. 2017): identity and expression blend shapes, pose correctives, linear blend
    skinning over its five joints (global, neck, jaw, two eyes) - the steps of the authors' FLAME_PyTorch through
    smplx's `lbs`. Only the jaw turns here; the head's pose is the fit's similarity transform."""

    def __init__(self):
        m = load_pickle(FLAME_OPEN)
        f64 = lambda a: torch.tensor(np.asarray(a), dtype=DT)  # noqa: E731
        self.template = f64(m["v_template"])
        self.shapedirs = f64(m["shapedirs"])  # (5023, 3, 400)
        self.posedirs = f64(m["posedirs"])  # (5023, 3, 36)
        self.J_regressor = f64(m["J_regressor"].toarray())
        self.weights = f64(m["weights"])
        self.parents = [int(p) for p in np.asarray(m["kintree_table"])[0]]
        self.faces = np.asarray(m["f"], np.int64)
        self.masks = {k: np.asarray(v, np.int64) for k, v in load_pickle(FLAME_MASKS).items()}

    def __call__(self, beta, psi, jaw):
        v = self.template + self.shapedirs @ torch.cat([beta, psi])
        J = self.J_regressor @ v
        zero = torch.zeros(2, 3, dtype=DT)
        R = rodrigues(torch.cat([zero, jaw[None], zero]))
        v = v + self.posedirs @ (R[1:] - torch.eye(3, dtype=DT)).reshape(-1)
        bottom = torch.tensor([[0.0, 0.0, 0.0, 1.0]], dtype=DT)
        G = []
        for k in range(5):
            offset = J[k] - J[self.parents[k]] if k else J[k]
            local = torch.cat([torch.cat([R[k], offset[:, None]], 1), bottom], 0)
            G.append(local if k == 0 else G[self.parents[k]] @ local)
        G = torch.stack(G)
        moved = G[:, :3, 3] - (G[:, :3, :3] @ J[:, :, None])[..., 0]  # each joint's transform about its rest place
        A = torch.cat([torch.cat([G[:, :3, :3], moved[:, :, None]], 2), G[:, 3:4, :]], 1)
        T = torch.einsum("vk,kij->vij", self.weights, A)
        return (T[:, :3, :3] @ v[:, :, None])[..., 0] + T[:, :3, 3]


def project(points, cam):
    """Blender's camera (looks down its -Z, y up), square picture: world points to pixel coordinates (x right, y down)."""
    M = torch.tensor(cam["matrix_world"], dtype=points.dtype)
    p = (points - M[:3, 3]) @ M[:3, :3]
    f = cam["lens"] / cam["sensor_width"] * cam["size"]
    c = cam["size"] / 2
    return torch.stack([f * p[:, 0] / -p[:, 2] + c, -f * p[:, 1] / -p[:, 2] + c], 1)


def infer():
    sys.path.insert(0, str(RDF_REPO / "models"))
    from realdenseface.model import RealDenseFace  # noqa: E402

    config = yaml.safe_load((RDF / "configs" / "model" / "vitb.yaml").read_text())
    config["dino_pretrained"] = False
    model = RealDenseFace(**config)
    model.load_state_dict(torch.load(RDF / "weights" / "realdenseface" / "vitb.pth", map_location="cpu", weights_only=True))
    model = model.cuda().eval()
    model.build_inference_cache()
    size = int(config["target_size"])
    assets = np.load(RDF / "weights" / "flame_assets.npz")
    grid = torch.tensor(assets["vertex_uvs"], dtype=torch.float32, device="cuda")[None, :, None] * 2.0 - 1.0
    mean = torch.tensor([0.485, 0.456, 0.406], device="cuda").view(1, 3, 1, 1)
    std = torch.tensor([0.229, 0.224, 0.225], device="cuda").view(1, 3, 1, 1)
    marks = json.loads((DIR / "landmarks.json").read_text())
    for kind, path in SOURCES.items():
        for view in VIEWS:
            img = cv2.imread(str(path(view)))[..., ::-1]
            pts = np.asarray(marks[view][kind])
            (x0, y0), (x1, y1) = pts.min(0), pts.max(0)
            cx, cy, half = (x0 + x1) / 2, (y0 + y1) / 2, max(x1 - x0, y1 - y0) * 1.3 / 2  # its enlarge 1.3, squared
            box = np.round([cx - half, cy - half, cx + half, cy + half]).astype(int)
            pad = int(max(0, -box[0], -box[1], box[2] - img.shape[1], box[3] - img.shape[0]))
            padded = cv2.copyMakeBorder(np.ascontiguousarray(img), pad, pad, pad, pad, cv2.BORDER_CONSTANT)
            crop = cv2.resize(padded[box[1] + pad:box[3] + pad, box[0] + pad:box[2] + pad], (size, size),
                              interpolation=cv2.INTER_LINEAR)
            x = (torch.tensor(crop, dtype=torch.float32, device="cuda").permute(2, 0, 1)[None] / 255.0 - mean) / std
            with torch.no_grad(), torch.autocast("cuda", dtype=torch.bfloat16):
                coords, coord_lv, _, _ = model(x)
            coords = coords.float() / config.get("scale_coord", 1.0) * 0.5 + 0.5

            def at_vertices(t):
                return torch.nn.functional.grid_sample(t.float(), grid, mode="bilinear", align_corners=False)[0, :, :, 0].T

            uv = at_vertices(coords).cpu().numpy()
            lv = at_vertices(torch.clamp(coord_lv.float(), -8.0, 3.0)).cpu().numpy()[:, 0]
            px = np.c_[uv[:, 0] * (box[2] - box[0]) + box[0], uv[:, 1] * (box[3] - box[1]) + box[1]]
            np.savez(DIR / f"rdf_{kind}_{view}.npz", px=px.astype(np.float32), log_var=lv.astype(np.float32), box=box)
            print(f"{kind} {view}: box {box.tolist()}, log variance median {np.median(lv):.2f}")


def _vertex_normals(verts, faces):
    tri = verts[faces]
    n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    vn = np.zeros_like(verts)
    for k in range(3):
        np.add.at(vn, faces[:, k], n)
    return vn / (np.linalg.norm(vn, axis=1, keepdims=True) + 1e-12)


def _facing(verts, faces, cam):
    """FLAME vertices that face this camera (a picture's far side of the nose and cheek get no say)."""
    to_cam = np.asarray(cam["matrix_world"])[:3, 3] - verts
    to_cam /= np.linalg.norm(to_cam, axis=1, keepdims=True)
    return (_vertex_normals(verts, faces) * to_cam).sum(1) > 0.25


def _placed(flame, p):
    v = flame(p["beta"], p["psi"], p["jaw"])
    return torch.exp(p["log_s"]) * v @ rodrigues(p["rot"]).T + p["t"]


def _prior(p):
    return 0.02 * (p["beta"] ** 2).sum() + 0.02 * (p["psi"] ** 2).sum() + 10.0 * (p["jaw"] ** 2).sum()


def _start():
    return {"beta": torch.zeros(N_ID, dtype=DT), "psi": torch.zeros(N_EX, dtype=DT), "jaw": torch.zeros(3, dtype=DT),
            "rot": torch.tensor([np.pi / 2, 0, 0], dtype=DT),  # FLAME is y-up facing +z; the scene z-up facing -y
            "t": torch.tensor([0.0, -0.058, 1.578], dtype=DT), "log_s": torch.zeros(1, dtype=DT)}


def fit_views(flame, kind, cams, region):
    """FLAME to one set of pictures' predictions, all views at once through their cameras."""
    obs = {v: np.load(DIR / f"rdf_{kind}_{v}.npz") for v in VIEWS}
    p = _start()
    for t in p.values():
        t.requires_grad_(True)
    target = {v: torch.tensor(obs[v]["px"], dtype=DT)[region] for v in VIEWS}
    conf = {v: torch.tensor(np.exp(-np.clip(obs[v]["log_var"], -8, 3)), dtype=DT)[region] for v in VIEWS}
    t0 = time.time()
    for stage, free, steps, lr in (("pose", ("rot", "t", "log_s"), 300, 0.01), ("shape", tuple(p), 1500, 0.005)):
        opt = torch.optim.Adam([p[k] for k in free], lr=lr)
        for step in range(steps):
            if step % 100 == 0:  # who faces each camera, from the current fit
                with torch.no_grad():
                    world = _placed(flame, p).numpy()
                seen = {v: torch.tensor(_facing(world, flame.faces, cams[v])[region], dtype=DT) for v in VIEWS}
            opt.zero_grad()
            world = _placed(flame, p)[region]
            loss = 0.0
            for v in VIEWS:
                r = torch.linalg.norm(project(world, cams[v]) - target[v], dim=1)
                w = conf[v] * seen[v]
                loss = loss + (w * torch.nn.functional.huber_loss(r, torch.zeros_like(r), delta=4.0, reduction="none")).sum() / w.sum()
            loss = loss / len(VIEWS) + _prior(p)
            loss.backward()
            opt.step()
    with torch.no_grad():
        world = _placed(flame, p)[region]
        errs = [f"{v} {np.median(torch.linalg.norm(project(world, cams[v]) - target[v], dim=1).numpy()[seen[v].numpy() > 0]):.1f}"
                for v in VIEWS]
    print(f"{kind}: {time.time() - t0:.0f}s, scale {torch.exp(p['log_s']).item():.3f}, |beta| {p['beta'].norm().item():.2f}, "
          f"|psi| {p['psi'].norm().item():.2f}; median px: {', '.join(errs)}")
    return {k: t.detach().clone() for k, t in p.items()}


def fit():
    flame = Flame()
    cams = json.loads((DIR / "cameras.json").read_text())
    region = np.unique(np.concatenate([flame.masks[k] for k in FACE_PARTS]))
    paint = fit_views(flame, "painted", cams, region)
    clay = fit_views(flame, "clay", cams, region)

    # FLAME onto our head's own surface (its neutral shape), from the clay fit's pose: only to tie FLAME's points to
    # our head's
    head = np.load(DIR / "head_neutral.npz")
    co = head["co"].astype(np.float64)
    skin_n = _vertex_normals(co, head["faces"].astype(np.int64))[:SKIN]
    tree = cKDTree(co[:SKIN])
    co_t, n_t = torch.tensor(co[:SKIN], dtype=DT), torch.tensor(skin_n, dtype=DT)
    p = {k: t.clone().requires_grad_(True) for k, t in clay.items()}
    opt = torch.optim.Adam(list(p.values()), lr=0.003)
    for step in range(1500):
        if step % 50 == 0:
            with torch.no_grad():
                dist, idx = tree.query(_placed(flame, p)[region].numpy())
            near, keep = torch.tensor(idx), torch.tensor(dist < 0.01, dtype=DT)
        opt.zero_grad()
        gap = _placed(flame, p)[region] - co_t[near]
        plane = (gap * n_t[near]).sum(1)  # point to plane: free to slide along the surface
        loss = (keep * (plane ** 2 + 0.1 * (gap ** 2).sum(1))).sum() / keep.sum() * 1e6 + _prior(p)
        loss.backward()
        opt.step()
    with torch.no_grad():
        on_head = _placed(flame, p).numpy()
    dist, _ = tree.query(on_head[region])
    print(f"our head: FLAME's face {np.median(dist) * 1000:.2f} mm from it (median), 90% within "
          f"{np.percentile(dist, 90) * 1000:.2f} mm")

    # what the AI changed: the painted fit's shape minus the clay fit's, both in the clay fit's pose
    with torch.no_grad():
        s_R = (rodrigues(clay["rot"]) * torch.exp(clay["log_s"])).numpy()
        delta = (flame(paint["beta"], paint["psi"], paint["jaw"]) - flame(clay["beta"], clay["psi"], clay["jaw"])).numpy() @ s_R.T
    weight = np.zeros(len(delta))
    weight[region] = 1.0
    rings = [set() for _ in weight]
    for a, b, c in flame.faces:
        rings[a].update((b, c))
        rings[b].update((a, c))
        rings[c].update((a, b))
    rings = [np.fromiter(r, np.int64) for r in rings]
    for _ in range(12):  # the fade beyond the face: neighbour averaging, ring by ring
        weight = np.array([0.5 * weight[i] + 0.5 * weight[r].mean() for i, r in enumerate(rings)])
    dist, idx = cKDTree(on_head).query(co, k=4)
    w = 1.0 / (dist + 1e-4)
    w /= w.sum(1, keepdims=True)
    offsets = (delta[idx] * (w * weight[idx])[..., None]).sum(1)
    offsets *= np.clip(1.0 - (dist.min(1) - 0.01) / 0.02, 0.0, 1.0)[:, None]  # nothing far from FLAME's surface
    np.savez(DIR / "fit_offsets.npz", offsets=offsets.astype(np.float32),
             **{f"{k}_{n}": t.numpy() for n, fitted in (("paint", paint), ("clay", clay)) for k, t in fitted.items()})
    moved = np.linalg.norm(offsets[:SKIN], axis=1)
    print(f"offsets: {int((moved > 0.0005).sum())} skin vertices move over 0.5 mm, at most {moved.max() * 1000:.1f} mm "
          f"(median of those {np.median(moved[moved > 0.0005]) * 1000:.1f})")


if __name__ == "__main__":
    {"infer": infer, "fit": fit}[sys.argv[1]]()

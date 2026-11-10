# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The eye's and the ear's proof on a free head (the own-content proof, 2026-11-10; Q-BASE-4's option B on trial, not in
the product): ICT-FaceKit's neutral head (MIT - USC ICT's light-stage model: a real lid margin with a fold, a deep
concha with the canal) put on our man's head shape, worn with our own skin, eyes and grooms, rendered beside HD Aaron.
Our hm08 head's lid ledge and shallow concha are its topology (the working doc, 11-09 / 11-10); this asks whether a
head with the right topology, under our content, reaches him at the eye and the ear.

The placing, CPU (the scan route's tools - Amberg's NICP in trimesh, as `smile_transfer.carry`): ICT's skin (face,
head and neck - vertices 0-11247, polygons 0-11143 by its README's index table) aligned to our head by the two eyes'
openings and a scaled ICP of its face, wrapped onto our head's skin with the eye rims as landmarks; then only the
wrap's SMOOTHED move is kept (`SMOOTH_MM`): our head's broad shape, ICT's own lids and ears - a full wrap would press
its fold and its pit onto our surface. Last, each lid region is shifted as a whole (a falloff of `RIM_MM`) so ICT's
eye openings sit on our lids' rims, where our eyeballs are.

    1. python tools/dev.py blender -b --python tools/gate/smile_transfer.py -- export OURS.npz
    2. .dev/venv-tools/Scripts/python -I tools/gate/ict_head.py OURS.npz ICT_DIR HEAD.npz
    3. python tools/dev.py blender -b --python tools/gate/factors.py -- --factors icthead*HEAD ... (HEAD under
       .dev/gate/ict/)
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import smile_transfer as st  # noqa: E402

ICT_SKIN_VERTICES, ICT_SKIN_POLYGONS = 11248, 11144  # its face and its head-and-neck (README's index table)
SMOOTH_MM = 15.0  # the wrap's move kept above this scale: our head's shape, ICT's lids and ears
RIM_MM = 8.0  # each lid region's shift onto our rims fades over this (head1)
#: head2 (2026-11-10 09:1x - head1's eye view: a gap under the lower lid, the brow half under ICT's brow ridge): the
#: FULL wrap everywhere (our brows, scalp and stubble sit on it), ICT's own (smoothed-wrap) shape only near the eyes and
#: the ears - full within the first distance, none past the second (mm); then every eye-opening vertex snapped to our
#: rim, the snap fading over SNAP_MM
EYE_KEEP_MM, EAR_KEEP_MM = (6.0, 14.0), (32.0, 48.0)
EAR_CENTRE = (0.083, -0.01, 0.015)  # ICT's own coordinates (x to each side): its widest point at eye height
SNAP_MM = 6.0
#: head3 (09:2x - head2's clay: our ledge gone, but ICT's upper-lid crease flattened by the snap onto our narrower
#: opening): ICT's lids kept whole - a wider keep zone, NO snap - and ICT's own eyeballs' centres written out, so our
#: eyeballs move into ICT's sockets (`factors icthead`) instead of ICT's lids onto ours
EYE_KEEP_WIDE_MM = (10.0, 22.0)
#: head6 (12:4x - head5 with our skin: half the brow under ICT's brow ridge, which the 10-22 mm keep kept): ICT's lids
#: whole to 8 mm, gone by 15 - the crease (CREASE_UP_MM 7 above the margin) inside, the brow (~15-25 mm) on our surface
EYE_KEEP_LID_MM = (8.0, 15.0)
ICT_EYEBALLS = ((21451, 22221), (23021, 23791))
#: the upper lid's crease (head4, 09:3x - head3's clay: ICT's generic neutral face has a weak crease where HD Aaron's is
#: deep; CC5 ships crease morphs - a shape control, not content): a groove CREASE_UP_MM above the upper lid's margin
#: following its curve, CREASE_WIDTH_MM wide (a Gaussian), its depth given in mm, pressed in along the skin's normal
CREASE_UP_MM, CREASE_WIDTH_MM = 7.0, 2.2  # its two eyeballs' first shells (README's index table): x > 0, x < 0


def _neighbour_mean(n: int, tris: np.ndarray):
    import scipy.sparse as sp

    e = np.vstack([tris[:, [0, 1]], tris[:, [1, 2]], tris[:, [2, 0]]])
    adj = sp.coo_matrix((np.ones(len(e) * 2), (np.r_[e[:, 0], e[:, 1]], np.r_[e[:, 1], e[:, 0]])), shape=(n, n)).tocsr()
    adj.data[:] = 1.0
    deg = np.asarray(adj.sum(1)).ravel()
    return sp.diags(1.0 / np.maximum(deg, 1)) @ adj


def smoothed(d: np.ndarray, verts: np.ndarray, tris: np.ndarray, scale_mm: float) -> np.ndarray:
    """`d` (per vertex) diffused over the mesh to about `scale_mm`: neighbour averaging, as many passes as the mesh's
    mean edge needs (a diffusion's spread grows with the square root of its passes)."""
    edge = float(np.linalg.norm(verts[tris[:, 0]] - verts[tris[:, 1]], axis=1).mean())
    passes = int(np.clip((scale_mm / 1000.0 / max(edge, 1e-6)) ** 2, 1, 4000))
    mean = _neighbour_mean(len(verts), tris)
    out = d.copy()
    for _ in range(passes):
        out = 0.5 * out + 0.5 * (mean @ out)
    return out


def rim_shift(verts: np.ndarray, rims: list[tuple[np.ndarray, np.ndarray]], fade_mm: float) -> np.ndarray:
    """Each eye's region moved as a whole by its rim landmarks' mean miss (their targets - where they are), fading out
    over `fade_mm` from the rim - the lid's own shape kept."""
    out = verts.copy()
    for idx, target in rims:
        miss = (target - verts[idx]).mean(0)
        dist = np.min(np.linalg.norm(verts[:, None, :] - verts[idx][None, :, :], axis=2), axis=1)
        w = np.clip(1.0 - dist / (fade_mm / 1000.0), 0.0, 1.0)
        out += w[:, None] * miss
    return out


def _crease(verts: np.ndarray, tri: np.ndarray, eyes: list[np.ndarray], depth_mm: float) -> np.ndarray:
    """Each upper lid's crease pressed in: the eye opening's upper edge lifted CREASE_UP_MM along the face's up (z),
    put on the skin (each point to its nearest skin vertex in front of the eye), smoothed and resampled densely (a
    smooth arc - the first cut's raw points drew a ragged, fraying fold), its depth tapering to nothing at both ends;
    every skin vertex moved in along its normal by depth(t) x exp(-(d / width)^2), d and t at its nearest arc point."""
    import trimesh
    from scipy.interpolate import splev, splprep

    normals = trimesh.Trimesh(verts, tri, process=False).vertex_normals
    out = verts.copy()
    for loop in eyes:
        pts = verts[loop]
        upper = pts[pts[:, 2] > pts[:, 2].mean() + 0.0005]
        upper = upper[np.argsort(upper[:, 0])]
        line = upper + np.array([0.0, 0.0, CREASE_UP_MM / 1000.0])
        front = verts[:, 1] < pts[:, 1].mean() + 0.004
        cand = np.where(front)[0]
        line = verts[cand[np.argmin(np.linalg.norm(verts[cand][None, :, :] - line[:, None, :], axis=2), axis=1)]]
        keep = np.r_[True, np.linalg.norm(np.diff(line, axis=0), axis=1) > 1e-5]  # repeats out (two points, one vertex)
        _, first = np.unique(np.round(line[keep], 6), axis=0, return_index=True)
        line = line[keep][np.sort(first)]
        tck, _u = splprep(line.T, s=len(line) * (0.0012 ** 2), k=3)  # a smoothing spline: ~1.2 mm of scatter taken out
        t = np.linspace(0.0, 1.0, 200)
        arc = np.array(splev(t, tck)).T
        taper = np.sin(np.pi * t) ** 0.6  # nothing at the ends, full in the middle
        dist = np.linalg.norm(verts[:, None, :] - arc[None, :, :], axis=2)
        k = np.argmin(dist, axis=1)
        d = dist[np.arange(len(verts)), k]
        w = np.exp(-((d * 1000.0 / CREASE_WIDTH_MM) ** 2)) * taper[k]
        w[d > 0.012] = 0.0
        out -= normals * (w * depth_mm / 1000.0)[:, None]
        print(f"CREASE: {int((w > 0.1).sum())} vertices pressed, depth {depth_mm} mm, arc from {len(line)} points", flush=True)
    return out


def place(ours_npz: Path, ict_dir: Path, out: Path, keep_lids: bool = False, crease_mm: float = 0.0,
          keep_mm: tuple | None = None) -> None:
    import trimesh
    from trimesh import registration

    o = np.load(ours_npz)
    co, tris = o["co"], o["tris"]
    rows = o["rows"]
    ict, polys = st._obj(ict_dir / "generic_neutral_mesh.obj")
    skin_polys = polys[:ICT_SKIN_POLYGONS]
    ict = ict[:ICT_SKIN_VERTICES]
    tri = np.array([[f[0], f[k], f[k + 1]] for f in skin_polys for k in range(1, len(f) - 1)])
    face_v = np.arange(st.ICT_FACE_VERTICES)
    top = co[:, 2].max()
    head = co[:, 2] > top - 0.30
    target = trimesh.Trimesh(co, tris[head[tris].all(1)], process=False)
    face_t = np.array([[f[0], f[k], f[k + 1]] for f in polys[:st.ICT_FACE_POLYGONS] for k in range(1, len(f) - 1)])
    loops = sorted(st._boundary_loops(face_t), key=len)
    ict_eyes = sorted((lp for lp in loops if abs(ict[lp, 0].mean()) > 0.02 and len(lp) < 80), key=lambda lp: ict[lp, 0].mean())
    rim = rows[:, 2][rows[:, 2] >= 0]
    our_eyes = sorted((rim[co[rim, 0] < 0], rim[co[rim, 0] > 0]), key=lambda r: co[r, 0].mean())
    if len(ict_eyes) != 2:
        raise SystemExit(f"ICT's face: {len(ict_eyes)} eye openings found, not 2")
    src, dst = [], []
    for le, ours_rim in zip(ict_eyes, our_eyes, strict=True):
        src.append(le[st._round(ict[le], ict[le].mean(0), st.EYE_POINTS)])
        dst.append(co[ours_rim[st._round(co[ours_rim], co[ours_rim].mean(0), st.EYE_POINTS)]])
    src_lm, dst_pts = np.concatenate(src), np.concatenate(dst)
    start = st._similarity(ict[src_lm], dst_pts)
    matrix, _, cost = registration.icp(ict[face_v], target, initial=start, threshold=1e-7, max_iterations=60,
                                       reflection=False, scale=True)  # fmt: skip
    placed = st._apply(matrix, ict)
    print(f"ALIGNED: ICP mean {cost * 1000:.2f} mm, scale {np.cbrt(np.linalg.det(matrix[:3, :3])):.3f}", flush=True)
    source = trimesh.Trimesh(placed, tri, process=False)
    wrapped = registration.nricp_amberg(source, target, source_landmarks=src_lm, target_positions=dst_pts,
                                        steps=st.WRAP_STEPS, distance_threshold=0.02, use_faces=True,
                                        use_vertex_normals=True)  # fmt: skip
    move = smoothed(wrapped - placed, placed, tri, SMOOTH_MM)
    soft = placed + move
    eye_loop = np.concatenate(ict_eyes)
    d_eye = np.min(np.linalg.norm(placed[:, None, :] - placed[eye_loop][None, :, :], axis=2), axis=1) * 1000
    centres = st._apply(matrix, np.array([[sx * EAR_CENTRE[0], EAR_CENTRE[1], EAR_CENTRE[2]] for sx in (-1, 1)]))
    d_ear = np.min(np.linalg.norm(placed[:, None, :] - centres[None, :, :], axis=2), axis=1) * 1000

    def ramp(d, lo_hi):
        t = np.clip((d - lo_hi[0]) / (lo_hi[1] - lo_hi[0]), 0.0, 1.0)
        return t * t * (3 - 2 * t)

    keep = keep_mm or (EYE_KEEP_WIDE_MM if keep_lids else EYE_KEEP_MM)
    w = np.minimum(ramp(d_eye, keep), ramp(d_ear, EAR_KEEP_MM))[:, None]
    head_v = soft + w * (wrapped - soft)
    # every eye-opening vertex onto our rim (its nearest point on our rim's edges), spread over SNAP_MM
    rim_set = set(rim.tolist())
    edges = {tuple(sorted(e)) for t in tris for e in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0]))
             if e[0] in rim_set and e[1] in rim_set}  # fmt: skip
    seg = np.array([[co[a], co[b]] for a, b in edges])
    pos = head_v[eye_loop]
    ab = seg[:, 1] - seg[:, 0]
    t = np.clip(np.einsum("pk,sk->ps", pos, ab) - np.einsum("sk,sk->s", seg[:, 0], ab)[None, :], 0, None)
    t = np.clip(t / np.maximum(np.einsum("sk,sk->s", ab, ab), 1e-12)[None, :], 0.0, 1.0)
    near = seg[None, :, 0, :] + t[..., None] * ab[None, :, :]
    k = np.argmin(np.linalg.norm(near - pos[:, None, :], axis=2), axis=1)
    snap = near[np.arange(len(pos)), k] - pos
    d = np.linalg.norm(head_v[:, None, :] - pos[None, :, :], axis=2)
    g = np.exp(-((d / 0.0015) ** 2))
    spread = (g @ snap) / np.maximum(g.sum(1, keepdims=True), 1e-9)
    fade = np.clip(1.0 - d.min(1) / (SNAP_MM / 1000.0), 0.0, 1.0)[:, None]
    if not keep_lids:
        head_v = head_v + spread * fade * fade * (3 - 2 * fade)
    print(f"SNAPPED: {len(eye_loop)} eye-opening vertices, before p50 {np.median(np.linalg.norm(snap, axis=1)) * 1000:.2f} / "
          f"max {np.linalg.norm(snap, axis=1).max() * 1000:.2f} mm; kept ICT's shape on {int((w[:, 0] < 0.5).sum())} vertices", flush=True)
    if crease_mm > 0:
        head_v = _crease(head_v, tri, ict_eyes, crease_mm)
    gap = trimesh.proximity.closest_point(target, head_v)[1]
    rim_off = np.linalg.norm(head_v[src_lm] - dst_pts, axis=1)  # against the 24 sampled landmarks (the snap goes to the rim's edges)
    print(f"PLACED: off our skin p50 {np.median(gap) * 1000:.2f} / p90 {np.percentile(gap, 90) * 1000:.2f} mm; eye rims off "
          f"{rim_off.mean() * 1000:.2f} mm (max {rim_off.max() * 1000:.2f})", flush=True)
    counts = np.array([len(f) for f in skin_polys])
    flat = np.concatenate([np.asarray(f) for f in skin_polys])
    out.parent.mkdir(parents=True, exist_ok=True)
    full, _ = st._obj(ict_dir / "generic_neutral_mesh.obj")
    eyes = []
    for a, b in ICT_EYEBALLS:  # each eyeball's centre placed as ICT's skin round it was: the matrix, then its lid's move
        centre = st._apply(matrix, full[a:b].mean(0)[None])[0]
        side = eye_loop[np.sign(placed[eye_loop, 0]) == np.sign(centre[0])]
        eyes.append(centre + (head_v[side] - placed[side]).mean(0))
    np.savez(out, verts=head_v.astype(np.float32), counts=counts, flat=flat, eyes=np.array(eyes, np.float32),
             world=o["world"] if "world" in o.files else np.eye(4))  # fmt: skip
    print("ICT EYEBALL CENTRES (cm):", np.round(np.array(eyes) * 100, 2).tolist(), flush=True)
    print("WRITTEN", out, len(head_v), "vertices", len(counts), "polygons", flush=True)


if __name__ == "__main__":
    a = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    crease = float(a[a.index("--crease") + 1]) if "--crease" in a else 0.0
    keep = EYE_KEEP_LID_MM if "--lid-keep" in a else None
    place(Path(a[0]), Path(a[1]), Path(a[2]), keep_lids="--keep-lids" in a, crease_mm=crease, keep_mm=keep)

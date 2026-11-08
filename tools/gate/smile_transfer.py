# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The smile proof's feasibility test (plan §0, §7 "Expression shapes": ICT 53 one of the candidate sets; the user,
2026-11-07: "determine if you can meet quality"): ICT-FaceKit's smile (MIT, light-stage scanned, ARKit-named -
`mouthSmile_L/R`, `cheekSquint_L/R`, `eyeSquint_L/R`) carried onto our character's head and rendered beside HD
Aaron's smile - does an open, scanned smile reach CC5's on our head?

The carry, the way a shape moves between two meshes (Blender's Surface Deform binds the same way): ICT's face aligned
to our head (a similarity from the two eyes' openings, then a scaled ICP), wrapped onto our head's skin (Amberg's
NICP, trimesh - the scan route's wrap, `tools/body_scan.py`), each eye's opening held to our lid's rim (`base.rows`)
as landmarks; then each of our head's skin vertices takes the shape's offset at its nearest point on the wrapped ICT
face (its triangle's barycentric mix), full within 2 mm, none past 6 mm, and the rest of the head - the eye sockets
and the mouth's inside, which ICT's face leaves open - filled harmonically from around them (a Laplace solve, the
far head held at 0).

    1. python tools/dev.py blender -b --python tools/gate/smile_transfer.py -- export OURS.npz
       (the gate's man, `parts_gate.OURS`: his skin's shaped vertices, triangles, lid rims)
    2. .dev/venv-tools/Scripts/python -I tools/gate/smile_transfer.py carry OURS.npz ICT_DIR DELTAS.npz [SHAPE,SHAPE]
    3. python tools/dev.py blender -b --python tools/gate/factors.py -- --factors ictsmile*DELTAS --alone
       --views face_smile,face_smile_full (the deltas written into our ARKit keys of the same names)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
#: ICT's shapes carried, by ICT's file names (its ARKit names with _L / _R)
SHAPES = ("mouthSmile_L", "mouthSmile_R", "cheekSquint_L", "cheekSquint_R", "eyeSquint_L", "eyeSquint_R")
#: ICT's README index table (as `modules/head/eye_layers.py` reads it): its face's vertices and polygons
ICT_FACE_VERTICES, ICT_FACE_POLYGONS = 9409, 9230
FULL_MM, NONE_MM = 2.0, 6.0  # the carry's falloff off the wrapped face
EYE_POINTS = 24  # landmarks round each eye's opening
WRAP_STEPS = [[0.02, 50, 0.5, 10], [0.02, 20, 0.5, 10], [0.02, 8, 0.5, 10], [0.02, 4, 0.5, 10]]  # body_scan's


def export(out: Path, character: str = "") -> None:
    """The gate's man as `parts_gate.build_ours` starts him (the library's character, his eyes opened): his skin's
    shaped vertices (world), its triangles and his lids' rims - no hair, no render. `character`: another library
    character (the gate's `--character`) - the transplants on the women (checklist row 19)."""
    import importlib
    import importlib.util

    import bpy

    spec = importlib.util.spec_from_file_location("pg", Path(__file__).resolve().parent / "parts_gate.py")
    pg = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pg)
    api = importlib.import_module("bl_ext.system.juststage.api")
    library = importlib.import_module("bl_ext.system.juststage.core.library")
    makehuman = importlib.import_module("bl_ext.system.juststage.core.makehuman")
    build = importlib.import_module("bl_ext.system.juststage.modules.body.build")
    base = importlib.import_module("bl_ext.system.juststage.modules.body.base")
    create = importlib.import_module("bl_ext.system.juststage.modules.body.body_create")
    scene, _ = pg._stage()
    name = character or pg.OURS["character"]
    shown = api.run("juststage.library.add", path=str(library.root() / "Characters" / f"{name}.blend"))
    create.open_eyes(shown.character)
    body = next(o for o in scene.objects if o.juststage.character_id == shown.character and not o.juststage.part_of)
    co = build.shaped_coords(body)
    mw = np.array(body.matrix_world)
    skin = makehuman.skin_mask(len(co))
    tris = [[p.vertices[0], p.vertices[k], p.vertices[k + 1]] for p in body.data.polygons if skin[list(p.vertices)].all()
            for k in range(1, len(p.vertices) - 1)]  # fmt: skip
    out.parent.mkdir(parents=True, exist_ok=True)
    np.savez(out, co=co @ mw[:3, :3].T + mw[:3, 3], tris=np.array(tris, np.int64), rows=base.rows(), world=mw,
             character=name)  # fmt: skip
    print("EXPORTED", len(co), "vertices", len(tris), "skin triangles", flush=True)


def _obj(path: Path) -> tuple[np.ndarray, list[list[int]]]:
    """An OBJ's positions in Blender's axes and metres (ICT's are y up, z forward, centimetres - eye_layers._ict) and
    its polygons."""
    v, faces = [], []
    for line in path.read_text().splitlines():
        if line.startswith("v "):
            v.append([float(x) for x in line.split()[1:4]])
        elif line.startswith("f "):
            faces.append([int(t.split("/")[0]) - 1 for t in line.split()[1:]])
    v = np.array(v)
    return np.c_[v[:, 0], -v[:, 2], v[:, 1]] * 0.01, faces


def _boundary_loops(tris: np.ndarray) -> list[np.ndarray]:
    e = np.sort(np.vstack([tris[:, [0, 1]], tris[:, [1, 2]], tris[:, [2, 0]]]), axis=1)
    u, c = np.unique(e, axis=0, return_counts=True)
    nbr: dict[int, list[int]] = {}
    for a, b in u[c == 1]:
        nbr.setdefault(int(a), []).append(int(b))
        nbr.setdefault(int(b), []).append(int(a))
    seen, loops = set(), []
    for start in nbr:
        if start in seen:
            continue
        loop, prev, cur = [start], -1, start
        seen.add(start)
        while True:
            nxt = [n for n in nbr[cur] if n != prev and n not in seen]
            if not nxt:
                break
            prev, cur = cur, nxt[0]
            seen.add(cur)
            loop.append(cur)
        loops.append(np.array(loop))
    return loops


def _round(points: np.ndarray, centre: np.ndarray, count: int) -> np.ndarray:
    """Indices into `points` nearest each of `count` even angles about `centre` in the face's plane (x, z)."""
    ang = np.arctan2(points[:, 2] - centre[2], points[:, 0] - centre[0])
    want = np.linspace(-np.pi, np.pi, count, endpoint=False)
    return np.array([int(np.argmin(np.abs(np.angle(np.exp(1j * (ang - w)))))) for w in want])


def _similarity(src: np.ndarray, dst: np.ndarray) -> np.ndarray:
    """Umeyama's similarity (rotation, one scale, translation) taking src's points onto dst's, as a 4x4."""
    ms, md = src.mean(0), dst.mean(0)
    a, b = src - ms, dst - md
    u, s, vt = np.linalg.svd(b.T @ a / len(src))
    d = np.diag([1.0, 1.0, np.sign(np.linalg.det(u @ vt))])
    r = u @ d @ vt
    scale = np.trace(np.diag(s) @ d) / (a**2).sum(1).mean()
    m = np.eye(4)
    m[:3, :3], m[:3, 3] = scale * r, md - scale * r @ ms
    return m


def _apply(m: np.ndarray, p: np.ndarray) -> np.ndarray:
    return p @ m[:3, :3].T + m[:3, 3]


def carry(ours_npz: Path, ict_dir: Path, out: Path, shapes: tuple = SHAPES) -> None:
    import scipy.sparse as sp
    import trimesh
    from scipy.sparse.linalg import spsolve
    from trimesh import registration

    o = np.load(ours_npz)
    co, tris = o["co"], o["tris"]
    rows = o["rows"] if "rows" in o.files else np.array(json.loads(
        (ROOT / "extension/juststage/data/generated/base/v2.json").read_text(encoding="utf-8"))["rows"])  # fmt: skip
    ict, polys = _obj(ict_dir / "generic_neutral_mesh.obj")
    face_v = np.arange(ICT_FACE_VERTICES)
    face_t = np.array([[f[0], f[k], f[k + 1]] for f in polys[:ICT_FACE_POLYGONS] for k in range(1, len(f) - 1)])
    # our head's skin (above the neck): the target
    top = co[:, 2].max()
    head = co[:, 2] > top - 0.30
    head_t = tris[head[tris].all(1)]
    target = trimesh.Trimesh(co, head_t, process=False)
    # the eyes' openings: ICT's two small loops beside the nose against our lids' rims (base.rows' third column)
    loops = sorted(_boundary_loops(face_t), key=len)
    ict_eyes = sorted((lp for lp in loops if abs(ict[lp, 0].mean()) > 0.02 and len(lp) < 80), key=lambda lp: ict[lp, 0].mean())
    rim = rows[:, 2][rows[:, 2] >= 0]
    our_eyes = sorted((rim[co[rim, 0] < 0], rim[co[rim, 0] > 0]), key=lambda r: co[r, 0].mean())
    if len(ict_eyes) != 2:
        raise SystemExit(f"ICT's face: {len(ict_eyes)} eye openings found, not 2")
    src_lm, dst_pts = [], []
    for le, ours_rim in zip(ict_eyes, our_eyes, strict=True):
        pick_ict = le[_round(ict[le], ict[le].mean(0), EYE_POINTS)]
        pick_ours = ours_rim[_round(co[ours_rim], co[ours_rim].mean(0), EYE_POINTS)]
        src_lm.append(pick_ict)
        dst_pts.append(co[pick_ours])
    src_lm, dst_pts = np.concatenate(src_lm), np.concatenate(dst_pts)
    # align: the similarity of the eye landmarks, then a scaled ICP of ICT's face onto our head
    start = _similarity(ict[src_lm], dst_pts)
    matrix, _, cost = registration.icp(ict[face_v], target, initial=start, threshold=1e-7, max_iterations=60,
                                       reflection=False, scale=True)  # fmt: skip
    scale = float(np.cbrt(np.linalg.det(matrix[:3, :3])))
    lin = matrix[:3, :3]
    placed = _apply(matrix, ict[face_v])
    print(f"ALIGNED: ICP mean {cost * 1000:.2f} mm, scale {scale:.3f}; eye landmarks off by "
          f"{np.linalg.norm(_apply(matrix, ict[src_lm]) - dst_pts, axis=1).mean() * 1000:.2f} mm", flush=True)
    source = trimesh.Trimesh(placed, face_t, process=False)
    wrapped = registration.nricp_amberg(source, target, source_landmarks=src_lm, target_positions=dst_pts,
                                        steps=WRAP_STEPS, distance_threshold=0.01, use_faces=True,
                                        use_vertex_normals=True)  # fmt: skip
    gap = trimesh.proximity.closest_point(target, wrapped)[1]
    lm_off = np.linalg.norm(wrapped[src_lm] - dst_pts, axis=1)
    print(f"WRAPPED: to our skin p50 {np.median(gap) * 1000:.2f} / p90 {np.percentile(gap, 90) * 1000:.2f} mm; moved "
          f"p50 {np.median(np.linalg.norm(wrapped - placed, axis=1)) * 1000:.1f} mm; eye landmarks off "
          f"{lm_off.mean() * 1000:.2f} mm", flush=True)
    # ICT's mouth corners where they land on us (its mouth opening's sideways ends), for the record
    mouth = next(lp for lp in loops if abs(ict[lp, 0].mean()) < 0.005 and len(lp) < 150)
    corners = wrapped[mouth[[np.argmin(wrapped[mouth, 0]), np.argmax(wrapped[mouth, 0])]]]
    # the carry: each head vertex's nearest point on the wrapped face, its barycentric mix
    wrapped_mesh = trimesh.Trimesh(wrapped, face_t, process=False)
    hv = np.unique(head_t)
    closest, dist, tri = trimesh.proximity.closest_point(wrapped_mesh, co[hv])
    bary = trimesh.triangles.points_to_barycentric(wrapped[face_t[tri]], closest)
    weight = np.clip((NONE_MM / 1000 - dist) / ((NONE_MM - FULL_MM) / 1000), 0.0, 1.0)
    # the harmonic fill's system over our head's skin: unknown where the carry is partial or absent (and near the
    # face - within 4 cm of it), held elsewhere (the carried value, or 0 far away)
    n = len(co)
    e = np.vstack([head_t[:, [0, 1]], head_t[:, [1, 2]], head_t[:, [2, 0]]])
    adj = sp.coo_matrix((np.ones(len(e) * 2), (np.r_[e[:, 0], e[:, 1]], np.r_[e[:, 1], e[:, 0]])), shape=(n, n)).tocsr()
    adj.data[:] = 1.0
    lap = sp.diags(np.asarray(adj.sum(1)).ravel()) - adj
    free = np.zeros(n, bool)
    free[hv[(weight < 1.0) & (dist < 0.04)]] = True
    fixed = ~free
    lap_ff = lap[free][:, free].tocsc()
    lap_fx = lap[free][:, fixed]
    deltas = {}
    for name in shapes:
        shaped, _ = _obj(ict_dir / f"{name}.obj")
        d_ict = (shaped[face_v] - ict[face_v]) @ lin.T  # ICT's offset in our frame and scale
        d = np.zeros((n, 3))
        d[hv] = np.einsum("nk,nkj->nj", bary, d_ict[face_t[tri]]) * weight[:, None]
        d[free] = spsolve(lap_ff, -lap_fx @ d[fixed]).reshape(-1, 3) if free.any() else d[free]
        deltas[name] = d.astype(np.float32)
        size = np.linalg.norm(d, axis=1)
        side = float((co[:, 0] * size).sum() / max(size.sum(), 1e-12))  # where it moves: the moved skin's mean x
        print(f"CARRIED {name}: max {size.max() * 1000:.1f} mm (ICT's own {np.linalg.norm(d_ict, axis=1).max() * 1000:.1f}"
              f" scaled), {int((size > 0.0005).sum())} vertices over 0.5 mm, its side x {side * 100:+.2f} cm", flush=True)
    out.parent.mkdir(parents=True, exist_ok=True)
    np.savez(out, **deltas, world=o["world"] if "world" in o.files else np.eye(4), corners=corners,
             landmarks_off_mm=lm_off * 1000, scale=scale)  # fmt: skip
    print("WRITTEN", out, "; ICT's mouth corners on us (cm):", np.round(corners * 100, 2).tolist(), flush=True)


if __name__ == "__main__":
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    if args[0] == "export":  # export OUT.npz [CHARACTER]
        export(Path(args[1]), args[2] if len(args) > 2 else "")
    else:
        carry(Path(args[1]), Path(args[2]), Path(args[3]), tuple(args[4].split(",")) if len(args) > 4 else SHAPES)

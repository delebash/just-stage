# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The scalp hair's feasibility test (plan §0, §14 "Grooms"): an authored groom on our head, rendered with our own
fill, shape and shading against HD Aaron's hair - does our render reach his once the cut is right? Our procedural comb
gave a helmet after five taper versions (the gate's hair views, 2026-11-07), the second-workaround mark; the leading
apps ship artist-made grooms. USC-HairSalon (343 styles, 10,000 strands each, on one standard head; its terms:
"internal, non-commercial research, evaluation or testing purposes only", no distribution) is a LOCAL TEST ONLY
(AGENTS.md) - nothing of it ships.

The carry, as `smile_transfer.py` moves a face: their head aligned to ours (a scaled ICP on the skull), wrapped onto
our head's skin (Amberg's NICP, trimesh); each strand point then moves as its nearest head vertices moved (inverse
distance over 4), so a strand keeps its stand-off and its flow on our skull.

    .dev/venv-tools/Scripts/python -I tools/gate/groom_transfer.py usc OURS.npz hairstyles.zip ID OUT.npz
    .dev/venv-tools/Scripts/python -I tools/gate/groom_transfer.py cards OURS.npz SOURCE.npz OUT.npz
       (OURS.npz: smile_transfer.py's export; SOURCE.npz: HD Aaron's body and hair cards exported from his gate .blend;
       OUT.npz: strands (points x 3, world) and their counts)
    then: factors.py --factors guidefile*<OUT stem> --alone (the strands as our scalp's guides)

The second source, HD Aaron's own cut (his "Classic_Slick_Back", 1,970 cards), turns each card into three strands
(`card_strands`) - the same test on exactly his cut, LOCAL TEST ONLY as well.
"""

from __future__ import annotations

import importlib.util
import sys
import zipfile
from pathlib import Path

import numpy as np

spec = importlib.util.spec_from_file_location("smile_transfer", Path(__file__).resolve().parent / "smile_transfer.py")
st = importlib.util.module_from_spec(spec)
spec.loader.exec_module(st)

WRAP_STEPS = st.WRAP_STEPS
NEAREST = 4


def read_style(archive: Path, style: str) -> list[np.ndarray]:
    """One USC-HairSalon style's strands (its own axes and units), the empty roots (one vertex) left out: the .data
    format - int32 strand count; per strand int32 vertex count, then float32 x, y, z per vertex."""
    with zipfile.ZipFile(archive) as z:
        b = z.read(f"hairstyles/strands{style}.data")
    count = int(np.frombuffer(b, np.int32, 1, 0)[0])
    off, out = 4, []
    for _ in range(count):
        k = int(np.frombuffer(b, np.int32, 1, off)[0])
        off += 4
        if k > 1:
            out.append(np.frombuffer(b, np.float32, 3 * k, off).reshape(k, 3).astype(np.float64))
        off += 12 * k
    return out


def read_head(archive: Path) -> tuple[np.ndarray, np.ndarray]:
    with zipfile.ZipFile(archive) as z:
        text = z.read("hairstyles/head_model.obj").decode()
    v, faces = [], []
    for line in text.splitlines():
        if line.startswith("v "):
            v.append([float(x) for x in line.split()[1:4]])
        elif line.startswith("f "):
            idx = [int(t.split("/")[0]) - 1 for t in line.split()[1:]]
            faces += [[idx[0], idx[k], idx[k + 1]] for k in range(1, len(idx) - 1)]
    return np.array(v), np.array(faces, np.int64)


def to_blender(p: np.ndarray) -> np.ndarray:
    """USC's axes (y up, the face toward +z, as ICT's) to Blender's (z up, the face toward -y); units kept."""
    return np.c_[p[:, 0], -p[:, 2], p[:, 1]]


def wrap_head(co: np.ndarray, tris: np.ndarray, hv: np.ndarray, hf: np.ndarray, landmarks=None):
    """A source head (hv, hf: Blender's axes, metres) onto our head (co, tris: our skin, world): the source's skull
    aligned to ours (the top of the head and the head's middle together, then a scaled ICP on the vertices within 10 cm
    of the top - the hair's region; the necks and faces differ), wrapped onto our skin (NICP) - `landmarks` (source
    vertex indices, our positions) pinned in the wrap. Returns the alignment, the source placed by it, the source
    wrapped and our head as a mesh."""
    import trimesh
    from trimesh import registration

    top = co[:, 2].max()
    head = co[:, 2] > top - 0.30
    target = trimesh.Trimesh(co, tris[head[tris].all(1)], process=False)
    start = np.eye(4)
    start[:3, 3] = [np.median(co[head, 0]) - np.median(hv[:, 0]), np.median(co[head, 1]) - np.median(hv[:, 1]),
                    top - hv[:, 2].max()]  # fmt: skip
    upper = hv[:, 2] > hv[:, 2].max() - 0.10
    matrix, _, cost = registration.icp(hv[upper], target, initial=start, threshold=1e-7, max_iterations=80,
                                       reflection=False, scale=True)  # fmt: skip
    placed = st._apply(matrix, hv)
    print(f"ALIGNED: ICP mean {cost * 1000:.2f} mm, scale {np.cbrt(np.linalg.det(matrix[:3, :3])):.4f}", flush=True)
    pins = {} if landmarks is None else {"source_landmarks": landmarks[0], "target_positions": landmarks[1]}
    wrapped = registration.nricp_amberg(trimesh.Trimesh(placed, hf, process=False), target, steps=WRAP_STEPS,
                                        distance_threshold=0.02, use_faces=True, use_vertex_normals=True,
                                        **pins)  # fmt: skip
    if landmarks is not None:
        off = np.linalg.norm(wrapped[landmarks[0]] - landmarks[1], axis=1)
        print(f"PINS: {len(off)} eye-rim landmarks off {np.median(off) * 1000:.2f} / {off.max() * 1000:.2f} mm", flush=True)
    gap = trimesh.proximity.closest_point(target, wrapped)[1]
    print(f"WRAPPED: to our skin p50 {np.median(gap) * 1000:.2f} / p90 {np.percentile(gap, 90) * 1000:.2f} mm; moved "
          f"p50 {np.median(np.linalg.norm(wrapped - placed, axis=1)) * 1000:.1f} mm", flush=True)
    return matrix, placed, wrapped, target


def carry_strands(co: np.ndarray, tris: np.ndarray, hv: np.ndarray, hf: np.ndarray, strands: list[np.ndarray],
                  out: Path, label: str) -> None:
    """Strands grown on a source head moved onto our head (`wrap_head`): every strand point moved as its NEAREST source
    vertices moved (inverse distance)."""
    import trimesh
    from scipy.spatial import cKDTree

    matrix, placed, wrapped, target = wrap_head(co, tris, hv, hf)
    move = wrapped - placed
    pts = st._apply(matrix, np.concatenate(strands))
    dist, idx = cKDTree(placed).query(pts, NEAREST)
    w = 1.0 / np.maximum(dist, 1e-6)
    pts = pts + np.einsum("nk,nkj->nj", w / w.sum(1, keepdims=True), move[idx])
    counts = np.array([len(x) for x in strands])
    roots = pts[np.r_[0, np.cumsum(counts)[:-1]]]
    root_gap = trimesh.proximity.closest_point(target, roots)[1]
    print(f"STRANDS: {len(strands)}, {len(pts)} points; roots off our skin p50 {np.median(root_gap) * 1000:.2f} / p90 "
          f"{np.percentile(root_gap, 90) * 1000:.2f} mm", flush=True)
    out.parent.mkdir(parents=True, exist_ok=True)
    np.savez(out, points=pts.astype(np.float32), counts=counts, source=label)
    print("WRITTEN", out, flush=True)


def head_region(co: np.ndarray, tris: np.ndarray, depth: float = 0.30) -> tuple[np.ndarray, np.ndarray]:
    """A body's vertices within `depth` of its top and the triangles among them, renumbered."""
    keep = co[:, 2] > co[:, 2].max() - depth
    new = -np.ones(len(co), np.int64)
    new[keep] = np.arange(int(keep.sum()))
    t = tris[keep[tris].all(1)]
    return co[keep], new[t]


def eye_pins(hv: np.ndarray, eyes_npz: Path, co: np.ndarray, rows: np.ndarray, count: int = 24):
    """The eye openings as wrap landmarks: his lid rims (his head skin within 1.5 mm outside his eyeball's sphere, in
    front of it) against ours (base v2's rim row), `count` points round each eye matched by angle (smile_transfer's
    `_round`)."""
    e = np.load(eyes_npz)
    rim = rows[:, 2][rows[:, 2] >= 0]
    src, dst = [], []
    for side in ("L", "R"):
        c, r = e[f"{side}_c"], float(e[f"{side}_r"])
        off = np.linalg.norm(hv - c, axis=1) - r
        his = np.flatnonzero((off > -0.0005) & (off < 0.0015) & (hv[:, 1] < c[1] - 0.6 * r))
        ours = rim[np.sign(co[rim, 0]) == np.sign(c[0])]
        src.append(his[st._round(hv[his], hv[his].mean(0), count)])
        dst.append(co[ours[st._round(co[ours], co[ours].mean(0), count)]])
    return np.concatenate(src), np.concatenate(dst)


def carry_skin(ours_npz: Path, source_npz: Path, out: Path, eyes_npz: Path | None = None) -> None:
    """HD Aaron's head skin onto our head (a LOCAL TEST - the transplant: does our head, rendered our way, reach his
    look in his own skin?): his head wrapped onto ours (`wrap_head`), kept with his head material's triangles and their
    corner UVs, for `factors aaronskin` to read his UV at each of our face corners."""
    o, s = np.load(ours_npz), np.load(source_npz)
    keep = s["co"][:, 2] > s["co"][:, 2].max() - 0.30
    tri_keep = keep[s["tris"]].all(1)
    hv, hf = head_region(s["co"], s["tris"])
    pins = eye_pins(hv, eyes_npz, o["co"], o["rows"]) if eyes_npz is not None else None
    _, placed, wrapped, _ = wrap_head(o["co"], o["tris"], hv, hf, pins)
    head_mat = tri_keep.nonzero()[0][s["tmat"][tri_keep] == 0]  # his Std_Skin_Head's triangles in the head region
    rows = np.searchsorted(tri_keep.nonzero()[0], head_mat)
    out.parent.mkdir(parents=True, exist_ok=True)
    np.savez(out, co=wrapped.astype(np.float32), tris=hf[rows], tuv=s["tuv"][head_mat], uv_name=s["uv_name"],
             placed=placed.astype(np.float32), all_tris=hf)  # his own shape, aligned to ours (`factors aaronshape`)
    print(f"SKIN: {len(rows)} of his head triangles on our head -> {out}", flush=True)


def card_strands(co: np.ndarray, tris: np.ndarray, uv: np.ndarray, scalp: np.ndarray) -> list[np.ndarray]:
    """Hair cards (strips textured with strands along the texture's v) as strands: each card's vertices in rows of one
    v; per row its middle and its two ends across (u) - three strands a card, each from the end nearest the scalp
    (`scalp`: the head's vertices) to the tip."""
    import scipy.sparse as sp
    from scipy.sparse.csgraph import connected_components
    from scipy.spatial import cKDTree

    n = len(co)
    e = np.vstack([tris[:, [0, 1]], tris[:, [1, 2]], tris[:, [2, 0]]])
    _, label = connected_components(sp.coo_matrix((np.ones(len(e)), (e[:, 0], e[:, 1])), shape=(n, n)), directed=False)
    tree = cKDTree(scalp)
    out = []
    for c in np.unique(label):
        i = np.flatnonzero(label == c)
        v = uv[i, 1]
        span = np.ptp(v)
        if span <= 0 or len(i) < 4:
            continue
        rows = np.round((v - v.min()) / span * 64).astype(int)  # rows of one v (cards hold a few vertices a row)
        lines = {"mid": [], "lo": [], "hi": []}
        for r in np.unique(rows):
            j = i[rows == r]
            order = j[np.argsort(uv[j, 0])]
            lines["mid"].append(co[j].mean(0))
            lines["lo"].append(co[order[0]])
            lines["hi"].append(co[order[-1]])
        for pts in lines.values():
            pts = np.array(pts)
            if len(pts) < 2:
                continue
            if tree.query(pts[-1])[0] < tree.query(pts[0])[0]:
                pts = pts[::-1]
            out.append(pts)
    return out


def carry(ours_npz: Path, archive: Path, style: str, out: Path) -> None:
    o = np.load(ours_npz)
    hv, hf = read_head(archive)
    hv = to_blender(hv)  # USC's head is in metres (its bounding box: 0.23 m wide, its top 1.89 m)
    strands = [to_blender(x) for x in read_style(archive, style)]
    carry_strands(o["co"], o["tris"], hv, hf, strands, out, f"usc {style}")


def carry_region(ours_npz: Path, source_npz: Path, out: Path, material: int, box: tuple, shift=(0.0, 0.0, 0.0),
                 anchors=None, tile: int = 1002, extra=None) -> None:
    """HD Aaron's skin on one region of our body (a LOCAL TEST, the body's transplant): his triangles of `material`
    (his slot index: 1 Std_Skin_Body, 2 Std_Skin_Arm) inside `box` ((x0, x1), (y0, y1), (z0, z1), metres, world)
    aligned onto ours in the same box (centre to centre, then a scaled ICP) and wrapped onto our skin there (NICP);
    saved as `carry_skin` saves the head's, for `factors aaronbody`. `shift` moves his body first (the two stand in
    different places: ours pupils' midpoint less his), so one box holds both; `anchors` (his points, ours) instead
    move him by the similarity between them (a hand's pose differs from ours). `tile`: our UDIM tile it covers.
    `extra` (material, tile, out): another of his materials in the box carried through this same wrap (each vertex
    moved as its nearest wrapped vertices moved) - his nails ride his fingers onto ours."""
    import trimesh
    from trimesh import registration

    o, s = np.load(ours_npz), np.load(source_npz)
    (x0, x1), (y0, y1), (z0, z1) = box

    def inside(p):
        return (p[:, 0] > x0) & (p[:, 0] < x1) & (p[:, 1] > y0) & (p[:, 1] < y1) & (p[:, 2] > z0) & (p[:, 2] < z1)

    co, tris = o["co"], o["tris"]
    ours_in = inside(co)
    target = trimesh.Trimesh(co, tris[ours_in[tris].all(1)], process=False)
    sco, stris = s["co"] + np.asarray(shift), s["tris"]
    if anchors is not None:
        sco = st._apply(st._similarity(np.asarray(anchors[0]), np.asarray(anchors[1])), s["co"])
    sel = np.flatnonzero((s["tmat"] == material) & inside(sco)[stris].all(1))
    used = np.unique(stris[sel])
    new = -np.ones(len(sco), np.int64)
    new[used] = np.arange(len(used))
    sv, sf = sco[used], new[stris[sel]]
    start = np.eye(4)
    start[:3, 3] = target.vertices[np.unique(target.faces)].mean(0) - sv.mean(0)
    matrix, _, cost = registration.icp(sv, target, initial=start, threshold=1e-7, max_iterations=80, reflection=False,
                                       scale=True)  # fmt: skip
    placed = st._apply(matrix, sv)
    print(f"ALIGNED: ICP mean {cost * 1000:.2f} mm, scale {np.cbrt(np.linalg.det(matrix[:3, :3])):.4f}", flush=True)
    wrapped = registration.nricp_amberg(trimesh.Trimesh(placed, sf, process=False), target, steps=WRAP_STEPS,
                                        distance_threshold=0.02, use_faces=True, use_vertex_normals=True)  # fmt: skip
    gap = trimesh.proximity.closest_point(target, wrapped)[1]
    print(f"WRAPPED: to our skin p50 {np.median(gap) * 1000:.2f} / p90 {np.percentile(gap, 90) * 1000:.2f} mm", flush=True)
    out.parent.mkdir(parents=True, exist_ok=True)
    np.savez(out, co=wrapped.astype(np.float32), tris=sf, tuv=s["tuv"][sel], uv_name=s["uv_name"],
             placed=placed.astype(np.float32), all_tris=sf, material=str(s["names"][material]), tile=tile)  # fmt: skip
    print(f"REGION: {len(sel)} of his {s['names'][material]} triangles -> {out}", flush=True)
    if extra is not None:
        from scipy.spatial import cKDTree

        e_mat, e_tile, e_out = extra
        e_sel = np.flatnonzero((s["tmat"] == e_mat) & inside(sco)[stris].all(1))
        e_used = np.unique(stris[e_sel])
        e_new = -np.ones(len(sco), np.int64)
        e_new[e_used] = np.arange(len(e_used))
        e_placed = st._apply(matrix, sco[e_used])
        dist, idx = cKDTree(placed).query(e_placed, NEAREST)
        w = 1.0 / np.maximum(dist, 1e-6)
        e_wrapped = e_placed + np.einsum("nk,nkj->nj", w / w.sum(1, keepdims=True), (wrapped - placed)[idx])
        gap = trimesh.proximity.closest_point(target, e_wrapped)[1]
        np.savez(e_out, co=e_wrapped.astype(np.float32), tris=e_new[stris[e_sel]], tuv=s["tuv"][e_sel],
                 uv_name=s["uv_name"], placed=e_placed.astype(np.float32), all_tris=e_new[stris[e_sel]],
                 material=str(s["names"][e_mat]), tile=e_tile)  # fmt: skip
        print(f"EXTRA: {len(e_sel)} of his {s['names'][e_mat]} triangles through the wrap; to our skin p50 "
              f"{np.median(gap) * 1000:.2f} mm -> {e_out}", flush=True)


def carry_cards(ours_npz: Path, source_npz: Path, out: Path) -> None:
    """HD Aaron's own hair cards (a gate export of his .blend - LOCAL TEST ONLY, nothing of his ships) as strands on
    our head: his cut exactly, so our strands and shading are judged on the same cut."""
    o, s = np.load(ours_npz), np.load(source_npz)
    hv, hf = head_region(s["body_co"], s["body_tris"])
    strands = card_strands(s["hair_co"], s["hair_tris"], s["hair_uv"], hv)
    print(f"CARDS: {len(strands)} strands from his cards", flush=True)
    carry_strands(o["co"], o["tris"], hv, hf, strands, out, "his cards")


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[0] == "cards":  # cards OURS.npz SOURCE.npz OUT.npz
        carry_cards(Path(a[1]), Path(a[2]), Path(a[3]))
    elif a[0] == "region":  # region OURS.npz SKIN_SOURCE.npz OUT.npz MATERIAL x0 x1 y0 y1 z0 z1
        b = [float(v) for v in a[5:11]]
        shift = [float(v) for v in a[11:14]] if len(a) >= 14 else (0.0, 0.0, 0.0)
        carry_region(Path(a[1]), Path(a[2]), Path(a[3]), int(a[4]), ((b[0], b[1]), (b[2], b[3]), (b[4], b[5])), shift)
    elif a[0] in ("hand", "nails"):  # hand|nails OURS.npz SKIN_SOURCE.npz OUT.npz OURS_ANCHORS.json HIS_ANCHORS.json
        import json  # the right hand: his arm skin (slot 2) onto our arm tile, or his nails (slot 4) onto our nail tile

        keys = ("wrist", "index1", "pinky1", "middle_tip")
        ours_a, his_a = (json.loads(Path(x).read_text()) for x in (a[4], a[5]))
        oa = np.array([ours_a[k] for k in keys])
        lo, hi = oa.min(0) - 0.05, oa.max(0) + 0.05
        material, tile = (2, 1003) if a[0] == "hand" else (4, 1005)
        extra = (4, 1005, Path(a[3]).with_name("aaron_nails.npz")) if a[0] == "hand" else None  # his nails ride the hand
        carry_region(Path(a[1]), Path(a[2]), Path(a[3]), material, ((lo[0], hi[0]), (lo[1], hi[1]), (lo[2], hi[2])),
                     anchors=(np.array([his_a[k] for k in keys]), oa), tile=tile, extra=extra)
    elif a[0] == "skin":  # skin OURS.npz SKIN_SOURCE.npz OUT.npz [EYES.npz] (his eyeballs: the eye rims pinned)
        carry_skin(Path(a[1]), Path(a[2]), Path(a[3]), Path(a[4]) if len(a) > 4 else None)
    else:  # usc OURS.npz hairstyles.zip ID OUT.npz
        carry(Path(a[1]), Path(a[2]), a[3], Path(a[4]))

# Build step 1 — the lid anatomy in the base mesh (JustStage base v2): the code plan (2026-11-05)

Approved design: `2026-11-05-character-design.md` piece 1 (the user: "your rec go on all"). Prototype and measurements:
`2026-11-05-research-base-mesh.md` §7 (scratchpad `lidlib.py`, `lid_gate.py`, `lid_clip.py`, `recess.py`).

## What the prototype proved, and what the code must add

- Proved: the lid-edge loop found by geometry (closed, longest cycle), one loop cut each side (vertices appended after
  19,158, every old index kept, shape keys carried), shaped to lash line 2.6 / margin 1.3 / eyeball rim 0.25 mm: the
  lower-lid band 28-50 px against HD Aaron's 26-63, the same pink.
- Must add (found by the prototype's checks): (1) the **contact step on every refit** - 20 of 66 eye targets clip the rim
  into the eyeball, 4 lift it; (2) the **upper lid ~2 mm forward** (real scans: its front 2.9 mm ahead of the cornea, ours
  1.0); (3) **appended vertices in every target** (a slider loaded after the cut doesn't move them); (4) **"the skin" is no
  longer vertices 0-13,379** - appended skin vertices follow the helpers, so every `[:BODY_VERTICES]` slice and
  `< BODY_VERTICES` test drops them (below); (5) **grooms re-bound** (their Surface Deform bind breaks on a vertex-count
  change - seen); (6) the library migrated.

## The pieces and their standards

| Piece | What | Standard |
|---|---|---|
| Base v2 file | `tools/make_base_v2.py` (run once, like `make_udim.py`) builds it from MPFB2's `base.obj`: the loop found, cut, shaped, the upper lid brought forward; writes `data/base/js_base_v2.obj` and `data/base/appended_v2.json` (per appended vertex: its two parent vertices on the cut edge, the edge parameter, its offset in the local frame of edge tangent / surface normal / bitangent; the moved ring vertices' neutral deltas) and the v1 -> v2 vertex map | spec §1.1 (`baseVersion`, a vertex map); Blender's subdivide for the cut; MakeHuman's OBJ |
| The skin set | `core/makehuman.py`: `skin_indices(n)` = 0..13,379 plus 19,158..n-1; every slice / test below moves to it | ours (one constant becomes one function) |
| Targets reach the new vertices | one function, `makehuman.extend_offsets(indices, deltas, base)`: each appended vertex's delta from its parents' deltas and its frame's rotation (Surface Deform's method) - called by every target reader | Blender's Surface Deform method; MakeHuman target format (NOT STANDARD - appending to MakeHuman's base, approved 2026-11-05) |
| The contact key | `head/parts.py` `refit`: after `eye_clearance`, an `eyelid_contact` shape key places the eyeball rim at 0.25 mm on its eyeball and eases the margin's middle | as `eye_clearance` (a refit shape key, spec) |
| Migration | `juststage/migrations/` step: a `baseVersion` 1 character gets base v2 (the vertex map), its grooms re-made or re-bound | spec §6 (ordered migration steps on `load_post` and package import) |
| Tools re-run | `make_face_regions.py`, `make_mouth_mask.py`, `make_udim.py` on base v2; the library rebuilt (backup first) | - |

## Blast radius (pasted greps, 2026-11-05)

`BODY_VERTICES` users (each moves to the skin set):

```
extension/juststage/modules/body/build.py:158     own = -float(shaped_coords(obj)[: makehuman.BODY_VERTICES, 2].min())
extension/juststage/modules/hair/lashes.py:156     if max(v) >= BODY_VERTICES:
extension/juststage/modules/head/eyes.py:91       return [list(p.vertices) for p in body.data.polygons if max(p.vertices) < BODY_VERTICES]
extension/juststage/modules/head/eyes.py:100      skin = build.shaped_coords(body)[:BODY_VERTICES].astype(np.float64)
extension/juststage/modules/head/eye_layers.py:315  skin = build.shaped_coords(character)[:BODY_VERTICES].astype(np.float64)
extension/juststage/modules/head/eye_layers.py:368  skin = build.shaped_coords(character)[:BODY_VERTICES].astype(np.float64)
extension/juststage/modules/head/parts.py:69      skin = build.shaped_coords(character)[:BODY_VERTICES]
extension/juststage/modules/head/parts.py:72      normals = normals.reshape(-1, 3)[:BODY_VERTICES]
extension/juststage/modules/head/parts.py:92      edges = edges[(edges < BODY_VERTICES).all(axis=1)]
extension/juststage/modules/head/parts.py:105     co[:BODY_VERTICES] += push.astype(np.float32)
tools/make_udim.py:64                             if max(verts) >= makehuman.BODY_VERTICES:
tests/blender/test_head.py:135, 150               skin = build.shaped_coords(body)[: makehuman.BODY_VERTICES]
```

Literal counts: `tests/blender/test_body.py:51` (`result.vertices == 19158`), `:84`, `:150`, `:152` (`[:13380]`);
`tools/face_test/face_shape.py:74, 133, 140`, `flame_fit.py:49`, `test_face_fit.py:53`, `test_face_project.py:573, 705`
(the face test's tools - they read the level-1 head export, re-exported on v2).

Target readers (each calls `extend_offsets`): `core/makehuman.py:82 read_target`, `body/build.py:60 _target_offsets`,
`body/sliders.py:80 _target`, `head/face_units.py:48`, `head/gnm_space.py:30`.

Library assets: 10 characters (`library/Characters/*.blend`), 16 hair grooms (`library/Hair/*/*.blend`) - backed up,
migrated, grooms re-made (ours) or re-bound (MakeHuman's styles).

Untouched by the append (old indices and UVs kept): `.mhclo` clothes and the fitted parts (eyes, teeth), the UDIM
images (face regions, mouth, nails - UV-based), the scan skins (HeadTile bakes), the joint cubes and rigs.

## Tests (each red first, then green)

1. Base v2: the vertex count and the appended range; old vertices' indices and UVs unchanged.
2. Every target moves each appended vertex where Blender's own subdivide would put it (a reference built in Blender for a
   sample of 20 targets: within 0.05 mm).
3. The eye sliders: all 66 targets, each alone at 1.0 - the eyeball rim between 0.05 and 1.0 mm off its eyeball (with
   the contact key).
4. The skin set: `eyes.openings` and the eye layers on v2 find the same opening as on v1 within 1 degree.
5. Migration: a v1 library character loads as v2 with its grooms attached and its sliders unchanged.
6. The gate's eye view: the lower-lid band in HD Aaron's range (the prototype's measure); the upper lid's front ~2.9 mm
   ahead of the cornea.

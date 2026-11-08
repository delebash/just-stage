# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The head's parts — GNM's eyes and teeth (with gums and tongue), fitted to the character by MakeHuman's MHCLO
(character-data-model.md §1.1: "Parts are fitted to the body as MakeHuman fits its eyes — by MHCLO"). Made offline by
`libs/wrap/gnm_to_hm08.py` and `tools/bind_parts.py`; names are MetaHuman's (`eyeLeft`, `eyeRight`, `teeth`).
"""

from __future__ import annotations

import json

import bpy
import numpy as np
from mathutils import Matrix

from ... import paths
from ...core import mhclo
from ..body import build
from . import part_materials

TOOL = ".dev/venv-tools/Scripts/python libs/wrap/gnm_to_hm08.py, then tools/bind_parts.py"


def _folder():
    return paths.generated("gnm", "parts", tool=TOOL)


def catalog() -> dict:
    return json.loads((_folder() / "parts.json").read_text(encoding="utf-8"))


def groups(part: str) -> dict[str, list[int]]:
    """A part's named vertex sets (`<part>.groups.json`, by tools/bind_parts.py), e.g. the teeth's
    `lower_teeth_and_gums`."""
    return json.loads((_folder() / f"{part}.groups.json").read_text(encoding="utf-8"))


def _binding(part: str) -> mhclo.Mhclo:
    return mhclo.parse(paths.generated("gnm", "parts", f"{part}.mhclo", tool=TOOL).read_text(encoding="utf-8"))


def parts_of(character: bpy.types.Object) -> dict[str, bpy.types.Object]:
    """The character's fitted head parts (eyes, teeth, ...) - not its grooms, which carry a part too ("scalp") but
    follow the body by their own surface deform."""
    cid = character.juststage.character_id
    fitted = catalog()
    return {o.juststage.part: o for o in bpy.data.objects if o.juststage.part_of == cid and o.juststage.part in fitted}


#: the shape key that keeps the lids' skin in front of the eyeballs (eye_clearance)
CLEARANCE = "JustStage eye clearance"
LID_GAP = 0.0003  # the outer lid skin's least gap over the eyeball


def eye_clearance(character: bpy.types.Object) -> int:
    """The lids' outer skin kept LID_GAP in front of the eyeballs: a shape can push lid skin inside an eye (the face
    test's Walter: 8 vertices an eye up to 0.95 mm in, the white showing through his upper lid - 2026-11-04). Outward-
    facing skin in front of the eye's centre and inside its sphere moves out along the eye's radius, its neighbours
    half as far; in a shape key of its own, made again on every refit. The socket's folded skin (it faces the eye) is
    left alone. Returns how many vertices moved."""
    from ...core.makehuman import skin_mask
    from . import eye_layers

    keys = character.data.shape_keys
    key = keys.key_blocks.get(CLEARANCE) if keys else None
    if key is not None:
        key.value = 0.0
    skin = build.shaped_coords(character)  # every vertex; the helpers masked out below
    is_skin = skin_mask(len(skin))
    normals = np.empty(len(character.data.vertices) * 3, np.float32)
    character.data.vertex_normals.foreach_get("vector", normals)
    normals = normals.reshape(-1, 3)
    push = np.zeros_like(skin)
    for part, eye in parts_of(character).items():
        if part not in ("eyeLeft", "eyeRight"):
            continue
        centre, radius = eye_layers._eye_sphere(eye)
        rel = skin - centre
        dist = np.linalg.norm(rel, axis=1)
        along = rel / np.maximum(dist, 1e-9)[:, None]
        poke = (dist < radius + LID_GAP) & (dist > radius - 0.006) & (skin[:, 1] < centre[1]) & is_skin
        poke &= np.einsum("ij,ij->i", normals, along) > 0.3
        push[poke] += (radius + LID_GAP - dist[poke])[:, None] * along[poke]
    moved = np.flatnonzero(np.abs(push).sum(axis=1) > 0)
    if not len(moved):
        return 0
    ring = np.zeros_like(push)
    count = np.zeros(len(push))
    edges = np.empty(len(character.data.edges) * 2, np.int32)
    character.data.edges.foreach_get("vertices", edges)
    edges = edges.reshape(-1, 2)
    edges = edges[is_skin[edges].all(axis=1)]
    for a, b in ((edges[:, 0], edges[:, 1]), (edges[:, 1], edges[:, 0])):
        np.add.at(ring, a, push[b])
        np.add.at(count, a, 1.0)
    ring = 0.5 * ring / np.maximum(count, 1.0)[:, None]
    push = np.where(np.abs(push).sum(axis=1, keepdims=True) > 0, push, ring)
    if key is None:
        if not character.data.shape_keys:
            character.shape_key_add(name="Basis", from_mix=False)
        key = character.shape_key_add(name=CLEARANCE, from_mix=False)
    co = np.empty(len(character.data.vertices) * 3, np.float32)
    character.data.shape_keys.reference_key.data.foreach_get("co", co)
    co = co.reshape(-1, 3)
    co += push.astype(np.float32)
    key.data.foreach_set("co", co.ravel())
    key.value = 1.0
    return int(len(moved))


RIM_GAP = 0.00025  # base v2's rim off the eyeball (modules/body/base.py: the prototype's 0.25 mm)
#: the lash line's least gap off the eyeball: with the rim at 0.25 mm a margin at least 0.75 mm wide (the sweep of
#: 2026-11-06: 38 of the 68 eye targets pressed the lash line up to 0.3 mm into the eyeball - the clearance key only
#: moves skin facing outward, and the lash line sits on the lid's edge)
LASH_MIN = 0.001
#: and its most: base v2's own lash line (the record's radii, 2.6 mm) - the clean-input gate's eye view (2026-11-06):
#: the opened eye's sliders push the lower lid's skin out, its lash line stood up to 5.2 mm off the eyeball under the
#: iris (the next row 0.8 mm), the margin a swollen glossy roll with a kink beside HD Aaron's ledge (1.0-2.3 mm seen);
#: the lash line's move is carried into the next two rings of lid skin (CARRY) so no step is left
CARRY = (0.6, 0.25)
#: the lower lid's margin a ledge, as the upper's is: the lower lash line turned LEDGE_TURN of the way from its own line
#: from the eye's centre onto its rim's, LEDGE_GAP off the eyeball. Along its own line hm08's lower lash line sat 2.4 mm
#: straight below its rim at the rim's depth - a margin 74-80 deg below horizontal, a wall facing the camera: the
#: thick roll under the eye (the upper lash line 2.2 mm in front of its rim, 5-7 deg). Measured on the gate's eye view
#: (2026-11-07 late, factors lidledge): 0.8 / 2.3 mm DISTS 0.258 against 0.264-0.267, the roll gone by eye; 1.0 / 2.3
#: 0.259; 1.0 / 1.6 0.264
LEDGE_TURN, LEDGE_GAP = 0.8, 0.0023


def eyelid_contact(character: bpy.types.Object) -> int:
    """Base v2's lid margin kept on the eyeball for the current shape: each rim RIM_GAP off its eyeball and the
    margin's middle row midway between the rim and the lash line, along their own lines from the eye's centre - in a
    shape key of its own (base.CONTACT), made again on every refit. The rim follows the lid's skin while the eyeball is
    fitted from MakeHuman's helpers, so a slider that moves one differently from the other parts them (measured over
    the 66 eye targets: 20 clip the rim into the eyeball by up to 1.6 mm, 4 lift it 2-3 mm off -
    docs/plans/2026-11-05-research-base-mesh.md §7). Returns how many rows it placed (0 on hm08 itself)."""
    from ..body import base
    from . import eye_layers

    if character.juststage.base_version < base.VERSION:
        return 0
    keys = character.data.shape_keys
    key = keys.key_blocks.get(base.CONTACT) if keys else None
    if key is not None:
        key.value = 0.0
    eyes = [p for name, p in parts_of(character).items() if name in ("eyeLeft", "eyeRight")]
    if not eyes:
        return 0
    spheres = [eye_layers._eye_sphere(e) for e in eyes]
    co = build.shaped_coords(character)
    push = np.zeros_like(co)
    rows = base.rows()
    for lash, margin, rim in rows:
        centre, radius = min(spheres, key=lambda s: np.linalg.norm(co[margin] - s[0]))

        def off(i, c=centre, r=radius):
            return np.linalg.norm(co[i] - c) - r

        def to(i, gap, c=centre, r=radius):
            d = (co[i] - c) / np.linalg.norm(co[i] - c)
            return c + d * (r + gap) - co[i]

        if rim >= 0:
            push[rim] = to(rim, RIM_GAP)
        if lash >= 0 and rim >= 0 and co[rim][2] < centre[2]:  # the lower lid: its margin turned into a ledge
            d_rim = (co[rim] - centre) / np.linalg.norm(co[rim] - centre)
            d_lash = (co[lash] - centre) / np.linalg.norm(co[lash] - centre)
            d = (1 - LEDGE_TURN) * d_lash + LEDGE_TURN * d_rim
            d /= np.linalg.norm(d)
            push[lash] = centre + d * (radius + LEDGE_GAP) - co[lash]
            mid = (d + d_rim) / np.linalg.norm(d + d_rim)
            push[margin] = centre + mid * (radius + (LEDGE_GAP + RIM_GAP) / 2) - co[margin]
            continue
        if lash >= 0:  # a lid pressed onto the eyeball or pushed off it keeps its margin's width
            lash_gap = min(max(off(lash), LASH_MIN), base.record()["radii_mm"]["lash"] / 1000)
            push[lash] = to(lash, lash_gap)
        else:
            lash_gap = base.record()["radii_mm"]["lash"] / 1000
        push[margin] = to(margin, (lash_gap + RIM_GAP) / 2)
    _carry(character, rows, push)
    if key is None:
        key = character.shape_key_add(name=base.CONTACT, from_mix=False)
    ref = np.empty(len(character.data.vertices) * 3, np.float32)
    character.data.shape_keys.reference_key.data.foreach_get("co", ref)
    key.data.foreach_set("co", (ref.reshape(-1, 3) + push.astype(np.float32)).ravel())
    key.value = 1.0
    return len(rows)


def _carry(character: bpy.types.Object, rows: np.ndarray, push: np.ndarray) -> None:
    """The lash line's moves carried into the lid's skin beyond it: each ring outward (by the mesh's edges, away from
    the margin's rows) takes CARRY's share of the mean move of its neighbours in the lash line."""
    edges = np.empty(len(character.data.edges) * 2, np.int64)
    character.data.edges.foreach_get("vertices", edges)
    edges = edges.reshape(-1, 2)
    both = np.vstack([edges, edges[:, ::-1]])
    taken = np.zeros(len(push), bool)
    taken[rows[rows >= 0]] = True
    ring = np.zeros(len(push), bool)
    ring[rows[rows[:, 0] >= 0, 0]] = True
    source = push.copy()
    for share in CARRY:
        reach = both[ring[both[:, 0]] & ~taken[both[:, 1]]]
        if not len(reach):
            break
        total = np.zeros_like(push)
        np.add.at(total, reach[:, 1], source[reach[:, 0]])
        count = np.bincount(reach[:, 1], minlength=len(push))
        nxt = count > 0
        push[nxt] = share * total[nxt] / count[nxt, None]
        source = np.zeros_like(push)
        source[nxt] = total[nxt] / count[nxt, None]  # the lash line's own move, shared on by its distance in rings
        taken |= nxt
        ring = nxt


def refit(character: bpy.types.Object) -> None:
    """Move every part to the character's current shape."""
    base = build.shaped_coords(character)
    for part, obj in parts_of(character).items():
        if part == "teeth" and obj.data.shape_keys:  # old jaw keys (the stand-in before the jaw joint): the fit
            obj.shape_key_clear()  # writes the vertices themselves
        co = mhclo.fit(_binding(part), base).astype(np.float32)
        obj.data.vertices.foreach_set("co", co.ravel())
        obj.data.update()
    from ..body import base
    from . import eye_layers

    keys = character.data.shape_keys
    if keys and base.CONTACT in keys.key_blocks:  # the clearance measures the lids without the last contact
        keys.key_blocks[base.CONTACT].value = 0.0
    eye_clearance(character)
    eyelid_contact(character)  # base v2's rim back on the eyeball, after the clearance moved the lid's skin
    eye_layers.refit(character)  # the occlusion and tearline ride the eyes
    from . import lip_seal

    lip_seal.seal(character)  # the neutral's lips closed (hm08 leaves a see-through slit)
    from . import blink_contact

    blink_contact.make(character)  # the blink closes onto the lower lid on today's shape (when the units are there)


def add(character: bpy.types.Object) -> list[str]:
    """Add the parts the character doesn't have yet, fitted to its shape; returns their names."""
    existing = parts_of(character)
    added = []
    for part, info in catalog().items():
        if part in existing:
            continue
        before = set(bpy.data.objects)
        bpy.ops.wm.obj_import(filepath=str(_folder() / info["obj"]), use_split_objects=False, use_split_groups=False)
        obj = (set(bpy.data.objects) - before).pop()
        obj.matrix_basis = Matrix.Identity(4)  # the fit below gives final positions in Blender's axes
        obj.name = f"{character.name}.{part}"
        obj.data.name = part
        obj.data.shade_smooth()
        obj.parent = character
        obj.juststage.part = part
        obj.juststage.part_of = character.juststage.character_id
        part_materials.assign(obj, part, groups(part))
        added.append(part)
    # the importer's own 90-degree turn stays in each new part's world matrix until the scene updates (the next import
    # updated the one before it, so only a part imported last - an eye added again alone - kept it; 2026-11-04)
    bpy.context.view_layer.update()
    refit(character)
    from . import eyes

    props = character.juststage
    for part in added:
        if part in ("eyeLeft", "eyeRight"):  # the procedural iris and white (MPFB2's), on UVs by the 3D radius
            eye = parts_of(character)[part]
            eyes.shade(eye)
            eyes.set_colour(eye, props.iris_colour, props.iris_accent, props.eye_white)  # the character's own
    if {"eyeLeft", "eyeRight"} & set(added):  # CC5's and MetaHuman's two films over the eyeball
        from . import eye_layers

        eye_layers.add(character)
    return added

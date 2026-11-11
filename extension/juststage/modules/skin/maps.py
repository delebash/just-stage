# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""A skin's maps (docs/standards/character-data-model.md: the body's one UDIM layout, 1001 head and neck … 1005 nails;
the channels `base_color`, `normal` - tangent space, OpenGL - `roughness`, `cavity`, and a fine `height`), as CC5's
skins carry scanned colour and relief (the realism working doc, `docs/plans/2026-11-04-realism.md`).

Every character has the layout (`add_layout`, made once by `tools/make_udim.py`), so a skin's maps fit any of them.
A skin is a material: Principled BSDF with Random Walk (Skin) subsurface from the chromophore model (material.py), the
maps on its inputs, and the tone it was made at (`juststage.map_*`). The character's own tone recolours it by a
per-channel gain - its tone's colour over the skin's own (core/skin_optics.py) - so the Skin tab's sliders keep working
on a mapped skin. Pores everywhere from a tiled scan patch on hm08's own UVs (the face test's, ~5.6 cm a tile).
Images: Blender's UDIM tiled images (https://docs.blender.org/manual/en/5.3/modeling/meshes/uv/workflows/udims.html).
"""

from __future__ import annotations

import json

import bpy
import numpy as np

from ... import paths

LAYOUT_TOOL = "python tools/dev.py blender -b --python tools/make_udim.py"
UV = "UDIM"
CHANNELS = ("base_color", "normal", "roughness", "cavity", "height")
COLOUR_SPACE = {"base_color": "sRGB"}  # the rest are data
TILES = (1001, 1002, 1003, 1004, 1005)
#: the face test's skin shading (tools/face_test/test_face_project.py, rounds 40-79)
COAT_WEIGHT, COAT_ROUGHNESS, COAT_IOR, SHEEN_WEIGHT, SHEEN_ROUGHNESS = 0.12, 0.44, 1.45, 0.1, 0.4
HEIGHT_STRENGTH, HEIGHT_DISTANCE = 0.15, 0.0004  # the painting's own fine relief (the normal map carries the larger)
#: each UDIM tile's millimetres per UV unit on the default human (measured 2026-11-05: the median polygon's
#: sqrt(3D area / UV area); the head tile by its face, where relief shows): the relief layers keep one real size on
#: every tile. hm08's own `UVMap`, which carried the pores before, spans 1.1 m a unit on the face but 2.1 on the torso
#: and 7.0 on the thigh - the pores were twice and six times their size there
MM_PER_UV = {1001: 724.0, 1002: 851.0, 1003: 753.0, 1004: 1224.0, 1005: 48.0}
#: hm08's UVs are not even inside a tile (measured 2026-11-06 on the default man: the head tile's face 600-700 mm a UV
#: unit, its neck and shoulders ~1150, ears and the back of the head up to 1560) - one tiling a tile gave the neck and
#: shoulders pores 1.6x the face's and a step at the torso's border. CC5 tiles its micro normal by region (one tiling a
#: material - Reallusion's manual, "Micro Normal": https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/
#: 15_Digital_Human_Shader/Skin/Micro_Normal.htm); ours by each place's own density: a corner attribute TEXEL (2 log2 of
#: the place's mm per UV over its tile's, on the rest shape, smoothed inside the tile - add_texel), the relief layers
#: sampled at TEXEL_LEVELS' half-octave tilings and cross-faded by it, their contrast kept (_levels). No attribute
#: (a character from before) reads 0: one tiling a tile, as before.
TEXEL = "juststage_texel"
TEXEL_LEVELS = (-1, 0, 1, 2)  # half octaves: x0.71, x1, x1.41, x2 the tile's tiling
TEXEL_SMOOTH = 12  # passes of the corner average inside a tile (a few cm on hm08)
#: the pore tile (pore_relief): Ten24's scanned forehead relief since 2026-11-08 (its upper cheek before - the forehead
#: measured better or equal against HD Aaron everywhere, tools/face_test/pore_tile.py TEN24_CROPS), its own size in its
#: pores.json (the Lee Perry-Smith cheek tile of 2026-11-05, 56 mm, carried his stubble's streaks -
#: docs/plans/2026-11-06-inputs-audit.md)
PORE_TOOL = ".dev/venv-rdf/Scripts/python -I tools/face_test/pore_tile.py"
#: the pores' relief: full strength, 0.3 mm (the gate, 2026-11-05: 0.35 / 0.2 mm left a scanned skin's cheek at 0.39 of
#: HD Aaron's pore band; 1.0 / 0.3 mm brought it to 0.99 against his 0.96 - his pores are relief, his colour alone 0.40)
#: 2026-11-06, the clean skins with Ten24's tile: 0.15 mm brings the cheek's pore / fold bands to HD Aaron's (1.135 /
#: 0.884 vs 1.154 / 0.894; at 0.3 mm 1.74 / 1.31 - an orange peel); the gate's cheek view, scratchpad pore_tune.py
PORE_STRENGTH, PORE_DISTANCE = 1.0, 0.00015
#: the pores' depth by sex (the character's gender macro: 0 a woman, 1 a man) - women's facial pores are finer; the
#: shared pore tile, judged against HD Aaron on the men, read cobbled on the Average woman's bare cheek, x0.7 as her
#: skin (2026-11-09, `.dev/gate/parts/2026-11-09womanpores`, by eye; x0.5 near too smooth)
PORES_BY_SEX = (0.7, 1.0)
#: per-pore shine: the specular scaled by PORE_SHINE[0] + PORE_SHINE[1] x the pore tile's height (darker in the pits)
PORE_SHINE = (0.4, 0.6)
#: the face's regions (tools/make_face_regions.py): the relief's depth scaled by region on the head tile - a forehead
#: three times a cheek's, as CC5's region masks (HD Aaron's forehead had three times our uniform depth's detail)
REGIONS_TOOL = "python tools/dev.py blender -b --python tools/make_face_regions.py"
REGION_RELIEF_SCALE = 8.0  # the map's R x this = the factor (make_face_regions.RELIEF_SCALE)
#: the microrelief - the skin's polygon network of fine furrows, finer than the pores (rec 18; the spec's
#: `micro_normal`, character-data-model.md §3.1): tools/make_microrelief.py's generated tile, its size on the skin and
#: its depth as the part-by-part gate picked them (`docs/gate/2026-11-05/report.md`: HD Aaron's cheek's finest band
#: 0.45, ours 0.23 without it, 0.42 with it at 0.03 mm)
MICRO_TOOL = ".dev/venv-tools/Scripts/python -I tools/make_microrelief.py"
MICRO_TILE_MM = 10.0
#: 2026-11-06: 0.015 mm (from 0.035) - the cheek's finest band 0.63 vs HD Aaron's 0.51 (0.035: 0.80). 2026-11-07: the
#: layered tile (make_microrelief.py `layered`) has 0.372x the old tile's slope per unit of height, so x2.686 keeps the
#: slope - HD Aaron's micro slope 0.090 (his tile's 0.285 x his shader's 0.317), ours 0.095 at the cheek's x1.35.
#: 2026-11-10: x0.75 with the coat on the bumped normal (below) - the coat now shines off the relief too, and the
#: cheek's micro band went 1.07 -> 1.33 of HD Aaron's; x0.75 puts it back at 1.07 (`factors coatnormal`)
MICRO_STRENGTH, MICRO_DISTANCE = 1.0, 0.0000302
#: the nails (rec 14, the realism brief §6.14: "a layered nail shader on tile 1005"): each nail's own coordinates
#: over its whole fingertip, per vertex (`tools/make_nail_coords.py`: along it 0 at the cuticle line to 1 at the
#: fingertip's end, across it -1 to 1 over the fingertip's back, its digit) - until 2026-11-10 they filled the tile's
#: island alone, a coarse polygon that cut the plate into an octagon ~55% of the finger's width where HD Aaron's spans
#: ~77% (the own-content proof, 13:5x-14:4x); the plate drawn in them with a gently curved cuticle edge and rounded
#: sides, over a bed tinted toward blood's red, a lunula as long as its digit's (the gaps research §3: visible on 96% of
#: thumbs, 48% of little fingers; toes but the big one rarely), a white free edge, faint lengthwise ridges; matte; its
#: edge raised and the skin's fold beside it by a bump, the skin's relief flat under it
NAIL_TOOL = "python tools/dev.py blender -b --python tools/make_nail_coords.py"
NAIL_ATTR = "js_nail"  # the coordinates as a point colour attribute: along, (across + 1) / 2, digit / 10, inside
#: the arms' and hands' tile (1003): the microrelief x2 - HD Aaron's back of the hand against ours in EEVEE, the
#: texture's excess over his own patch-to-patch (`tools/gate/dists.py --patches`) 0.071 -> 0.047 (2026-11-07; the
#: torso's and the foot's didn't move with it, so only this tile)
ARM_TILE_INDEX, ARM_MICRO = 2, 2.0
#: the hands on that tile (HANDS_ATTR: each vertex's share by the skeleton's hand and finger weights) their own: at the
#: nails close-up the finger read cracked (the microrelief x2) and red-speckled (the face's pores); x1 / x0.5 smooth it
#: and put the back of the hand's pores inside HD Aaron's spread at his tone (1.46 -> 0.91 of his), while on the whole
#: tile they also moved the foot's form band out of his (1.08 -> 1.24) - hence the hands alone (2026-11-10,
#: `.dev/gate/parts/2026-11-10fingerskin*`, `handtone2`, `handtone3`)
HANDS_ATTR = "js_hands"
HAND_PORES, HAND_MICRO = 0.5, 1.0
#: the scans' relief (the skin's normal map) on the hands, by the same share: at full strength the back of the hand
#: read drier and older than HD Aaron's, its fold and form bands 1.38 / 2.16 of his at his tone; with none 0.97 / 1.16
#: (inside his spread) but plain beside his soft knuckle wrinkles (2026-11-10 rounds 10 and 15,
#: `.dev/gate/parts/2026-11-10round10`)
HAND_RELIEF = 0.2
#: the skeleton's bones whose weights make the hands' share (UE5's names, modules/rig: hand, metacarpals, fingers)
HAND_BONES = ("hand_", "thumb_", "index_", "middle_", "ring_", "pinky_")
#: where the plate starts: along > cuticle + curve * across^2 - the curve 0.35 drew a deep U over the whole fingertip,
#: 0.12 his shallow arc (`factors nailobj`, 2026-11-10 round 2)
NAIL_CUTICLE, NAIL_CUTICLE_CURVE = 0.08, 0.12
#: |across| inside this - his plate ~77% of the finger's width; 0.78 (round 3) - and the edges' softness (in along
#: / across)
NAIL_SIDE, NAIL_EDGE_SOFT = 0.78, 0.06
NAIL_LENGTH = 0.9  # the fingers' plate ends this far toward the fingertip's end (round 2: at 0.97 it wrapped the tip)
#: the free edge rounded at its corners, as the cuticle is: the plate ends where along > 1 - curve * across^2 - hm08
#: has no nail outline, so the tile's islands carry fingertip skin faces at their corners (RESEARCH 14.5), which a
#: square plate painted white (2026-11-08)
NAIL_TIP_CURVE = 0.35
NAIL_FREE_EDGE = (0.92, 0.97)  # along: the free edge - a thin pale rim on a short nail - fades in over this
#: the toes' plate, its length and half-width: hm08's toe islands run over the toe's tip, so the fingers' plate covered
#: the whole tip - a large pale sticker beside HD Aaron's short plate on top of the toe (2026-11-09,
#: `.dev/gate/parts/2026-11-09toenail`). 0.6 / 0.7: a short plate on top of the toe with its free edge, as his
#: (`.dev/gate/parts/2026-11-09toeplate`; 0.5 / 0.65 left slivers). Over the whole toe tip (2026-11-10, the coordinates
#: no longer the island's) 0.6 / 0.7 made the big toe's plate wider and longer than his; 0.45 / 0.55 his size
#: (`.dev/gate/parts/2026-11-10round4`, the foot view)
TOE_PLATE_LENGTH, TOE_PLATE_SIDE = 0.45, 0.55
NAIL_LUNULA_FINGERS = (0.25, 0.03)  # lunula length = first - second * digit (thumb 0.22 ... little 0.10)
NAIL_LUNULA_TOES = (0.06, 0.0)  # the big toe's, the others' (rarely seen)
#: linear, mixed into the skin's colour: the plate's colour against the skin's, Lab distance to HD Aaron's - (0.50, 0.30,
#: 0.27) at 0.25 3.2, at 0.12 2.7 (cooler, less red); warmer (0.46, 0.33, 0.22) at 0.2 1.7 (2026-11-10 rounds 2 and 4,
#: `factors nailobj`, `nailbedcolour`)
NAIL_BED, NAIL_BED_SHARE = (0.46, 0.33, 0.22), 0.2
#: the lunula's pale share: 0.35 read as a white crescent beside HD Aaron's barely-seen one; 0.05 as his (the gate's
#: `nailluna`, 2026-11-08, sheet `scratchpad/sheet_D22_luna.png`)
NAIL_LUNULA, NAIL_LUNULA_SHARE = (0.82, 0.72, 0.68), 0.05
NAIL_TIP = (0.80, 0.75, 0.66)
#: how much the fold's groove round the plate darkens it - 0.45 drew a dark outline round every nail, a sticker beside
#: HD Aaron's plates set into the fingertip (the nail bed's displaced groove and fold already shade that edge); 0.15 a
#: faint edge (2026-11-09, `.dev/gate/parts/2026-11-09toenail`, the foot and nails views; 0 lost the plate's edge)
NAIL_GROOVE = 0.15
NAIL_RIDGES = 0.05  # +- share of the colour
#: the plate's shine: matte like HD Aaron's - at 0.18 / 0.6 / 0.5 (roughness, specular level, coat) our plate read
#: milky white beside his skin-toned one; at 0.55 / 0.3 / 0 it reads as his (the gate's `nailshine`, 2026-11-08)
NAIL_ROUGHNESS, NAIL_SPECULAR, NAIL_COAT = 0.55, 0.3, 0.0
NAIL_RAISE = 0.0006  # m: the plate over the skin beside it
#: the skin's fold round the plate (the proximal and side folds; the geometric bed it replaces drew the plate's outline
#: on the tile's island): the plate drawn this much wider past its cuticle and sides, its band raised NAIL_FOLD x the
#: plate's raise (`factors nailobj`, 2026-11-10)
#: 2026-11-10 round 14 (mine): 1.2, reach (0.10, 0.14), edges 0.06 drew a step beside HD Aaron's soft rolled
#: fold (`.dev/gate/parts/2026-11-10round14`)
NAIL_FOLD, NAIL_FOLD_REACH = 1.2, (0.18, 0.22)
NAIL_FOLD_SOFT = 0.12  # the fold's edges' width (the plate's own stay NAIL_EDGE_SOFT)
#: the mouth's lining (the inner lips and the mouth's skin; `tools/make_mouth_mask.py`): wet mucosa where the mask is -
#: no scan or painting covers it, so an open mouth showed a pale rim of skin inside the lips (the gate, 2026-11-05)
MOUTH_TOOL = "python tools/dev.py blender -b --python tools/make_mouth_mask.py"
#: the lids' margins where the resting shape stretches them 2-10x against the UV layout (the eyelid contact - always on;
#: tools/make_stretch_mask.py): every map read through the UVs streaked the lower lid's ledge at the eye view
#: (2026-11-09); a margin is smooth wet tissue, so inside it the relief layers are out (`_relief_off_stretched`) and the
#: composed colour smoothed (skin_base.STRETCH_SMOOTH)
STRETCH_TOOL = "python tools/dev.py blender -b --python tools/make_stretch_mask.py"
#: the closed lid (the own-content proof, 2026-11-10 00:49): the skin a blink opens out over the closed eye is a sliver of
#: the head tile (tools/make_lid_mask.py: its faces 2.4-5x), so every map read through the UVs streaked it and smoothing
#: it always made the open lid glossy; MetaHuman's and CC5's way - detail driven by the expression's own value: by each
#: eye's blink x its mask, the UV relief faded out, the colour toward a soft copy (1/LID_SOFT_SCALE of the head tile,
#: sampled Linear) with the eyes' surround tint lifted (a closed lid reads lighter than the open eye's surround),
#: and fine pits in OBJECT space (LID_PORE_DEPTH, LID_PORE_CELL - not stretched by the UVs; NOT STANDARD: a procedural
#: detail, the standard a scanned closed-lid map - none free). The open eye is unchanged (blink 0: pixel-equal).
LID_TOOL = "python tools/dev.py blender -b --python tools/make_lid_mask.py"
#: the lips' mask with a soft border (MPFB2's lips mask blurred - 2026-11-10: a crisp drawn outline beside HD Aaron's
#: lip fading into the skin)
LIPS_TOOL = ".dev/venv-tools/Scripts/python -I tools/make_lips_soft.py"
#: the smile's crow's feet (2026-11-10, beside HD Aaron's smile): our own wrinkle generator's lines out from each eye's
#: outer corner, the left side's in red, the right's in green (1 flat, lower in a groove), faded in by each side's smile
#: (head/face_units.SMILE_PROPS); CROWS_DEPTH the groove's depth at full smile (x3 the wrinkle tool's 0.4 mm read like
#: his at the eye-smile view, `.dev/gate/parts/2026-11-10smile`)
CROWS_TOOL = ("python tools/dev.py blender -b --python tools/make_wrinkles.py -- --only crows --split "
              "--out extension/juststage/data/generated/skin --name crows_feet.png")
CROWS_DEPTH = 0.0012
LID_SOFT_SCALE, LID_PORE_DEPTH, LID_PORE_CELL = 32, 0.00015, 0.0006  # -, m, m
MOUTH_COLOUR, MOUTH_SHARE = (0.42, 0.11, 0.11), 0.85  # linear
MOUTH_ROUGHNESS, MOUTH_SPECULAR, MOUTH_COAT = 0.25, 0.7, 0.6
#: the lips' vermilion over any skin - MPFB2's CC0 lips mask (`mpfb_lips.jpg`, hm08's own UVs) - as CC5's lip colour:
#: scanned and painted skins carry their person's lips (HSR0040's pale, thinner than hm08's) or none; a vermilion keeps
#: the skin's red and loses about a quarter of its green and a fifth of its blue
#: the lid margin (base v2's appended rows, modules/body/base.py's `js_margin`: 1 on the margin and rim, 0.35 on the
#: lash line): wet pink tissue - the skin's colour times MARGIN_TINT (so a darker skin's margin is darker: conjunctival
#: melanosis), glossy and wet. The tint is the prototype's measured colour (0.45, 0.17, 0.15 over a light skin's
#: ~0.60, 0.42, 0.35) as a ratio; the band it made, 28-50 px, was in HD Aaron's 26-63 (research-base-mesh §7) - to be
#: measured again on clean skins (docs/plans/2026-11-06-inputs-audit.md)
#: 2026-11-06, the clean-input gate: at (0.75, 0.42, 0.43) / 0.18 / coat 0.6 the lower lid read as a swollen glossy
#: pink rim beside HD Aaron's thin wet line - softer
MARGIN_TINT, MARGIN_ROUGHNESS, MARGIN_COAT = (0.86, 0.62, 0.62), 0.25, 0.35
LIP_TINT, LIP_STRENGTH = (1.0, 0.56, 0.90), 1.0  # at 0.74 / 0.79 still paler than HD Aaron's
#: the lips darker and redder toward the closed mouth's line (linear, x the colour at the line; by the seam's band,
#: MOUTH_TOOL's mouth_seam.png) - real lips deepen into the line, ours were one flat pink (the own-content proof,
#: 2026-11-08: HD Aaron's dark red at the seam)
LIP_SEAM_TINT, LIP_SEAM_STRENGTH = (0.70, 0.48, 0.50), 1.5  # 1.5: the line between the lips deepens at full
#: resolution, most at the corners (a 10 mm band, `.dev/gate/parts/2026-11-08lashes`)
#: the skin round the eyes darker and a little red-brown (linear, x the colour; by REGIONS_TOOL's face_eyes.png, the
#: eyes region within 17 mm of a pupil, softened) - real lids and under-eyes are darker; ours read the cheek's flat
#: colour and the eyes looked pasted on (the own-content proof 2026-11-08: `factors eyedark` at 0.65 / 0.5 beside HD
#: Aaron's - the eyes set in at both; the scan composition's EYE_DARK only caps a scan's own darkening, it can't add it)
EYE_SURROUND_TINT = (0.60, 0.54, 0.51)
#: the upper lip deeper red than the lower (linear, x the colour; by MOUTH_TOOL's lips_upper.png - the lips on the upper
#: side of the mouth's slit): real upper lips are, HD Aaron's among them; ours were one pink on both (2026-11-09,
#: `.dev/gate/parts/2026-11-09upperlip`, by eye: (0.85, 0.65, 0.68) and this, this the closer)
LIP_UPPER_TINT = (0.75, 0.52, 0.55)
#: 2026-11-06, the clean-input gate's lips view: ours matte orange (L* a* b* 58.6 / 23.4 / 23.5), HD Aaron's redder and
#: less yellow (56.4 / 30.4 / 15.1) and his lower lip shining - the tint from the two lips' linear ratio (0.70 / 0.75 x
#: 0.80 / 1.22), the vermilion smoother and lightly coated
#: 2026-11-09 (`.dev/gate/parts/2026-11-09lipgloss`, by eye at full resolution): at 0.33 / 0.3 the lip lines caught
#: wet highlights - crinkled cellophane at extreme close-up beside HD Aaron's soft matte lips; 0.6 / 0.05 then read as
#: lip skin up close, but beside him at the face, lips and open-mouth views it read as matte clay, the lines unseen
#: (`.dev/gate/parts/2026-11-09lipsheen`): 0.4 / 0.2 - a soft sheen on the lower lip, its lines catching the light as
#: his do, no cellophane at the corner's crop
LIP_ROUGHNESS, LIP_COAT = 0.4, 0.2
#: the lips' fine vertical lines - our own (no free scan resolves them: Ten24's lips are ~220 texels across): a wave in
#: bands across the lip, its distortion and a noise of ~4 mm cells making the furrows uneven, as a bump inside the lips'
#: mask. Judged by eye beside HD Aaron (2026-11-08, `.dev/gate/parts/2026-11-08ao`, `factors liplines*1.3*0.4*4*0.8`):
#: the smooth "rubber" lips read as lips. In hm08's own UVs ("UVMap", the mask's) so the lines ride the lips through
#: every expression: across the lip V runs ~1,602 mm a unit on hm08's base (measured 2026-11-08 on base.obj's faces under
#: the mask), the lines are bands along V. (period mm, depth m, distortion, how much the noise varies the lines)
#: 2026-11-08 late, at full resolution (`.dev/gate/parts/2026-11-08lipset`): (1.3, 0.4 mm, 4, 0.8) read as an even rib -
#: corduroy - beside HD Aaron's sparse soft creases; sparser, shallower, more irregular and fading in patches reads as
#: lip skin (half the depth alone was still a rib)
#: 2026-11-09 (`.dev/gate/parts/2026-11-09lipworm`, -lipcrease): with the lips' sheen (0.4 / 0.2) the sine ripple at
#: distortion 8 and fractal detail 3 read as an even worm-like crinkle, crepe paper - equal ridges and valleys; real
#: lip lines are thin creases on a smooth lip: the wave's 0-1 raised to LIP_CREASE (a plateau, a narrow valley each
#: period), distortion 3, detail LIP_LINES_DETAIL 1 (sparser / deeper creases read as parallel ribs again)
LIP_LINES = (1.8, 0.00015, 3.0, 1.0)
LIP_CREASE, LIP_LINES_DETAIL = 0.2, 1.0
LIP_MM_PER_V, LIP_NOISE_MM = 1602.0, 4.0
#: the ears' redness - MPFB2's CC0 ears mask (`mpfb_ears.jpg`, hm08's own UVs), the colour x EAR_TINT inside it: ours
#: read pale beside HD Aaron's red, translucent ear (2026-11-08, `.dev/gate/parts/2026-11-08ears`, by eye; the plan's
#: §5 "a map on MPFB2's CC0 ears mask only if the ear view shows a gap")
EAR_TINT = (1.0, 0.78, 0.76)
#: the ears' redness is blood showing, and melanin hides it: EAR_TINT is the tint at EAR_TINT_MELANIN (the gate's man,
#: where it was judged beside HD Aaron); on another tone it is scaled by how much EAR_BLOOD x the blood moves the
#: skin model's green there against at EAR_TINT_MELANIN - at melanin 0.15 nothing (2026-11-09: the Muscular man's ear
#: glowed orange-red beside his dark skin, its base colour R/G 4.3 against his neck's 2.5; skin_optics: blood x 2.5
#: lowers green 13% at melanin 0.03, 2% at 0.1, 0% at 0.15)
EAR_TINT_MELANIN, EAR_BLOOD = 0.03, 2.5
OILINESS_DEFAULT = 0.5  # the oiliness slider's default (skin_set_tone.Params): the chain's factor is 1 there
SPECULAR_FROM_CAVITY = 0.5  # Blender's standard specular level where the cavity map is 1
#: the body's mottling below the head tile (its maps are plain colour there): a seamless 3D noise in the object's own
#: metres, a few centimetres across, +-MOTTLE/2 of the colour - SkinGen's broad "blotch" layer in kind
MOTTLE, MOTTLE_SCALE, MOTTLE_DETAIL = 0.14, 18.0, 4.0
#: the clear coat (the skin's oily sheen) on the face only: over the whole body it read as oiled plastic (Amara's
#: body, Cycles, 2026-11-04); the body keeps a trace
BODY_COAT_WEIGHT = 0.03
NODE = "juststage.maps."  # this module's nodes are named with it


def layout() -> tuple[np.ndarray, np.ndarray]:
    data = np.load(paths.generated("skin", "udim.npz", tool=LAYOUT_TOOL))
    return data["uv"], data["tile"]


def add_layout(obj: bpy.types.Object) -> None:
    """The body's UDIM layer (each loop's place in its tile), beside hm08's own `UVMap`."""
    me = obj.data
    if UV in me.uv_layers:
        return
    uv, _tile = layout()
    if len(uv) != len(me.loops):
        raise ValueError(f"{obj.name}: {len(me.loops)} loops, the layout has {len(uv)} (not hm08?)")
    active = me.uv_layers.active
    me.uv_layers.new(name=UV).data.foreach_set("uv", uv.ravel())
    if active is not None:
        me.uv_layers.active = active  # hm08's own map stays the one the tools edit
    for layer in me.uv_layers:
        layer.active_render = layer.name == "UVMap"


def add_texel(obj: bpy.types.Object) -> None:
    """TEXEL on `obj`'s corners: 2 log2 of each place's millimetres a UV unit (sqrt(3D area / UV area) of its polygons
    on the rest shape - the Basis, before shape keys and modifiers) over its tile's MM_PER_UV, averaged over the
    polygons round each corner inside its tile, TEXEL_SMOOTH times; 0 on the nails' tile (their own coordinates)."""
    me = obj.data
    if UV not in me.uv_layers or not me.polygons:
        return
    co = np.empty(len(me.vertices) * 3, np.float64)
    (me.shape_keys.reference_key.data if me.shape_keys else me.vertices).foreach_get("co", co)
    co = co.reshape(-1, 3) @ np.array(obj.matrix_world)[:3, :3].T
    uv = np.empty(len(me.loops) * 2, np.float64)
    me.uv_layers[UV].data.foreach_get("uv", uv)
    uv = uv.reshape(-1, 2)
    loop_vert = np.empty(len(me.loops), np.int64)
    me.loops.foreach_get("vertex_index", loop_vert)
    me.calc_loop_triangles()
    tri = np.empty(len(me.loop_triangles) * 3, np.int64)
    me.loop_triangles.foreach_get("loops", tri)
    tri = tri.reshape(-1, 3)
    tri_poly = np.empty(len(me.loop_triangles), np.int64)
    me.loop_triangles.foreach_get("polygon_index", tri_poly)
    p = co[loop_vert[tri]]
    a3 = np.linalg.norm(np.cross(p[:, 1] - p[:, 0], p[:, 2] - p[:, 0]), axis=1) / 2
    q = uv[tri]
    d1, d2 = q[:, 1] - q[:, 0], q[:, 2] - q[:, 0]
    a2 = np.abs(d1[:, 0] * d2[:, 1] - d1[:, 1] * d2[:, 0]) / 2
    n = len(me.polygons)
    area3 = np.bincount(tri_poly, a3, n)
    area2 = np.bincount(tri_poly, a2, n)
    loop_total = np.empty(n, np.int64)
    me.polygons.foreach_get("loop_total", loop_total)
    loop_poly = np.repeat(np.arange(n), loop_total)  # loops are stored polygon by polygon
    tile = np.clip(np.floor(np.bincount(loop_poly, uv[:, 0], n) / loop_total).astype(np.int64), 0, len(TILES) - 1)
    mm = np.array([MM_PER_UV[t] for t in TILES])[tile]
    density = np.sqrt(area3 / np.maximum(area2, 1e-12)) * 1000.0
    value = np.where(area2 > 1e-12, np.clip(2.0 * np.log2(np.maximum(density, 1e-6) / mm), -2.0, 3.0), 0.0)
    value[tile == len(TILES) - 1] = 0.0
    weight = np.maximum(area3, 1e-12)[loop_poly]
    _, group = np.unique(loop_vert * len(TILES) + tile[loop_poly], return_inverse=True)
    for _ in range(TEXEL_SMOOTH):
        corner = np.bincount(group, weight * value[loop_poly]) / np.bincount(group, weight)
        value = np.bincount(loop_poly, corner[group], n) / loop_total
    corner = (np.bincount(group, weight * value[loop_poly]) / np.bincount(group, weight))[group]
    if TEXEL in me.attributes:
        me.attributes.remove(me.attributes[TEXEL])
    me.attributes.new(TEXEL, "FLOAT", "CORNER").data.foreach_set("value", corner.astype(np.float32))


def write_png(path, rgb: np.ndarray, depth: str = "8") -> None:
    """A PNG of the values as given - no colour transform: colour stays sRGB-encoded, data stays data - by OpenImageIO
    (Blender's own copy); `rgb` rows bottom first as Blender's pixels, PNG's top first."""
    import OpenImageIO as oiio

    h, w = rgb.shape[:2]
    spec = oiio.ImageSpec(w, h, rgb.shape[2], oiio.UINT8 if depth == "8" else oiio.UINT16)  # RGB, or RGBA packed
    out = oiio.ImageOutput.create(str(path))
    out.open(str(path), spec)
    out.write_image(np.ascontiguousarray(np.clip(rgb[::-1], 0.0, 1.0), dtype=np.float32))
    out.close()


def tiled_image(folder, stem: str) -> bpy.types.Image:
    """`<folder>/<stem>.<tile>.png` for every tile as one UDIM image, packed into the .blend."""
    from pathlib import Path

    folder = Path(folder)
    image = bpy.data.images.load(str(folder / f"{stem}.1001.png"), check_existing=False)
    image.source = "TILED"
    image.filepath = str(folder / f"{stem}.<UDIM>.png")
    for number in TILES[1:]:
        image.tiles.new(tile_number=number)
    image.reload()
    image.name = stem
    image.pack()
    return image


def _node(nt, kind: str, name: str, location=(0, 0)):
    node = nt.nodes.get(NODE + name) or nt.nodes.new(kind)
    node.name = node.label = NODE + name
    node.location = location
    return node


def pore_relief() -> tuple[bpy.types.Image, float]:
    """The pore tile (PORE_TOOL) - one for every skin, loaded once and shared - and its size on the skin in mm."""
    path = paths.generated("skin", "pores.png", tool=PORE_TOOL)
    size_mm = float(json.loads(path.with_suffix(".json").read_text(encoding="utf-8"))["size_mm"])
    image = bpy.data.images.load(str(path), check_existing=True)
    image.colorspace_settings.name = "Non-Color"
    return image, size_mm


def micro_relief() -> bpy.types.Image:
    """The generated microrelief tile (MICRO_TOOL), loaded once and shared by every skin."""
    path = paths.generated("skin", "microrelief.png", tool=MICRO_TOOL)
    image = bpy.data.images.load(str(path), check_existing=True)
    image.colorspace_settings.name = "Non-Color"
    return image


def nail_coords() -> np.ndarray:
    """Each vertex's nail coordinates over its fingertip (NAIL_TOOL; vertices x 4: along, (across + 1) / 2, digit / 10,
    1 inside a fingertip's region) on base v2 - hm08's vertices first, so an hm08 body reads its own part."""
    with np.load(paths.generated("skin", "nails.npz", tool=NAIL_TOOL)) as data:
        return data["coords"]


def add_hands_share(character: bpy.types.Object) -> None:
    """Each vertex's hands share as the point attribute HANDS_ATTR: the sum of its weights in the skeleton's hand and
    finger groups (HAND_BONES), up to 1 - 0 everywhere without a skeleton (the arms' tile's own levels then)."""
    me = character.data
    bones = {g.index for g in character.vertex_groups if g.name.startswith(HAND_BONES) and g.name[-2:] in ("_l", "_r")}
    share = np.zeros(len(me.vertices), np.float32)
    if bones:
        for v in me.vertices:
            share[v.index] = sum(g.weight for g in v.groups if g.group in bones)
    attr = me.attributes.get(HANDS_ATTR) or me.attributes.new(HANDS_ATTR, "FLOAT", "POINT")
    attr.data.foreach_set("value", np.clip(share, 0.0, 1.0))


def add_nail_coords(character: bpy.types.Object) -> None:
    """The nail coordinates on the character as its point attribute NAIL_ATTR (again: replaced)."""
    me = character.data
    coords = nail_coords()
    n = len(me.vertices)
    values = np.zeros((n, 4), np.float32)
    values[: min(n, len(coords))] = coords[:n]
    attr = me.attributes.get(NAIL_ATTR) or me.attributes.new(NAIL_ATTR, "FLOAT_COLOR", "POINT")
    attr.data.foreach_set("color", values.ravel())


def _math(nt, name: str, op: str, a, b=None, c=None):
    """A Math node fed by sockets or numbers; returns its output."""
    node = _node(nt, "ShaderNodeMath", name)
    node.operation = op
    for k, value in enumerate((a, b, c)):
        if value is None:
            continue
        if isinstance(value, (int, float)):
            node.inputs[k].default_value = value
        else:
            nt.links.new(value, node.inputs[k])
    return node.outputs["Value"]


def _clamp01(nt, name: str, value, scale: float):
    """min(max(value * scale, 0), 1): a soft edge `1 / scale` wide."""
    scaled = _math(nt, name, "MULTIPLY", value, scale)
    return _math(nt, name + "_c", "MINIMUM", _math(nt, name + "_p", "MAXIMUM", scaled, 0.0), 1.0)


def _mix(nt, name: str, kind: str, factor, a, b):
    """A Mix node (FLOAT or RGBA) of sockets or constants by `factor`; returns its result."""
    node = _node(nt, "ShaderNodeMix", name)
    node.data_type = kind
    suffix = "Float" if kind == "FLOAT" else "Color"
    if isinstance(factor, (int, float)):
        node.inputs["Factor"].default_value = factor
    else:
        nt.links.new(factor, node.inputs["Factor"])
    for ident, value in (("A_" + suffix, a), ("B_" + suffix, b)):
        socket = next(i for i in node.inputs if i.identifier == ident)
        if isinstance(value, tuple):
            socket.default_value = (*value, 1.0)
        elif isinstance(value, (int, float)):
            socket.default_value = value
        else:
            nt.links.new(value, socket)
    return next(o for o in node.outputs if o.identifier == "Result_" + suffix)


def _nail_layer(nt, bsdf) -> None:
    """The nail plate over each fingertip's skin (the NAIL_* constants; its coordinates the attribute NAIL_ATTR):
    colour, roughness, specular and coat mixed by the plate's mask; its edge raised and the skin's fold beside it by a
    bump at the end of the normal chain, over the skin's relief flattened under the plate."""

    def fed(name):
        return bsdf.inputs[name].links[0].from_socket

    coords = _node(nt, "ShaderNodeAttribute", "nail_coords", (-1600, -1600))
    coords.attribute_type, coords.attribute_name = "GEOMETRY", NAIL_ATTR
    parts = _node(nt, "ShaderNodeSeparateColor", "nail_parts", (-1350, -1600))
    nt.links.new(coords.outputs["Color"], parts.inputs["Color"])
    along = parts.outputs["Red"]
    digit = _math(nt, "nail_digit", "MULTIPLY", parts.outputs["Blue"], 10.0)
    across = _math(nt, "nail_across", "MULTIPLY_ADD", parts.outputs["Green"], 2.0, -1.0)
    across2 = _math(nt, "nail_across2", "MULTIPLY", across, across)
    inside = _math(nt, "nail_inside", "MULTIPLY", coords.outputs["Alpha"], 1.0)  # 0 off every fingertip
    # the plate: past the curved cuticle edge, inside the rounded sides - a toe's shorter and narrower (TOE_PLATE_*)
    toes = _math(nt, "nail_toes", "GREATER_THAN", digit, 5.5)
    length = _mix(nt, "nail_plate_length", "FLOAT", toes, NAIL_LENGTH, TOE_PLATE_LENGTH)
    side = _mix(nt, "nail_plate_side", "FLOAT", toes, NAIL_SIDE, TOE_PLATE_SIDE)
    cut = _math(nt, "nail_cut", "MULTIPLY_ADD", across2, NAIL_CUTICLE_CURVE, NAIL_CUTICLE)
    start = _clamp01(nt, "nail_start", _math(nt, "nail_past_cut", "SUBTRACT", along, cut), 1 / NAIL_EDGE_SOFT)
    sides = _clamp01(nt, "nail_sides", _math(nt, "nail_side_room", "SUBTRACT", side,
                                             _math(nt, "nail_abs", "ABSOLUTE", across)), 1 / NAIL_EDGE_SOFT)
    tip_cut = _math(nt, "nail_tip_cut", "MULTIPLY", _math(nt, "nail_tip_round", "MULTIPLY_ADD", across2,
                                                           -NAIL_TIP_CURVE, 1.0), length)
    before_tip = _math(nt, "nail_before_tip", "SUBTRACT", tip_cut, along)
    tip_room = _clamp01(nt, "nail_tip_room", before_tip, 1 / NAIL_EDGE_SOFT)
    plate = _math(nt, "nail_plate", "MULTIPLY", _math(nt, "nail_plate_a", "MULTIPLY",
                                                       _math(nt, "nail_plate_b", "MULTIPLY", start, sides), tip_room),
                  inside)  # fmt: skip
    # the lunula: a half-moon from the cuticle, as long as its digit's
    finger_len = _math(nt, "nail_len_f", "MULTIPLY_ADD", digit, -NAIL_LUNULA_FINGERS[1], NAIL_LUNULA_FINGERS[0])
    big_toe = _math(nt, "nail_big_toe", "COMPARE", digit, 6.0, 0.5)
    toe_len = _mix(nt, "nail_len_t", "FLOAT", big_toe, NAIL_LUNULA_TOES[1], NAIL_LUNULA_TOES[0])
    luna_len = _mix(nt, "nail_len", "FLOAT", toes, finger_len, toe_len)
    round_ = _math(nt, "nail_round", "SQRT", _math(nt, "nail_round_a", "MAXIMUM",
                                                    _math(nt, "nail_round_b", "SUBTRACT", 1.0, across2), 0.0))
    edge = _math(nt, "nail_lunula_edge", "MULTIPLY_ADD", luna_len, round_, cut)
    lunula = _clamp01(nt, "nail_lunula", _math(nt, "nail_lunula_d", "SUBTRACT", edge, along), 1 / 0.04)
    free_edge = _math(nt, "nail_free_edge", "MULTIPLY", length, NAIL_FREE_EDGE[0])  # the rim moves with the plate's end
    tip = _clamp01(nt, "nail_tip", _math(nt, "nail_tip_d", "SUBTRACT", along, free_edge),
                   1 / (NAIL_FREE_EDGE[1] - NAIL_FREE_EDGE[0]))
    # faint lengthwise ridges: noise stretched along the nail
    ridge_at = _node(nt, "ShaderNodeCombineXYZ", "nail_ridge_at", (-1100, -1900))
    nt.links.new(_math(nt, "nail_ridge_x", "MULTIPLY", across, 30.0), ridge_at.inputs["X"])
    nt.links.new(_math(nt, "nail_ridge_y", "MULTIPLY", along, 2.0), ridge_at.inputs["Y"])
    ridge = _node(nt, "ShaderNodeTexNoise", "nail_ridges", (-900, -1900))
    ridge.inputs["Scale"].default_value, ridge.inputs["Detail"].default_value = 1.0, 2.0
    nt.links.new(ridge_at.outputs["Vector"], ridge.inputs["Vector"])
    shade = _math(nt, "nail_ridge_shade", "MULTIPLY_ADD", ridge.outputs["Fac"], 2 * NAIL_RIDGES, 1.0 - NAIL_RIDGES)
    skin = fed("Base Color")
    bed = _mix(nt, "nail_bed", "RGBA", NAIL_BED_SHARE, skin, NAIL_BED)
    with_lunula = _mix(nt, "nail_with_lunula", "RGBA",
                       _math(nt, "nail_lunula_share", "MULTIPLY", lunula, NAIL_LUNULA_SHARE), bed, NAIL_LUNULA)
    with_tip = _mix(nt, "nail_with_tip", "RGBA", tip, with_lunula, NAIL_TIP)
    ridged = _node(nt, "ShaderNodeVectorMath", "nail_ridged", (-300, -1600))
    ridged.operation = "SCALE"
    nt.links.new(with_tip, ridged.inputs[0])
    nt.links.new(shade, ridged.inputs["Scale"])
    plated = _mix(nt, "nail_colour", "RGBA", plate, skin, ridged.outputs["Vector"])
    # the fold's groove: a darker band where the plate meets the skin (plate x (1 - plate) peaks at its edge)
    band = _math(nt, "nail_band", "MULTIPLY", plate, _math(nt, "nail_band_a", "SUBTRACT", 1.0, plate))
    groove = _node(nt, "ShaderNodeVectorMath", "nail_groove", (-100, -1600))
    groove.operation = "SCALE"
    nt.links.new(plated, groove.inputs[0])
    nt.links.new(_math(nt, "nail_groove_shade", "MULTIPLY_ADD", band, -4 * NAIL_GROOVE, 1.0), groove.inputs["Scale"])
    nt.links.new(groove.outputs["Vector"], bsdf.inputs["Base Color"])
    from . import material

    for name, value, key in (("Roughness", NAIL_ROUGHNESS, "rough"), ("Specular IOR Level", NAIL_SPECULAR, "spec"),
                             ("Coat Weight", NAIL_COAT, "coat")):
        own = fed(name) if bsdf.inputs[name].is_linked else bsdf.inputs[name].default_value
        if key == "rough":  # the skins paint MPFB2's nail region shinier (build_skins); on a fingertip the plain skin's
            own = _mix(nt, "nail_skin_rough", "FLOAT", coords.outputs["Alpha"], own, material.ROUGHNESS)
        nt.links.new(_mix(nt, f"nail_{key}", "FLOAT", plate, own, value), bsdf.inputs[name])
    # the skin's fold beside the plate: the plate drawn wider past its cuticle and sides (the same free edge), its band
    # raised over the plate's edge
    soft = 1.0 / NAIL_FOLD_SOFT
    fold_cut = _math(nt, "nail_fold_cut", "SUBTRACT", cut, NAIL_FOLD_REACH[0])
    start_w = _clamp01(nt, "nail_fold_start", _math(nt, "nail_fold_past", "SUBTRACT", along, fold_cut), soft)
    sides_w = _clamp01(nt, "nail_fold_sides", _math(nt, "nail_fold_room", "SUBTRACT",
                                                     _math(nt, "nail_fold_side", "ADD", side, NAIL_FOLD_REACH[1]),
                                                     _math(nt, "nail_abs", "ABSOLUTE", across)), soft)  # fmt: skip
    wide = _math(nt, "nail_wide", "MULTIPLY", _math(nt, "nail_wide_a", "MULTIPLY",
                                                     _math(nt, "nail_wide_b", "MULTIPLY", start_w, sides_w), tip_room),
                 inside)  # fmt: skip
    fold = _math(nt, "nail_fold", "MULTIPLY", _math(nt, "nail_fold_band", "SUBTRACT", wide, plate), NAIL_FOLD)
    # the skin's own relief (pores, microrelief, the scans') flat under the plate
    geometry = _node(nt, "ShaderNodeNewGeometry", "nail_geometry", (-300, -200))
    flat = _node(nt, "ShaderNodeMix", "nail_flat", (-150, -200))  # a VECTOR mix (`_mix` makes FLOAT / RGBA ones)
    flat.data_type = "VECTOR"
    nt.links.new(plate, flat.inputs["Factor"])
    nt.links.new(fed("Normal"), next(i for i in flat.inputs if i.identifier == "A_Vector"))
    nt.links.new(geometry.outputs["Normal"], next(i for i in flat.inputs if i.identifier == "B_Vector"))
    raise_ = _node(nt, "ShaderNodeBump", "nail_raise", (50, -200))
    raise_.inputs["Strength"].default_value, raise_.inputs["Distance"].default_value = 1.0, NAIL_RAISE
    nt.links.new(_math(nt, "nail_height", "ADD", plate, fold), raise_.inputs["Height"])
    nt.links.new(next(o for o in flat.outputs if o.identifier == "Result_Vector"), raise_.inputs["Normal"])
    nt.links.new(raise_.outputs["Normal"], bsdf.inputs["Normal"])


def _lip_layer(nt, bsdf) -> None:
    """The lips' vermilion: the colour scaled toward LIP_TINT by MPFB2's lips mask with its border softened (LIPS_TOOL),
    read through hm08's own UVs; smoother than the skin with a light coat (LIP_ROUGHNESS, LIP_COAT: a soft sheen, not
    a wet film)."""
    uvmap = _node(nt, "ShaderNodeUVMap", "lips_uv", (-1800, -2400))
    uvmap.uv_map = "UVMap"
    mask = _node(nt, "ShaderNodeTexImage", "lips_mask", (-1600, -2400))
    mask.image = bpy.data.images.load(str(paths.generated("skin", "lips_soft.png", tool=LIPS_TOOL)), check_existing=True)
    mask.image.colorspace_settings.name = "Non-Color"
    nt.links.new(uvmap.outputs["UV"], mask.inputs["Vector"])
    share = _math(nt, "lips_share", "MULTIPLY", mask.outputs["Color"], LIP_STRENGTH)
    tint = _mix(nt, "lips_tint", "RGBA", share, (1.0, 1.0, 1.0), LIP_TINT)
    tinted = _node(nt, "ShaderNodeVectorMath", "lips_colour", (-200, -2400))
    tinted.operation = "MULTIPLY"
    nt.links.new(bsdf.inputs["Base Color"].links[0].from_socket, tinted.inputs[0])
    nt.links.new(tint, tinted.inputs[1])
    nt.links.new(tinted.outputs["Vector"], bsdf.inputs["Base Color"])
    for name, value, key in (("Roughness", LIP_ROUGHNESS, "rough"), ("Coat Weight", LIP_COAT, "coat")):
        own = bsdf.inputs[name].links[0].from_socket if bsdf.inputs[name].is_linked else bsdf.inputs[name].default_value
        nt.links.new(_mix(nt, f"lips_{key}", "FLOAT", share, own, value), bsdf.inputs[name])
    period, depth, distortion, vary = LIP_LINES
    wave = _node(nt, "ShaderNodeTexWave", "lips_wave", (-1400, -2700))
    wave.wave_type, wave.bands_direction, wave.wave_profile = "BANDS", "Y", "SIN"
    wave.inputs["Scale"].default_value = LIP_MM_PER_V / period
    wave.inputs["Distortion"].default_value = distortion
    wave.inputs["Detail"].default_value, wave.inputs["Detail Scale"].default_value = LIP_LINES_DETAIL, 1.5
    nt.links.new(uvmap.outputs["UV"], wave.inputs["Vector"])
    noise = _node(nt, "ShaderNodeTexNoise", "lips_vary", (-1400, -2950))
    noise.inputs["Scale"].default_value = LIP_MM_PER_V / LIP_NOISE_MM
    noise.inputs["Detail"].default_value = 2.0
    nt.links.new(uvmap.outputs["UV"], noise.inputs["Vector"])
    gain = _math(nt, "lips_gain", "MULTIPLY_ADD", noise.outputs["Fac"], vary, 1.0 - vary)  # 1 - vary + vary x noise
    crease = _math(nt, "lips_crease", "POWER", wave.outputs["Fac"], LIP_CREASE)  # a thin valley on a plateau
    lines = _math(nt, "lips_lines_height", "MULTIPLY", _math(nt, "lips_varied", "MULTIPLY", crease, gain), share)
    bump = _node(nt, "ShaderNodeBump", "lips_lines", (-150, -2700))
    bump.inputs["Strength"].default_value, bump.inputs["Distance"].default_value = 1.0, depth
    nt.links.new(lines, bump.inputs["Height"])
    if bsdf.inputs["Normal"].is_linked:
        nt.links.new(bsdf.inputs["Normal"].links[0].from_socket, bump.inputs["Normal"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    _ear_layer(nt, bsdf, uvmap)


def _ear_layer(nt, bsdf, uvmap) -> None:
    """The ears' redness: the colour x EAR_TINT by MPFB2's ears mask, read through hm08's own UVs (the lips' UV node)."""
    mask = _node(nt, "ShaderNodeTexImage", "ears_mask", (-1600, -3200))
    mask.image = bpy.data.images.load(str(paths.makehuman("textures", "mpfb_ears.jpg")), check_existing=True)
    mask.image.colorspace_settings.name = "Non-Color"
    nt.links.new(uvmap.outputs["UV"], mask.inputs["Vector"])
    tint = _mix(nt, "ears_tint", "RGBA", mask.outputs["Color"], (1.0, 1.0, 1.0), EAR_TINT)
    tinted = _node(nt, "ShaderNodeVectorMath", "ears_colour", (-200, -3200))
    tinted.operation = "MULTIPLY"
    nt.links.new(bsdf.inputs["Base Color"].links[0].from_socket, tinted.inputs[0])
    nt.links.new(tint, tinted.inputs[1])
    nt.links.new(tinted.outputs["Vector"], bsdf.inputs["Base Color"])


def _relief_off_mouth(nt) -> None:
    """No pores on the lips (no follicles) or the wet lining, and no microrelief on the lining - they took the cheek's
    (the plan's §9, 2026-11-07): the relief's depth factors cut by MPFB2's lips mask and the lining's mask, after both
    layers are built."""
    nodes = nt.nodes
    lips = nodes[NODE + "lips_mask"].outputs["Color"]
    lining = nodes[NODE + "mouth_in"].outputs["Value"]  # the lining's mask, on the head tile only
    for key, masks in (("pore", (("lips", lips), ("lining", lining))), ("micro", (("lining", lining),))):
        depth = nodes[NODE + f"{key}_depth"]
        factor = depth.inputs[0].links[0].from_socket
        for name, mask in masks:
            keep = _math(nt, f"{key}_keep_{name}", "SUBTRACT", 1.0, mask)
            factor = _math(nt, f"{key}_off_{name}", "MULTIPLY", factor, keep)
        nt.links.new(factor, depth.inputs[0])


def stretched() -> bpy.types.Image:
    """The lids' stretched margins on the head tile (STRETCH_TOOL), loaded once and shared."""
    path = paths.generated("skin", "stretched.png", tool=STRETCH_TOOL)
    image = bpy.data.images.load(str(path), check_existing=True)
    image.colorspace_settings.name = "Non-Color"
    return image


def lid_blink() -> bpy.types.Image:
    """The upper lids' blink stretch on the head tile (LID_TOOL: the left eye's in red, the right's in green)."""
    path = paths.generated("skin", "lid_blink.png", tool=LID_TOOL)
    image = bpy.data.images.load(str(path), check_existing=True)
    image.colorspace_settings.name = "Non-Color"
    return image


def _closed_lid_share(nt, uv):
    """How closed each lid's skin is, 0-1: the mask's R x the left blink + G x the right (the object properties the
    face units' drivers keep - head/face_units.BLINK_PROPS), on the head tile; returns its socket."""
    from ..head import face_units

    mask = _node(nt, "ShaderNodeTexImage", "lid_mask", (-1600, -4400))
    mask.image, mask.interpolation, mask.extension = lid_blink(), "Linear", "CLIP"
    nt.links.new(uv.outputs["UV"], mask.inputs["Vector"])
    sep = _node(nt, "ShaderNodeSeparateColor", "lid_mask_rgb", (-1400, -4400))
    nt.links.new(mask.outputs["Color"], sep.inputs["Color"])
    total = None
    for (_key, prop), channel in zip(face_units.BLINK_PROPS, ("Red", "Green"), strict=True):
        attr = _node(nt, "ShaderNodeAttribute", f"lid_{prop}", (-1400, -4600 if channel == "Red" else -4700))
        attr.attribute_type, attr.attribute_name = "OBJECT", prop
        part = _math(nt, f"lid_{channel.lower()}", "MULTIPLY", sep.outputs[channel], attr.outputs["Fac"])
        total = part if total is None else _math(nt, "lid_both", "ADD", total, part)
    share = _math(nt, "lid_closed", "MULTIPLY", total, nt.nodes[NODE + "mouth_on_head"].outputs["Value"])
    nt.nodes[NODE + "lid_closed"].use_clamp = True
    return share


def _smile_wrinkles(nt, bsdf, uv) -> None:
    """The crow's feet (CROWS_TOOL) on the head tile, each side's grooves x its smile (the object properties the face
    units' drivers keep - head/face_units.SMILE_PROPS) as a bump at the end of the normal chain: nothing at rest."""
    from ..head import face_units

    image = bpy.data.images.load(str(paths.generated("skin", "crows_feet.png", tool=CROWS_TOOL)), check_existing=True)
    image.colorspace_settings.name = "Non-Color"
    tex = _node(nt, "ShaderNodeTexImage", "crows_map", (-1600, -5000))
    tex.image, tex.interpolation, tex.extension = image, "Cubic", "CLIP"
    nt.links.new(uv.outputs["UV"], tex.inputs["Vector"])
    sep = _node(nt, "ShaderNodeSeparateColor", "crows_rgb", (-1400, -5000))
    nt.links.new(tex.outputs["Color"], sep.inputs["Color"])
    total = None
    for (prop, _keys), channel in zip(face_units.SMILE_PROPS, ("Red", "Green"), strict=True):
        attr = _node(nt, "ShaderNodeAttribute", f"crows_{prop}", (-1400, -5200 if channel == "Red" else -5300))
        attr.attribute_type, attr.attribute_name = "OBJECT", prop
        groove = _math(nt, f"crows_{channel.lower()}_groove", "SUBTRACT", 1.0, sep.outputs[channel])
        part = _math(nt, f"crows_{channel.lower()}", "MULTIPLY", groove, attr.outputs["Fac"])
        total = part if total is None else _math(nt, "crows_both", "ADD", total, part)
    depth = _math(nt, "crows_depth", "MULTIPLY", total, nt.nodes[NODE + "mouth_on_head"].outputs["Value"])
    height = _math(nt, "crows_height", "SUBTRACT", 1.0, depth)
    bump = _node(nt, "ShaderNodeBump", "crows_bump", (-200, -5000))
    bump.inputs["Strength"].default_value, bump.inputs["Distance"].default_value = 1.0, CROWS_DEPTH
    nt.links.new(height, bump.inputs["Height"])
    if bsdf.inputs["Normal"].is_linked:
        nt.links.new(bsdf.inputs["Normal"].links[0].from_socket, bump.inputs["Normal"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])


def _soft_copy(image: bpy.types.Image) -> bpy.types.Image:
    """The colour's head tile at 1/LID_SOFT_SCALE (block means; a UDIM image's pixels are its first tile, 1001), made
    once a colour image and packed - a library load finds it by name."""
    name = f"{image.name} (soft)"
    soft = bpy.data.images.get(name)
    if soft is not None:
        return soft
    w, h = image.size
    px = np.empty(w * h * 4, np.float32)
    image.pixels.foreach_get(px)
    k = LID_SOFT_SCALE
    px = px.reshape(h, w, 4)[: h - h % k, : w - w % k]
    small = px.reshape(h // k, k, w // k, k, 4).mean((1, 3))
    soft = bpy.data.images.new(name, w // k, h // k, alpha=True)
    soft.colorspace_settings.name = image.colorspace_settings.name
    soft.pixels.foreach_set(small.astype(np.float32).ravel())
    soft.pack()
    return soft


def _closed_lid_skin(nt, bsdf, uv, share, colour: bpy.types.Image | None) -> None:
    """The closed lid's skin by `share`: the colour x soft / sharp (its streaks out, its tone kept) and the eyes'
    surround tint lifted; fine pits in object space at the end of the normal chain."""
    nodes, links = nt.nodes, nt.links
    final = bsdf.inputs["Base Color"].links[0].from_socket
    if colour is not None and colour.size[0] >= LID_SOFT_SCALE:
        sharp = nodes[NODE + "base_color"]
        soft = _node(nt, "ShaderNodeTexImage", "lid_soft", (-1600, -4900))
        soft.image, soft.interpolation, soft.extension = _soft_copy(colour), "Linear", "EXTEND"
        links.new(uv.outputs["UV"], soft.inputs["Vector"])
        ratio = _node(nt, "ShaderNodeVectorMath", "lid_ratio", (-1200, -4900))
        ratio.operation = "DIVIDE"
        links.new(soft.outputs["Color"], ratio.inputs[0])
        links.new(sharp.outputs["Color"], ratio.inputs[1])
        capped = _node(nt, "ShaderNodeVectorMath", "lid_ratio_capped", (-1000, -4900))
        capped.operation = "MINIMUM"
        links.new(ratio.outputs["Vector"], capped.inputs[0])
        capped.inputs[1].default_value = (3.0, 3.0, 3.0)
        smoothed = _node(nt, "ShaderNodeVectorMath", "lid_smoothed", (-800, -4900))
        smoothed.operation = "MULTIPLY"
        links.new(final, smoothed.inputs[0])
        links.new(capped.outputs["Vector"], smoothed.inputs[1])
        mixed = _node(nt, "ShaderNodeMix", "lid_colour", (-600, -4900))
        mixed.data_type = "RGBA"
        links.new(share, mixed.inputs["Factor"])
        links.new(final, next(i for i in mixed.inputs if i.identifier == "A_Color"))
        links.new(smoothed.outputs["Vector"], next(i for i in mixed.inputs if i.identifier == "B_Color"))
        final = next(o for o in mixed.outputs if o.identifier == "Result_Color")
    lift = _mix(nt, "lid_untint", "RGBA", share, (1.0, 1.0, 1.0), tuple(1.0 / c for c in EYE_SURROUND_TINT))
    lifted = _node(nt, "ShaderNodeVectorMath", "lid_lifted", (-400, -4900))
    lifted.operation = "MULTIPLY"
    links.new(final, lifted.inputs[0])
    links.new(lift, lifted.inputs[1])
    links.new(lifted.outputs["Vector"], bsdf.inputs["Base Color"])
    coords = _node(nt, "ShaderNodeTexCoord", "lid_coords", (-1600, -5200))
    cells = _node(nt, "ShaderNodeTexVoronoi", "lid_cells", (-1400, -5200))
    cells.feature = "F1"
    cells.inputs["Scale"].default_value = 1.0 / LID_PORE_CELL
    links.new(coords.outputs["Object"], cells.inputs["Vector"])
    grain = _node(nt, "ShaderNodeTexNoise", "lid_grain", (-1400, -5400))
    grain.inputs["Scale"].default_value, grain.inputs["Detail"].default_value = 1.0 / (2 * LID_PORE_CELL), 3.0
    links.new(coords.outputs["Object"], grain.inputs["Vector"])
    height = _math(nt, "lid_height", "MULTIPLY_ADD", cells.outputs["Distance"], 1.0, grain.outputs["Fac"])
    bump = _node(nt, "ShaderNodeBump", "lid_bump", (-200, -5200))
    bump.inputs["Strength"].default_value = 1.0
    links.new(_math(nt, "lid_depth", "MULTIPLY", share, LID_PORE_DEPTH), bump.inputs["Distance"])
    links.new(height, bump.inputs["Height"])
    links.new(bsdf.inputs["Normal"].links[0].from_socket, bump.inputs["Normal"])
    links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])


def _relief_off_stretched(nt, uv, closed=None) -> None:
    """No pores, microrelief or scanned relief on the lids' stretched margins (STRETCH_TOOL): the contact stretches them
    2-10x, which drew the relief out into streaks; a margin is smooth wet tissue. `closed` (the closed lid's share,
    `_closed_lid_share`): the same cut there, by the blink."""
    nodes = nt.nodes
    mask = _node(nt, "ShaderNodeTexImage", "stretched_mask", (-1600, -4100))
    mask.image, mask.interpolation, mask.extension = stretched(), "Linear", "CLIP"
    nt.links.new(uv.outputs["UV"], mask.inputs["Vector"])
    share = _math(nt, "stretched", "MULTIPLY", mask.outputs["Color"], nodes[NODE + "mouth_on_head"].outputs["Value"])
    if closed is not None:
        share = _math(nt, "stretched_or_closed", "MAXIMUM", share, closed)
    keep = _math(nt, "stretched_keep", "SUBTRACT", 1.0, share)
    for key in ("pore", "micro"):
        depth = nodes[NODE + f"{key}_depth"]
        factor = depth.inputs[0].links[0].from_socket
        nt.links.new(_math(nt, f"{key}_off_stretched", "MULTIPLY", factor, keep), depth.inputs[0])
    # the scans' relief at full strength (1; HAND_RELIEF on the hands, by their share) times the keep - numbers each
    # build, so a rebuild can't loop it into itself
    strength = _mix(nt, "relief_hands", "FLOAT", nodes[NODE + "hands_share"].outputs["Fac"], 1.0, HAND_RELIEF)
    cut = _math(nt, "relief_off_stretched", "MULTIPLY", strength, keep)
    nt.links.new(cut, nodes[NODE + "normal_map"].inputs["Strength"])


def _margin_layer(nt, bsdf) -> None:
    """The lid margin's wet pink (MARGIN_TINT, MARGIN_ROUGHNESS, MARGIN_COAT) by base v2's `js_margin` attribute (0
    off the margin, and on characters without it)."""
    from ..body import base

    attr = _node(nt, "ShaderNodeAttribute", "margin_attr", (-1800, -2700))
    attr.attribute_name = base.MARGIN_ATTR
    share = attr.outputs["Fac"]
    tint = _mix(nt, "margin_tint", "RGBA", share, (1.0, 1.0, 1.0), MARGIN_TINT)
    tinted = _node(nt, "ShaderNodeVectorMath", "margin_colour", (-150, -2700))
    tinted.operation = "MULTIPLY"
    nt.links.new(bsdf.inputs["Base Color"].links[0].from_socket, tinted.inputs[0])
    nt.links.new(tint, tinted.inputs[1])
    nt.links.new(tinted.outputs["Vector"], bsdf.inputs["Base Color"])
    for socket, value, key in (("Roughness", MARGIN_ROUGHNESS, "rough"), ("Coat Weight", MARGIN_COAT, "coat")):
        inp = bsdf.inputs[socket]
        own = inp.links[0].from_socket if inp.is_linked else inp.default_value
        nt.links.new(_mix(nt, f"margin_{key}", "FLOAT", share, own, value), inp)


def face_regions() -> bpy.types.Image:
    """The face's regions on the head tile (REGIONS_TOOL), loaded once and shared."""
    path = paths.generated("skin", "face_regions.png", tool=REGIONS_TOOL)
    image = bpy.data.images.load(str(path), check_existing=True)
    image.colorspace_settings.name = "Non-Color"
    return image


def face_eyes() -> bpy.types.Image:
    """The eyes region's share on the head tile (REGIONS_TOOL), loaded once and shared."""
    path = paths.generated("skin", "face_eyes.png", tool=REGIONS_TOOL)
    image = bpy.data.images.load(str(path), check_existing=True)
    image.colorspace_settings.name = "Non-Color"
    return image


def _eye_layer(nt, bsdf, uv) -> None:
    """The skin round the eyes x EYE_SURROUND_TINT by the eyes region's share, on the head tile (after the mouth's
    layers, before the lid margin's)."""
    nodes = nt.nodes
    mask = _node(nt, "ShaderNodeTexImage", "eyes_mask", (-1600, -3800))
    mask.image, mask.interpolation, mask.extension = face_eyes(), "Linear", "CLIP"
    nt.links.new(uv.outputs["UV"], mask.inputs["Vector"])
    share = _math(nt, "eyes_share", "MULTIPLY", mask.outputs["Color"], nodes[NODE + "mouth_on_head"].outputs["Value"])
    tint = _mix(nt, "eyes_tint", "RGBA", share, (1.0, 1.0, 1.0), EYE_SURROUND_TINT)
    tinted = _node(nt, "ShaderNodeVectorMath", "eyes_colour", (-150, -3800))
    tinted.operation = "MULTIPLY"
    nt.links.new(bsdf.inputs["Base Color"].links[0].from_socket, tinted.inputs[0])
    nt.links.new(tint, tinted.inputs[1])
    nt.links.new(tinted.outputs["Vector"], bsdf.inputs["Base Color"])


def face_share() -> bpy.types.Image:
    """The face's share on the head tile (REGIONS_TOOL; 0 on its neck, which is body skin), loaded once and shared - a
    map of its own: packed in the region map's alpha, the live view divided the region map's R, G, B by it."""
    path = paths.generated("skin", "face_share.png", tool=REGIONS_TOOL)
    image = bpy.data.images.load(str(path), check_existing=True)
    image.colorspace_settings.name = "Non-Color"
    return image


def _region_relief(nt, uv, which):
    """The relief's depth factors (pores, microrelief): the region map's on the head tile (R, B x
    REGION_RELIEF_SCALE), the microrelief ARM_MICRO on the arms' tile and HAND_PORES / HAND_MICRO on its hands (by
    HANDS_ATTR), 1 elsewhere (under a nail's plate the nail layer
    flattens them)."""
    regions = _node(nt, "ShaderNodeTexImage", "face_regions", (-1600, -2700))
    regions.image, regions.interpolation, regions.extension = face_regions(), "Linear", "EXTEND"
    nt.links.new(uv.outputs["UV"], regions.inputs["Vector"])
    parts = _node(nt, "ShaderNodeSeparateColor", "face_regions_split", (-1350, -2700))
    nt.links.new(regions.outputs["Color"], parts.inputs["Color"])
    on_head = _math(nt, "regions_on_head", "COMPARE", which.outputs["Value"], 0.0, 0.5)
    on_arms = _math(nt, "regions_on_arms", "COMPARE", which.outputs["Value"], float(ARM_TILE_INDEX), 0.5)
    hands = _node(nt, "ShaderNodeAttribute", "hands_share", (-1600, -3000))  # add_hands_share's (0 when missing)
    hands.attribute_type, hands.attribute_name = "GEOMETRY", HANDS_ATTR
    factors = []
    for channel, key in (("Red", "pore"), ("Blue", "micro")):
        head = _math(nt, f"regions_{key}", "MULTIPLY", parts.outputs[channel], REGION_RELIEF_SCALE)
        on_tile = _mix(nt, f"{key}_hands", "FLOAT", hands.outputs["Fac"], ARM_MICRO if key == "micro" else 1.0,
                       HAND_MICRO if key == "micro" else HAND_PORES)  # fmt: skip
        body = _mix(nt, f"{key}_on_arms", "FLOAT", on_arms, 1.0, on_tile)
        factors.append(_mix(nt, f"{key}_factor", "FLOAT", on_head, body, head))
    return factors


def mouth_mask() -> bpy.types.Image:
    """The mouth's lining on the head tile (MOUTH_TOOL), loaded once and shared."""
    path = paths.generated("skin", "mouth.png", tool=MOUTH_TOOL)
    image = bpy.data.images.load(str(path), check_existing=True)
    image.colorspace_settings.name = "Non-Color"
    return image


def mouth_seam() -> bpy.types.Image:
    """The band of the lips in front of the mouth's lining on the head tile (MOUTH_TOOL), loaded once and shared."""
    path = paths.generated("skin", "mouth_seam.png", tool=MOUTH_TOOL)
    image = bpy.data.images.load(str(path), check_existing=True)
    image.colorspace_settings.name = "Non-Color"
    return image


def _seam_layer(nt, bsdf, uv) -> None:
    """The lips x LIP_SEAM_TINT toward the closed mouth's line: the seam's band on the head tile, on the lips only
    (their share), after the mouth's lining."""
    nodes = nt.nodes
    mask = _node(nt, "ShaderNodeTexImage", "lips_seam_mask", (-1600, -3500))
    mask.image, mask.interpolation, mask.extension = mouth_seam(), "Linear", "CLIP"
    nt.links.new(uv.outputs["UV"], mask.inputs["Vector"])
    on_lips = _math(nt, "lips_seam_on", "MULTIPLY", nodes[NODE + "lips_share"].outputs["Value"],
                    nodes[NODE + "mouth_on_head"].outputs["Value"])  # fmt: skip
    band = _math(nt, "lips_seam_band", "MULTIPLY", mask.outputs["Color"], on_lips)
    share = _math(nt, "lips_seam_share", "MULTIPLY", band, LIP_SEAM_STRENGTH)
    tint = _mix(nt, "lips_seam_tint", "RGBA", share, (1.0, 1.0, 1.0), LIP_SEAM_TINT)
    tinted = _node(nt, "ShaderNodeVectorMath", "lips_seam_colour", (-150, -3500))
    tinted.operation = "MULTIPLY"
    nt.links.new(bsdf.inputs["Base Color"].links[0].from_socket, tinted.inputs[0])
    nt.links.new(tint, tinted.inputs[1])
    nt.links.new(tinted.outputs["Vector"], bsdf.inputs["Base Color"])


def lips_upper() -> bpy.types.Image:
    """The upper lip's share on the head tile (MOUTH_TOOL), loaded once and shared."""
    path = paths.generated("skin", "lips_upper.png", tool=MOUTH_TOOL)
    image = bpy.data.images.load(str(path), check_existing=True)
    image.colorspace_settings.name = "Non-Color"
    return image


def _upper_lip_layer(nt, bsdf, uv) -> None:
    """The upper lip x LIP_UPPER_TINT: its mask on the head tile, on the lips only (their share), after the seam."""
    nodes = nt.nodes
    mask = _node(nt, "ShaderNodeTexImage", "lips_upper_mask", (-1600, -4100))
    mask.image, mask.interpolation, mask.extension = lips_upper(), "Linear", "CLIP"
    nt.links.new(uv.outputs["UV"], mask.inputs["Vector"])
    on_lips = _math(nt, "lips_upper_on", "MULTIPLY", nodes[NODE + "lips_share"].outputs["Value"],
                    nodes[NODE + "mouth_on_head"].outputs["Value"])  # fmt: skip
    share = _math(nt, "lips_upper_share", "MULTIPLY", mask.outputs["Color"], on_lips)
    tint = _mix(nt, "lips_upper_tint", "RGBA", share, (1.0, 1.0, 1.0), LIP_UPPER_TINT)
    tinted = _node(nt, "ShaderNodeVectorMath", "lips_upper_colour", (-150, -4100))
    tinted.operation = "MULTIPLY"
    nt.links.new(bsdf.inputs["Base Color"].links[0].from_socket, tinted.inputs[0])
    nt.links.new(tint, tinted.inputs[1])
    nt.links.new(tinted.outputs["Vector"], bsdf.inputs["Base Color"])


def _mouth_layer(nt, bsdf, uv, which) -> None:
    """Wet mucosa over the skin where the mouth's mask is, on the head tile: colour, roughness, specular and coat."""

    def fed(name):
        return bsdf.inputs[name].links[0].from_socket

    mask = _node(nt, "ShaderNodeTexImage", "mouth_mask", (-1600, -2100))
    mask.image, mask.interpolation, mask.extension = mouth_mask(), "Linear", "CLIP"
    nt.links.new(uv.outputs["UV"], mask.inputs["Vector"])
    on_head = _math(nt, "mouth_on_head", "COMPARE", which.outputs["Value"], 0.0, 0.5)
    share = _math(nt, "mouth_share", "MULTIPLY", _math(nt, "mouth_in", "MULTIPLY", mask.outputs["Color"], on_head),
                  MOUTH_SHARE)
    nt.links.new(_mix(nt, "mouth_colour", "RGBA", share, fed("Base Color"), MOUTH_COLOUR), bsdf.inputs["Base Color"])
    for name, value, key in (("Roughness", MOUTH_ROUGHNESS, "rough"), ("Specular IOR Level", MOUTH_SPECULAR, "spec"),
                             ("Coat Weight", MOUTH_COAT, "coat")):
        own = fed(name) if bsdf.inputs[name].is_linked else bsdf.inputs[name].default_value
        nt.links.new(_mix(nt, f"mouth_{key}", "FLOAT", share, own, value), bsdf.inputs[name])


def _tiled_coords(nt, name: str, uv, which, tile_mm: float, location):
    """The UDIM layer's coordinates scaled so a tile of `tile_mm` millimetres keeps its size on every UDIM tile:
    x MM_PER_UV[tile] / tile_mm, the factor picked by the tile's index (`which`: floor(u), 0 = 1001)."""
    first = MM_PER_UV[TILES[0]] / tile_mm
    factor = _node(nt, "ShaderNodeValue", f"{name}_scale_1001", (location[0] - 400, location[1]))
    factor.outputs[0].default_value = first
    socket = factor.outputs[0]
    for k, number in enumerate(TILES[1:], start=1):
        step = MM_PER_UV[number] / tile_mm - MM_PER_UV[TILES[k - 1]] / tile_mm
        past = _node(nt, "ShaderNodeMath", f"{name}_past_{number}", (location[0] - 400, location[1] - 60 * k))
        past.operation, past.inputs[1].default_value = "GREATER_THAN", k - 0.5
        nt.links.new(which.outputs["Value"], past.inputs[0])
        add = _node(nt, "ShaderNodeMath", f"{name}_scale_{number}", (location[0] - 200, location[1] - 60 * k))
        add.operation = "MULTIPLY_ADD"
        nt.links.new(past.outputs["Value"], add.inputs[0])
        add.inputs[1].default_value = step
        nt.links.new(socket, add.inputs[2])
        socket = add.outputs["Value"]
    scaled = _node(nt, "ShaderNodeVectorMath", f"{name}_coords", location)
    scaled.operation = "SCALE"
    nt.links.new(uv.outputs["UV"], scaled.inputs[0])
    nt.links.new(socket, scaled.inputs["Scale"])
    return scaled.outputs["Vector"]


def _levels(nt, name: str, image, coords, texel, location):
    """`image` (a relief tile) at each of TEXEL_LEVELS' tilings of `coords` (x 2^(k/2), each level shifted so they
    don't line up), cross-faded by `texel` (hat weights: two levels at most), the blend's contrast kept - 0.5 + sum
    w (h - 0.5) / sqrt(sum w^2) (the variance-preserving blend of texture tiles). The level 0 node is `name` itself
    (as before); returns the blended height."""
    x, y = location
    t = _math(nt, f"{name}_texel_hi", "MINIMUM", _math(nt, f"{name}_texel_lo", "MAXIMUM", texel, float(TEXEL_LEVELS[0])),
              float(TEXEL_LEVELS[-1]))  # fmt: skip
    num = den = None
    for i, k in enumerate(TEXEL_LEVELS):
        tex = _node(nt, "ShaderNodeTexImage", name if k == 0 else f"{name}_level{k}", (x, y - 300 * i))
        tex.image, tex.interpolation = image, "Cubic"
        if k == 0:
            nt.links.new(coords, tex.inputs["Vector"])
        else:
            at = _node(nt, "ShaderNodeVectorMath", f"{name}_level{k}_coords", (x - 200, y - 300 * i))
            at.operation = "MULTIPLY_ADD"
            nt.links.new(coords, at.inputs[0])
            at.inputs[1].default_value = (2.0 ** (k / 2),) * 3
            at.inputs[2].default_value = (0.37 * k, 0.61 * k, 0.0)
            nt.links.new(at.outputs["Vector"], tex.inputs["Vector"])
        hat = _math(nt, f"{name}_w{k}_d", "ABSOLUTE", _math(nt, f"{name}_w{k}_s", "SUBTRACT", t, float(k)))
        w = _math(nt, f"{name}_w{k}", "MAXIMUM", _math(nt, f"{name}_w{k}_h", "SUBTRACT", 1.0, hat), 0.0)
        h = _math(nt, f"{name}_h{k}", "SUBTRACT", tex.outputs["Color"], 0.5)
        wh = _math(nt, f"{name}_wh{k}", "MULTIPLY", w, h)
        ww = _math(nt, f"{name}_ww{k}", "MULTIPLY", w, w)
        num = wh if num is None else _math(nt, f"{name}_num{k}", "ADD", num, wh)
        den = ww if den is None else _math(nt, f"{name}_den{k}", "ADD", den, ww)
    norm = _math(nt, f"{name}_norm", "SQRT", _math(nt, f"{name}_den_min", "MAXIMUM", den, 1e-6))
    return _math(nt, f"{name}_blend", "ADD", _math(nt, f"{name}_ratio", "DIVIDE", num, norm), 0.5)


def build_material(mat: bpy.types.Material, images: dict[str, bpy.types.Image], pores=None) -> None:
    """The skin's maps on its Principled BSDF (material.py made the BSDF and its scattering): `images` by channel,
    UDIM tiled; the pores from the shared tile (pore_relief - `pores`, a skin's own tile before 2026-11-06, is not
    used: every skin wears the clean one)."""
    from . import material

    nt = mat.node_tree
    bsdf = material.principled(mat)  # the film's; material.apply syncs the live view's after (sync_live)
    links = nt.links
    uv = _node(nt, "ShaderNodeUVMap", "uv", (-1400, 0))
    uv.uv_map = UV
    tex = {}
    for k, channel in enumerate(CHANNELS):
        node = _node(nt, "ShaderNodeTexImage", channel, (-1100, 300 - 280 * k))
        node.image = images[channel]
        node.image.colorspace_settings.name = COLOUR_SPACE.get(channel, "Non-Color")
        node.interpolation = "Cubic" if channel in ("normal", "height") else "Linear"
        links.new(uv.outputs["UV"], node.inputs["Vector"])
        tex[channel] = node
    gain = _node(nt, "ShaderNodeVectorMath", "gain", (-750, 300))
    gain.operation = "MULTIPLY"
    gain.inputs[1].default_value = (1.0, 1.0, 1.0)
    links.new(tex["base_color"].outputs["Color"], gain.inputs[0])
    # the body's mottling: where the UDIM layer's u is past the head tile (u >= 1)
    place = _node(nt, "ShaderNodeTexCoord", "place", (-1400, 600))
    noise = _node(nt, "ShaderNodeTexNoise", "mottle_noise", (-1200, 600))
    noise.inputs["Scale"].default_value, noise.inputs["Detail"].default_value = MOTTLE_SCALE, MOTTLE_DETAIL
    links.new(place.outputs["Object"], noise.inputs["Vector"])
    tile = _node(nt, "ShaderNodeSeparateXYZ", "tile", (-1200, 420))
    links.new(uv.outputs["UV"], tile.inputs["Vector"])
    body = _node(nt, "ShaderNodeMath", "body", (-1000, 420))
    body.operation, body.inputs[1].default_value = "GREATER_THAN", 0.999
    links.new(tile.outputs["X"], body.inputs[0])
    # the body's share: 1 on the body's tiles, and on the head tile 1 less the region map's face share (its neck is
    # body skin - make_face_regions: the coat and the mottle fade across it, no line at the tile's border)
    faces = _node(nt, "ShaderNodeTexImage", "face_share", (-1600, -3000))
    faces.image, faces.interpolation, faces.extension = face_share(), "Linear", "EXTEND"
    links.new(uv.outputs["UV"], faces.inputs["Vector"])
    for old in [lk for lk in nt.links if lk.from_node.name == NODE + "face_regions" and lk.from_socket.name == "Alpha"]:
        nt.links.remove(old)  # a skin built while the share was the region map's alpha
    share = _node(nt, "ShaderNodeMath", "body_share", (-800, 420))
    share.operation = "MAXIMUM"
    links.new(body.outputs["Value"], share.inputs[0])
    links.new(_math(nt, "face_share_less", "SUBTRACT", 1.0, faces.outputs["Color"]), share.inputs[1])
    swing = _node(nt, "ShaderNodeMapRange", "mottle_swing", (-1000, 600))
    swing.inputs["To Min"].default_value, swing.inputs["To Max"].default_value = 1.0 - MOTTLE / 2, 1.0 + MOTTLE / 2
    links.new(noise.outputs["Fac"], swing.inputs["Value"])
    on_body = _node(nt, "ShaderNodeMix", "mottle_on_body", (-800, 600))
    on_body.data_type = "FLOAT"
    links.new(share.outputs["Value"], on_body.inputs["Factor"])
    next(i for i in on_body.inputs if i.identifier == "A_Float").default_value = 1.0
    links.new(swing.outputs["Result"], next(i for i in on_body.inputs if i.identifier == "B_Float"))
    mottle = _node(nt, "ShaderNodeVectorMath", "mottle", (-600, 300))
    mottle.operation = "SCALE"
    links.new(gain.outputs["Vector"], mottle.inputs[0])
    links.new(next(o for o in on_body.outputs if o.identifier == "Result_Float"), mottle.inputs["Scale"])
    links.new(mottle.outputs["Vector"], bsdf.inputs["Base Color"])
    normal = _node(nt, "ShaderNodeNormalMap", "normal_map", (-750, 20))
    normal.space, normal.uv_map = "TANGENT", UV
    links.new(tex["normal"].outputs["Color"], normal.inputs["Color"])
    links.new(tex["roughness"].outputs["Color"], bsdf.inputs["Roughness"])
    spec = _node(nt, "ShaderNodeMath", "specular", (-750, -300))
    spec.operation, spec.inputs[1].default_value = "MULTIPLY", SPECULAR_FROM_CAVITY
    links.new(tex["cavity"].outputs["Color"], spec.inputs[0])
    links.new(spec.outputs["Value"], bsdf.inputs["Specular IOR Level"])  # x the pores' shine, below
    fine = _node(nt, "ShaderNodeBump", "height_bump", (-450, -100))
    fine.inputs["Strength"].default_value, fine.inputs["Distance"].default_value = HEIGHT_STRENGTH, HEIGHT_DISTANCE
    links.new(tex["height"].outputs["Color"], fine.inputs["Height"])
    links.new(normal.outputs["Normal"], fine.inputs["Normal"])
    # former routes in a skin saved before: the pores' on hm08's UVMap; the nails' island map and tile gates (until
    # 2026-11-10 - the coordinates are an attribute now: its node is another type under the same name)
    for old in ("body_uv", "pore_mapping", "nail_uv", "nail_on_tile", "regions_on_nails", "pore_off_nails",
                "micro_off_nails"):
        if nt.nodes.get(NODE + old) is not None:
            nt.nodes.remove(nt.nodes[NODE + old])
    if nt.nodes.get(NODE + "nail_coords") is not None and nt.nodes[NODE + "nail_coords"].type != "ATTRIBUTE":
        nt.nodes.remove(nt.nodes[NODE + "nail_coords"])
    # the relief layers on the UDIM layer, each tile scaled by its own millimetres per unit (MM_PER_UV)
    which = _node(nt, "ShaderNodeMath", "tile_index", (-1200, -700))
    which.operation = "FLOOR"
    links.new(tile.outputs["X"], which.inputs[0])
    texel = _node(nt, "ShaderNodeAttribute", "texel", (-1600, -1000))  # add_texel's density (0 when missing)
    texel.attribute_type, texel.attribute_name = "GEOMETRY", TEXEL
    pore_image, pore_mm = pore_relief()
    pore_height = _levels(nt, "pores", pore_image, _tiled_coords(nt, "pore", uv, which, pore_mm, (-1200, -900)),
                          texel.outputs["Fac"], (-1000, -900))  # fmt: skip
    bump = _node(nt, "ShaderNodeBump", "pore_bump", (-250, -200))
    bump.inputs["Strength"].default_value = PORE_STRENGTH
    pore_factor, micro_factor = _region_relief(nt, uv, which)
    links.new(_math(nt, "pore_depth", "MULTIPLY", pore_factor, PORE_DISTANCE), bump.inputs["Distance"])
    links.new(pore_height, bump.inputs["Height"])
    links.new(fine.outputs["Normal"], bump.inputs["Normal"])
    micro_height = _levels(nt, "micro", micro_relief(),
                           _tiled_coords(nt, "micro", uv, which, MICRO_TILE_MM, (-1200, -2200)), texel.outputs["Fac"],
                           (-1000, -2200))  # fmt: skip
    micro_bump = _node(nt, "ShaderNodeBump", "micro_bump", (-100, -200))
    micro_bump.inputs["Strength"].default_value = MICRO_STRENGTH
    links.new(_math(nt, "micro_depth", "MULTIPLY", micro_factor, MICRO_DISTANCE), micro_bump.inputs["Distance"])
    links.new(micro_height, micro_bump.inputs["Height"])
    links.new(bump.outputs["Normal"], micro_bump.inputs["Normal"])
    links.new(micro_bump.outputs["Normal"], bsdf.inputs["Normal"])
    shine = _math(nt, "pore_specular", "MULTIPLY", spec.outputs["Value"],
                  _math(nt, "pore_shine", "MULTIPLY_ADD", pore_height, PORE_SHINE[1], PORE_SHINE[0]))
    # the oiliness slider scales the whole chain (1 at its default 0.5): its value under the link did nothing on a
    # mapped skin (the plan's §10 fix list, 2026-11-07)
    links.new(_math(nt, "oiliness", "MULTIPLY", shine, mat.juststage.oiliness / OILINESS_DEFAULT),
              bsdf.inputs["Specular IOR Level"])
    # the base coat first, the wet layers over it (linked after them, it replaced the nails' and the mouth's coat)
    coat = _node(nt, "ShaderNodeMix", "coat", (-450, 500))
    coat.data_type = "FLOAT"
    links.new(share.outputs["Value"], coat.inputs["Factor"])
    next(i for i in coat.inputs if i.identifier == "A_Float").default_value = COAT_WEIGHT
    next(i for i in coat.inputs if i.identifier == "B_Float").default_value = BODY_COAT_WEIGHT
    links.new(next(o for o in coat.outputs if o.identifier == "Result_Float"), bsdf.inputs["Coat Weight"])
    _nail_layer(nt, bsdf)
    _lip_layer(nt, bsdf)
    _mouth_layer(nt, bsdf, uv, which)
    _seam_layer(nt, bsdf, uv)
    _upper_lip_layer(nt, bsdf, uv)
    _eye_layer(nt, bsdf, uv)
    closed = _closed_lid_share(nt, uv)
    _closed_lid_skin(nt, bsdf, uv, closed, images.get("base_color"))
    _relief_off_mouth(nt)
    _relief_off_stretched(nt, uv, closed)
    bsdf.inputs["Coat Roughness"].default_value = COAT_ROUGHNESS
    bsdf.inputs["Coat IOR"].default_value = COAT_IOR
    bsdf.inputs["Sheen Weight"].default_value = SHEEN_WEIGHT
    bsdf.inputs["Sheen Roughness"].default_value = SHEEN_ROUGHNESS
    _margin_layer(nt, bsdf)  # last: over the colour, roughness and coat the layers above set
    _smile_wrinkles(nt, bsdf, uv)
    # the coat on the skin's final bumped normal, as the base's (the nails', lips' and upper lip's layers relink
    # Normal above): HD Aaron's head BSDF feeds both from one normal (CC Blender Tools' rl_head_shader, read
    # 2026-11-10); unlinked, our oil lobe shone off a smooth surface and the relief's bumps never glinted
    links.new(bsdf.inputs["Normal"].links[0].from_socket, bsdf.inputs["Coat Normal"])
    mat.juststage.has_maps = True


def refresh(mat: bpy.types.Material) -> None:
    """A mapped skin's shading set again from this code (its maps kept): a skin or a character from the library wears
    today's settings, not the ones it was saved with."""
    nodes = mat.node_tree.nodes
    images = {c: nodes[NODE + c].image for c in CHANNELS}
    build_material(mat, images)
    for obj in bpy.data.objects:  # the characters wearing it get the density the relief layers read (add_texel)
        if obj.type == "MESH" and obj.juststage.kind == "HUMAN" and mat.name in obj.data.materials:
            if TEXEL not in obj.data.attributes:
                add_texel(obj)
            from ..head import face_units

            face_units.add_blink_props(obj)  # the closed lid's blink values (none without the keys; once)
            face_units.add_smile_props(obj)  # the crow's feet's smile values (likewise)
            if NAIL_ATTR not in obj.data.attributes:  # the nails' coordinates (a character saved before 2026-11-10)
                add_nail_coords(obj)
            add_hands_share(obj)  # the hands' share, again: the skeleton may have come after the skin
            bed = obj.modifiers.get("JustStage nail bed")  # its geometric bed on the tile's island, replaced that day
            if bed is not None:
                obj.modifiers.remove(bed)


def set_pores(mat: bpy.types.Material, character: bpy.types.Object) -> None:
    """The pores' depth on a mapped skin for its character's sex (PORES_BY_SEX by the gender macro)."""
    node = mat.node_tree.nodes.get(NODE + "pore_depth")
    if node is not None:
        node.inputs[1].default_value = PORE_DISTANCE * float(np.interp(character.juststage.gender, (0.0, 1.0),
                                                                       PORES_BY_SEX))  # fmt: skip


def ear_tint(melanin: float, eumelanin: float, blood: float) -> tuple[float, float, float]:
    """EAR_TINT at this tone: its pull from 1 scaled by how visible extra blood is here (EAR_TINT_MELANIN, EAR_BLOOD)."""
    from ...core import skin_optics

    tables = skin_optics.load_tables(paths.FETCHED / "optics")

    def green_drop(m):
        own = skin_optics.Skin(m, eumelanin, blood).linear_rgb(tables)[1]
        return 1.0 - skin_optics.Skin(m, eumelanin, blood * EAR_BLOOD).linear_rgb(tables)[1] / own

    # never past the judged tint on lighter skin: its hue (blue down more than green) is orange, not blood's
    seen = min(max(green_drop(melanin) / green_drop(EAR_TINT_MELANIN), 0.0), 1.0)
    return tuple(1.0 - (1.0 - c) * seen for c in EAR_TINT)


def set_ear_tint(mat: bpy.types.Material) -> None:
    """The ears' tint on a mapped skin for its tone (ear_tint, from the material's own record)."""
    node = mat.node_tree.nodes.get(NODE + "ears_tint")
    if node is not None:
        record = mat.juststage
        tint = ear_tint(record.melanin, record.eumelanin, record.blood)
        next(i for i in node.inputs if i.identifier == "B_Color").default_value = (*tint, 1.0)


def set_oiliness(mat: bpy.types.Material, oiliness: float) -> None:
    """The oiliness slider on a mapped skin: the factor on its specular chain, oiliness / OILINESS_DEFAULT."""
    node = mat.node_tree.nodes.get(NODE + "oiliness")
    if node is not None:
        node.inputs[1].default_value = oiliness / OILINESS_DEFAULT


def set_gain(mat: bpy.types.Material, rgb: tuple[float, float, float]) -> None:
    """The character's tone over the skin's own: `rgb` is the tone's linear colour (skin_optics)."""
    from ...core import skin_optics

    record = mat.juststage
    tables = skin_optics.load_tables(paths.FETCHED / "optics")
    own = skin_optics.Skin(record.map_melanin, record.map_eumelanin, record.map_blood).linear_rgb(tables)
    gain = tuple(float(t / o) for t, o in zip(rgb, own, strict=True))
    mat.node_tree.nodes[NODE + "gain"].inputs[1].default_value = gain


def apply(character: bpy.types.Object, skin: bpy.types.Material) -> bpy.types.Material:
    """A mapped skin on the character: a copy of `skin` (each character its own), in the place of its skin material,
    in the character's own tone."""
    from . import skin_set_tone

    add_layout(character)
    add_texel(character)
    add_nail_coords(character)  # each nail's coordinates over its fingertip, for the nail layer
    add_hands_share(character)  # the hands' share of the arms' tile, for their own tiled relief
    old = character.juststage.skin_material
    mine = skin.copy()
    mine.name = f"JustStage Skin ({character.name})"
    mine.use_fake_user = False
    refresh(mine)
    slots = character.data.materials
    if old is not None and old.name in slots:
        slots[slots.find(old.name)] = mine
    else:
        slots.append(mine)
    character.juststage.skin_material = mine
    if old is not None and old.users == 0:
        bpy.data.materials.remove(old)
    props = character.juststage
    skin_set_tone.main(
        skin_set_tone.Params(props.character_id, props.melanin, props.eumelanin, props.blood, props.oiliness)
    )
    return mine

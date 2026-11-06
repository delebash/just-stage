# The character, redesigned — every piece, verified (DRAFT, in progress 2026-11-05)

The user, 2026-11-05 (TASKS "THE BASE MESH FIRST; THE WHOLE CHARACTER REDESIGNED"): "really think on the design and make
sure you have it correct and ll the pieces correct, think adverserially multiple times on this desing of the charctaer
and how the pieices fit from mesh to texture to hair to slider to everything"; "please get this correct this time ...
verifying it multple time that it is the correct path". The aim: better than CC5 and MetaHuman, part by part
(`2026-11-05-base-mesh-first.md`, "the best of both").

**How this document is verified before it reaches the user:** every fact marked [page] / [code] / [measured] at its
source, anything else marked unverified; each research agent's file audited (query log, evidence marks, search
mistakes a-n) and its key claims spot-checked; the design attacked in passes - (1) each piece, (2) how the pieces fit,
(3) my own claims, (4) the tests that would catch a mistake, (5) the untouched neighbours - until a fresh pass finds
nothing; each risky choice proved by a small measured test before adoption.

## Facts established today (measured unless marked)

- **Density is not the gap.** CC5's HD Aaron (SubD 1 export, 56,412 body vertices) and hm08 at level 1 (53,514) are
  about equally dense round the eye, mouth, ear, hand, foot and torso (`.dev/gate/parts/audit/sheet_*.png`). CC5's base:
  17,683 polygons at SubD 0 [page, CC5 spec table]; hm08: 14,766 faces.
- **The lids are where hm08's topology fails.** Real scanned faces wrapped onto hm08 (20 fits, visible surface only):
  within ~2 mm (p90) at nose, mouth, cheeks, forehead; ears 4.4 mm; **the lid ring 14.7 mm**
  (`2026-11-05-research-base-mesh.md` §6). CC5 models the lid as a thick flap with a margin and a ledge round a recessed
  eyeball; hm08's lid edge is one ring standing up to 3.3 mm off the eyeball.
- **Elsewhere the gaps are sculpted shape and detail, not topology:** hands (knuckles, tendons, nail beds), feet (toe
  pads, nail beds), torso definition (audit sheet 2).
- **Blender Studio's CC0 realistic head models the lid margin (2-3 loops) and an inner-corner pocket** [measured render].
- **The live view keeps the film render's detail on our skin** (EEVEE 113-117% of Cycles' fine/pore/fold bands with the
  calibrated scattering) - the renderer is not the limit (RESEARCH, rec 1).
- **The proven pieces:** face skin from scans (cheek pore band equal to Aaron's on six characters); eye white, iris
  (photo), pupil and the lower-lid wet margin equal by measure on one character and holding on five; the Artec scan
  carries real torso definition (form band 3.12 vs ours 2.27, Aaron 4.34).

## The pieces (each: CC5's way, MetaHuman's way, ours, the best, its standard, its attack)

1. Base mesh and anatomy - awaiting `2026-11-05-research-base-mesh-2.md` (topology transfer, topology best practice,
   other bases, UV seams).
2. Parts (eyes, eye layers incl. caruncle, teeth, gums, tongue, lashes, brows).
3. UV layout and texel density - awaiting the same file (seams).
4. Shape spaces and sliders; character mixing - awaiting `2026-11-05-research-mixing-hair.md`.
5. HD detail (definition, sculpt-level) - spec §1.4.
6. Face rig, expressions, wrinkles - awaiting `2026-11-05-research-face-animation.md`.
7. Body rig and correctives - awaiting the same.
8. Skin (master texture set, layers, scans, micro detail, tone).
9. Hair (scalp, facial, body; strands, cards; shading) - awaiting the mixing-hair file.
10. Materials and the two renderers (EEVEE live, Cycles film).
11. Live-view budget (8 GB card), LODs, export.

## Research files audited (2026-11-05)

- `2026-11-05-research-face-animation.md` (agent): 36 queries logged; 28 [page], 20 [code]/[measured], 11 [snippet]
  marks; the a-n check written in. Spot-checked by me: FACSHuman's licence LGPL-3.0, last push 2026-04-18 (GitHub API);
  CC5's wrinkle set `HD Aaron 2K.rlWrinkle` on disk under `F:\Reallusion Content\Reallusion Templates\Actor\Expression
  Wrinkles\CC5 2K\`. Usable.
- `2026-11-05-research-base-mesh-2.md` (agent): 39 queries logged; 46 [page], 14 [code], 6 [file], 18 [snippet], 6
  [inferred]. Spot-checked by me: CharMorph's binding is `kd.find_n(v, 16)` nearest hm08 vertices plus nearest-face
  points (`lib/fit_calc.py`) - an averaging map, as the file says. Usable.

What they change: (1) the append (option A) ranks first and is the industry's own move (Maya's "Bake Topology To
Targets"); switching topology (B, D) loses at the lids, where no hm08 surface exists to transfer from; Blender's CC0
head is coarser at level 0 (3,242 v) than hm08's head (4,986). (2) Two conditions on A: each appended vertex keeps its
offset in its birth face's local frame (turns with the face; plain averaging puts a margin vertex ~1 mm wrong in a
blink - the file's arithmetic), and every closing expression gets a contact step (lids meet, lips seal). (3) A second
expression source on hm08 itself: FACSHuman's 133 FACS action units (LGPL-3.0); the expression sets are to be scored
against real expression scans, not picked. (4) Wrinkles: no shippable scanned library exists; mesh tension (MIT) drives
RigLogic's wrinkle maps. (5) Body correctives: SOMA-X (Apache-2.0) has one learned model reaching MakeHuman's mesh
through Anny's SOMA topology.

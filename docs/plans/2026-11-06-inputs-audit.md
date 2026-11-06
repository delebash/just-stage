# The inputs audit - every piece of our character against how CC5 makes it (2026-11-06)

Why (TASKS "THE INPUTS FIRST"): our lashes looked painted on - the skins carried the scanned or painted people's own
hair - and ~5 hours of proofs (2026-11-05) were measured on them. The user: "check again if you are doing things wrong
like this"; "just verify there is nothing else you are doing wrong it should be like cc5".

**How checked:** CC5's side from HD Aaron's own files on disk (`.dev/gate/cc5_aaron_blender/` - the FBX's `.fbm`
maps, CC Blender Tools' `textures/aron_with_hair/<object>/<material>/` extras, the object list); ours from the code
(`modules/`), the library's skin files (`.dev/skins/<name>/<name> skin.<channel>.<tile>.png`) and contact sheets made
for this audit (scratchpad `skins_sheet.py`: every skin's head tile, colour and normal, side by side). [file] = read
or viewed on disk; [code] = read in our code.

## CC5's character, as HD Aaron is made [file]

Objects: `CC_Base_Body` (one mesh; materials head, body, arm, leg, nails, eyelash base), `Eyelash_Up` and
`Eyelash_Low` (lash card meshes), `Brows` (three card layers: `Brows_Base`, `Brows_Color`, `Brows_Hair`), `Stubble`
(a hair card shell), `Classic_Slick_Back` (hair cards), `CC_Base_Eye` (eyes, corneas), `CC_Base_EyeOcclusion`,
`CC_Base_TearLine`, `CC_Base_Teeth`, `CC_Base_Tongue`. Skin maps per region (head / body / arm / leg): diffuse,
normal, roughness, ambient occlusion (its own map), cavity, subsurface map, transmission map, micro-normal mask,
specular mask, region masks (`RGBAMask`, `CFULCMask`, `ENMask`, `MNAOMask`, `NMUILMask`), a blend mask; the head also
three wrinkle sets (diffuse, normal, roughness, flow). His head diffuse: no lashes, no brows, no shading - only a faint
grey shaved tint on the jaw and lip under the Stubble mesh. His body diffuse: real skin variation, areolas, navel; his
body normal: sculpted pecs, abs, ribs, collarbones and fine skin texture.

## Ours against it

| # | Piece | Ours (source) | CC5's way | Verdict | Fix |
|---|---|---|---|---|---|
| 1 | Lashes | strand curves, 150 + 80 per eye, 0.1 mm thick (`hair/lashes.py`) - sub-pixel at face distance, EEVEE draws them at zero width [code, render] | card meshes (`Eyelash_Up`, `Eyelash_Low`) that read at any distance | **WRONG** (invisible; the spec's own `eyelash.L/R` card part, §1.1, was never built) | lash cards made from our strands (the spec's part), or a minimum strand width - whichever measures closer to Aaron's lash line |
| 2 | Lashes in the skin | painted along both lids on Daniel, Mei, Walter (face-test AI paintings) [file] | none | **WRONG** | out of every skin |
| 3 | Brows | strand curves (`hair/brows.py`) over brows painted in some skins [file] | three card layers: a soft base layer, a colour layer, hair cards - all mesh | **WRONG** (paint underneath; strands thin at distance) | brows out of the skins; a base layer as geometry like CC5's under our strands; visible at distance |
| 4 | Stubble, beard | painted in Scan man A, B, C's colour (C's whole lower face) and in their relief (lumps along the beard's edge) [file]; no stubble groom | a `Stubble` mesh over a faint shaved tint | **WRONG** | out of the skins (a faint shaved tint kept for men, as Aaron's); a stubble groom |
| 5 | Shading in the colour | Daniel, Mei, Walter: the face's light painted in (nose shadow, socket shading - the AI paintings) [file] | flat colour; AO its own map | **WRONG** | these three (and Amara, same source) no longer the defaults (files kept); skins from the scan composer, which delights (an SH fit) |
| 6 | Wrinkles in the colour | Walter: drawn wrinkle lines [file] | wrinkles in the normal map and the three wrinkle sets | **WRONG** | as 5 |
| 7 | Face patch edges | Scan woman A, B, C: the composed face patch's outline shows in the colour [file] | one continuous map | **WRONG** | the composer's border blend (piece 4's seam rule) |
| 8 | Relief (normal) from scans | the scans' geometry baked - hairline, beard edge, stray strands and scan debris on all six scan skins [file] | sculpted, clean | **WRONG** | the hair and debris regions masked out of the relief bake |
| 9 | Pore tile | `pores_lps.png` on every character, women too: seams at its quarter lines, elongated streaks like the scanned man's stubble [file; the stubble to confirm against the scan] | a clean, tiling micro normal (Texturing.XYZ's) with a region mask | **WRONG** | a seamless, hairless pore tile (from the clean areas, or rec 18's relief tiles) |
| 10 | Body skin | tiles 1002-1004: one flat colour, two dots for nipples, a flat normal map [file] | full skin variation, areolas, navel; a normal map with the body's definition and texture | **WRONG** | body colour and relief from bare-body scans (Artec's torso fitted and baked - proof step 2's route) with the same hair and seam rules |
| 11 | Subsurface and transmission | one value over the whole body (`skin/material.py`) [code] | a subsurface map and a transmission map (ears, nostrils, lids glow) | **MISSING** | maps per region from thickness (a bake of the mesh's thickness) |
| 12 | Region masks | `face_regions.png` (forehead / cheek micro and pores) [code] | five region masks for micro normal, roughness, specular, AO | partly | extend ours to CC5's regions |
| 13 | Teeth, gums, tongue | flat colours, "starting values ... not measurements" (`head/part_materials.py`) [code] | diffuse and normal maps | **WRONG** | the design's piece 3: Poseidon3D shapes, MIO photos (CC BY 4.0) as maps |
| 14 | Iris | MPFB2's procedural iris in code; the photo iris measured equal only in a scratchpad harness [code] | an iris texture | **NOT IN CODE** | the photo iris into `head/eyes.py` (step 5) |
| 15 | Nipples | two painted dots on the flat body | areola colour and relief in the maps | **WRONG** | with 10 |
| 16 | Expression wrinkles | none (step 3) | three wrinkle sets | MISSING, planned | step 3 |
| 17 | Scalp hair | strands (`hair/scalp.py`) | cards | a design choice (piece 9: strands master, cards for far views) - its visibility at distance has the same width problem as 1 | the live view's minimum width; cards baked for far views |
| 18 | The gate's comparison | Aaron wears his Stubble mesh; ours no stubble groom | - | **UNFAIR** | the stubble groom (4), or both without |

Stand (checked): the eyes' white, iris photo, pupil (measured inside the opening); the lid geometry and its tests; the
live view's calibration; the stage and lights (the same for both); the lips' colour by MakeHuman's lips mask (a mask,
no hair); the nails' generated plate.

## What it changes

The proofs measured on rows 1-10 are void (RESEARCH "Painted hair in our inputs"). Before any further measurement:
fix the inputs, in this order - (a) the skins (rows 2, 4-9: hair, shading, patches, relief, pore tile) with a check
that fails any skin with hair or shading baked in; (b) facial hair as geometry that reads at distance (1, 3, 4, 17);
(c) the body skin (10, 15); (d) the parts' maps (13, 14); (e) subsurface, transmission and region masks (11, 12). Then
re-run the proofs on clean inputs, each proof's log opening with its inputs table (memory
`audit-inputs-before-measuring`).

## Status (2026-11-06, as fixed - each in its commit)

| # | Status |
|---|---|
| 1 | Lashes stay strands (design piece 9); their reading at face distance is MEASURED at the gate (on / off) before the coverage width or cards |
| 2, 4, 5-8 | FIXED in the scan composer (`tools/face_test/skin_base.py` with `hair.py`): the lash and brow band out, strands found and filled, stubble found per texel and left out, holes filled with real skin (mirror fill) and smooth colour (no patch edges); the AI-painted skins (Daniel, Mei, Amara, Walter) no longer defaults or the library characters' skins - files kept |
| 4 (hair) | FIXED: `hair/stubble.py` - stubble as hair; the gate's man wears it as Aaron wears CC5's |
| 9 | FIXED: Ten24's scanned cheek relief, seamless (`pore_tile.py`), shared by every skin (`maps.pore_relief`) |
| 10, 15 | OPEN: the body's own colour and relief (Artec's bare torso through the face's scan route) |
| 11 | HANDLED physically: Cycles' random-walk scattering carries light through thin parts; EEVEE reads the thickness from its shadow maps (`material.py`: ears and nostrils glow) - a map only if the gate's ear view shows a gap |
| 12 | OPEN: region masks beyond the face's (forehead, cheek) |
| 13 | FIXED (first pass): teeth and gums shaded as the MIO photo shows them (`part_materials.py`); real arches (Poseidon3D) still open |
| 14 | FIXED: the photo iris in code (`tools/make_iris.py`, `eyes.shade`) |
| 16 | step 3 (expressions) |
| 17 | with 1 |
| 18 | FIXED: stubble on the gate's man |

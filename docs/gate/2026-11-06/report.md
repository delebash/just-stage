# The part-by-part gate on clean inputs (2026-11-06)

The 2026-11-05 gate's proofs were measured on skins with painted hair (TASKS "THE INPUTS FIRST"); this run is the
first on inputs checked against CC5's way (`../../plans/2026-11-06-inputs-audit.md`). Same stage, cameras and views as
`../2026-11-05/report.md` (`tools/gate/parts_gate.py`); HD Aaron's renders are that day's (his inputs unchanged).

## Inputs (memory `audit-inputs-before-measuring`: every input, its source, CC5's way, how checked)

| Input | Ours, this run | CC5's way (HD Aaron) | Checked |
|---|---|---|---|
| Character | the library's Average man on base v2 (lid margin, contact key), eyes opened (EYE_OPEN) | HD Aaron, SubD 1 | `base.upgrade`, tests |
| Skin colour, head | Scan man A (compositions 611: HSR0040 + LPS), hair out (band, strands, stubble per texel), faint shaved tint | hairless diffuse, faint shaved tint | contact sheets of the head tile, crops at the eyes |
| Skin colour, torso | Artec's torso detail (colour ratio, its areolas), our tone | full body diffuse | `tools/body_scan.py` preview |
| Skin relief | the scans' relief (stubble lumps out), Artec's torso relief, Ten24's pore tile, the generated microrelief | normal maps + micro normal | tile previews |
| Lashes | strands from base v2's lash line (150 + 80 an eye) | lash cards | `lashes.py`, tests |
| Brows | strands, 800 a brow, no paint under them | three card layers | the head tile's brow area |
| Stubble | strands (`hair/stubble.py`, ~24k, 1.5 mm) | Stubble mesh | test |
| Scalp hair | JustStage short combed (strands) | Classic Slick Back (cards) | - |
| Eyes | GNM eyes, the photo iris in code (pupil 0.45, white x0.71), ICT's films | CC5's eye | tests |
| Teeth | GNM, shaded from the MIO photo's ratios, wet | textured teeth | test |
| Light | the app's stage (key, rim, Studio Small 09) | the same | - |

## Results

### Run 1 (EEVEE, 21 views, `.dev/gate/parts/2026-11-06/`, sheets ours | Aaron in `sheets/`)

With the paint gone, what the paint had hidden shows - each found by looking at the sheets beside Aaron, then
measured where a measure exists:

| Part | Seen against Aaron | Measured | Done |
|---|---|---|---|
| Face skin relief | ours an orange peel everywhere (the new pore tile at the old tile's 0.3 mm) | upper cheek fine / pore / fold 0.82 / 1.74 / 1.31 vs 0.51 / 1.15 / 0.89 | pore depth 0.15 mm, microrelief 0.015 mm -> 0.63 / 1.135 / 0.884 (`maps.py`; scratchpad `pore_tune.py`) |
| Stubble | ours scattered black straight hairs up to the cheekbones, a hard line on the jaw; his short, dense, curved, grey and dark, lip / chin / jaw only | - | region from the mouth (lip, chin, jaw, cheeks below the mouth), 100 a cm2, 1 mm, curved, a third grey (`stubble.py`) |
| Lid margin | ours a swollen glossy pink lower rim; his a thin wet line | - | tint (0.86, 0.62, 0.62), roughness 0.25, coat 0.35 (`maps.py`) |
| Round the eyes | dark rings under the brows and eyes (the scans' makeup and socket shade) | - | the composer holds darkening there to 12% and its grey to the skin's hue (`skin_base.py` EYE_DARK) |
| Torso | a horizontal colour seam at the head tile's border; patches at the shoulders; the scanned definition faint beside his sculpted physique | - | the head's colour fades to the tone above the border (`skin_base.py` neck_fade); the torso detail fades 4 cm inside its island (`body_scan.py`) |
| Lashes | sparse at face distance; his a dense dark line | on / off: to measure | - |
| Face shape | puffy lids, small eyes, broad flat nose (MakeHuman's average) | - | shape: step 4 (sliders) / a character's choice |
| Scalp hair | flat, greasy-looking strands; his styled cards | - | step 6 (hair live view) |

### Runs 2-3 and what each changed (`.dev/gate/parts/2026-11-06b`, `-06c`, `hair_cal/`)

| Found | Measured | Changed |
|---|---|---|
| The design's lash settings (180 upper, 0.08 mm, melanin 1.0) never in code; the caruncle (proof 4c) never in code | - | applied (`lashes.py`; base v2's record `caruncle`, the margin layer) |
| Lashes at face distance | on / off: 6,550 px darker by > 5 L*, 1,063 by > 15 (`.dev/gate/parts/proof_lash/`) | they read - no cards or width floor needed now |
| Brows thin without the painted ones | - | 1,400 fine short lighter hairs a brow under the 800 coarse (`brows.py`) |
| The live view's hair a plain Principled surface (rec 1's lobes never written) | first model: hair white (lobes 3x narrow, unshadowed) | Karis' Marschner per light (Light Accumulation), Cycles' lobe width, Shadow Raycast, softened body shadow: scalp window 0.112 vs Cycles 0.121, brow window 0.405 vs 0.367 (`hair_shading.py`) |
| Chest seam and shoulder patches remain | - | the neck fade sat in the face test's coordinates (removed); the body tiles take the head tile's border colour (`build_skins.py`) |
| The lower margin still a glossy rim | - | wet pink at the rim only, fading across the margin (`base.mark`); marks refreshed on every load (`migrations`) |
| No catch light in our eyes (Aaron's shows the key light) | hiding the films, a mirror cornea: none - the key light's reflection lands under our upper lid | the dressed human's eyes opened by MakeHuman's own sliders (no bags, fold, lid's middle up; proof 4b's measured set) |

### Runs 4-6 and what each changed (`.dev/gate/parts/2026-11-06d`, `-06e`, `-06f`, `factors/`; scratchpad `factors.py`)

Run 4 (all 21 views, every fix above but the eye shape) and run 5 (the eye shape, six views, then Average woman, Older
man, Heavy woman, Muscular man) looked at beside Aaron, each gap found one factor at a time before a fix:

| Found | Measured | Changed |
|---|---|---|
| A brown lower face with a hard edge on one cheek, dark sockets, on every scan skin | a flat colour map: unchanged; a flat normal map: gone. The head normal held tilt the composed relief has not (p50 0.13 / p90 0.31 against 0.00) - a plain BSDF baked it too: Cycles' Normal bake keeps its frames on the Basis while the shading follows the shape keys (RESEARCH "The head tile's false shading") | normals baked on the Basis, modifiers off (`build_skins._bake`): p50 0.002 / p90 0.032; skins and library characters rebuilt |
| The chest seam and shoulder patches still there after run 3's colour match: the relief changes size across the line | hm08's UVs inside the head tile: face 600-700 mm a UV unit, neck and shoulders ~1150 - pores 1.6x the face's above the line | the relief layers cross-fade half-octave tilings by each place's density (`maps.add_texel`, `_levels`; CC5 tiles its micro normal by region) - run 6: no seam on the chest or arms |
| The colour still steps at the tile borders (one median colour for the body) | - | a 3D border blend in the skin builder (`build_skins._border_blend`, the design's piece 4) |
| Gashes and patches (Average woman's temple and cheek, Older man's and Heavy woman's necks) | the composed reliefs carry wedges of constant tilt where no scan reached - the hole fill streaked the scan's edge texel across wide holes | a relief's wide holes fade to flat (`hair.mirror_fill(neutral=0)`) |
| Stubble dots, no white hairs | his 2.4-4.2 mm lying close, a third white; ours 1 mm at 45 degrees | 3.2 mm, 22 degrees, 0.1 mm thick, white melanin 0.04 (`stubble.py`) |
| Brows a black bar with a brush at the head | his dark grey with a quarter white, sparse at the head, arched hairs | a fifth white, the head at 45% density, hairs arching toward the tail, 0.07 mm (`brows.py`) |
| A swollen glossy lower rim with a kink under the iris | the lower lash line up to 5.2 mm off the eyeball (the next row 0.8 mm) - the contact key held only a minimum | the lash line capped at base v2's 2.6 mm, its move carried into two rings of skin (`parts.eyelid_contact`) |
| Lashes in spiky clumps, no upper margin seen; lower lashes invisible; a dark grey outline round the opening; a flat white | - | next: one factor at a time (lashes remade on the opened lids, the tearline hidden) |

Run 7 (`.dev/gate/parts/2026-11-06g`): the rebuilt skins (border blend, flat-faded relief holes), the stubble, on the
five characters.

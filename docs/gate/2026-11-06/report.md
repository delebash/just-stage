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

### Run 2 (after the fixes above): running

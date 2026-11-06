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

(filled after the run)

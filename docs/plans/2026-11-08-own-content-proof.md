# Our own content against HD Aaron, part by part — read this FIRST after any compaction

## The job, in the user's words (2026-11-08)

- "prove if we can meet quality that means with our texstures, otherwise it doenst work" (09:55, on my moving to the
  mixer after the transplant verdicts).
- "you need to see if our skin our textures our shaders matdh and all parts matdh, how hard is it to test and fix these
  issues ... you whewr supposed to make a specific plan to test this and it looks like you keep getting sidetracked and
  lost" (~10:00).
- Standing: TASKS "UNTIL A VERDICT ON EVERY PART"; the plan's §0 (the bar: ours against HD Aaron, both EEVEE; one loop
  per part; the stop rule).

The transplant verdicts of 2026-11-08 (`docs/gate/2026-11-07/report.md`, "the verdict per part") show only that our
mesh and renderer can carry his quality - diagnostics, not verdicts. Nothing else (no mixer, no features) until every
part below has a verdict with OUR content.

## The test (the same for every part)

1. **Render** our default character exactly as the app makes it (`parts_gate.py --character new`: New human, dressed -
   our skin, textures, shaders, eyes, teeth, brows, lashes) and HD Aaron (`--who cc5`): the app's stage, the gate's
   camera and views, EEVEE. Where a part needs what New human lacks (scalp hair, stubble, face units), the gate's own
   man (`--who ours`) with the library's content.
2. **Measure** each part against him: texture `tools/gate/dists.py --patches` (excess over his own patch-to-patch
   band); colour (Lab, `measure.py`); shine `tools/gate/shine_probe.py` (roughness, specular per pixel, his and ours);
   size and shape where it applies; a side-by-side sheet.
3. **Pass** = within his own band (the "skin rule" the user hasn't answered yet - used here provisionally and said so).
4. **Fail** -> change one thing in OUR content (a texture, a shader value, a shape), re-render, keep it only if the
   gap closed, undo it if not; until it passes or every change in our control is tried -> "can't, because X is missing".
5. **Status words:** matches / doesn't match yet / can't (X missing). Never "feasible".

## Order and status (update the moment a result lands)

| # | Part | Status | Our number vs his band | Last change tried |
|---|---|---|---|---|
| 1 | Face skin: texture, colour, shine (the "plastic" look) | doesn't match yet | shine matches on the matched window (cheek sheen 0.61 vs his 0.58); texture DISTS excess cheek 0.018, forehead 0.042 (chance +-0.002-0.004); fold band 1.01 vs 1.35; a* 11.1 vs 13.0 | round 1 (8 trials): none kept; round 2 next - forehead pores, tile, fold relief, redness |
| 2 | Body skin: torso, hands, feet | doesn't match yet | torso 0.049 vs 0.023 (his skin on ours), hand 0.047 vs 0.016, foot 0.102 vs 0.002 | - |
| 3 | Scalp hair | doesn't match yet | - | - |
| 4 | Eyes: eyeball, iris, sclera, lids | doesn't match yet | eyeball 14.8 mm vs 13.2 | - |
| 5 | Brows, lashes, stubble | doesn't match yet | - | - |
| 6 | Lips, teeth, mouth | doesn't match yet | - | - |
| 7 | Smile, blink, speech, wrinkles | doesn't match yet | - | - |
| 8 | Nails, ears | doesn't match yet | - | - |
| 9 | Whole body; four characters | doesn't match yet | - | - |

## Where it stands

- 2026-11-08 ~10:20: renders made 09:45-09:57 (`.dev/gate/parts/2026-11-08new`: `eevee_{view}_ours_new` the New
  human, `_ours` the gate's man, `_cc5` HD Aaron; front, three_quarter, face, eye, cheek, nose, forehead; sheets
  `scratchpad/sheet_new_*.png`). Caveat: web-9e's model filled the card 09:52-09:55 (the end of the man's render, the
  start of Aaron's) - checked by eye before use. Next: measure part 1 on them.

## Part 1, face skin - candidate fixes (written before any trial; the plan's guard)

Seen on the 09:45 renders (sheets `scratchpad/sheet_new_{face,forehead,cheek}.png`): his face shows a broad sheen
(forehead, nose, upper cheek), red mottling and fine capillaries, forehead lines; ours (New human) an even pale pink, a
uniform pebbly bump at the forehead (orange peel), almost no sheen though our roughness is the lower - so the first
question is why our highlight is missing, measured, not guessed: `parts_gate --passes` (EEVEE's Specular Light, Diffuse
Light into an EXR) read by `tools/gate/sheen.py` (sheen share = specular / all light, sheen spread = its variation) at
the face, cheek and forehead windows, ours and his.

| Id | Change (a gate trial first - `factors.py`, materials only; kept ones go into `maps.py` / the library skins) | Moves |
|---|---|---|
| S1 | fine relief (`micro*0.5`, `*0.25`): a strong regular bump breaks the sheen into glints | sheen share, spread; DISTS |
| S2 | roughness to his 0.66 with his kind of variation (`rough*1.38`, then `roughvar`) | sheen share, spread |
| S3 | specular level (`spec*1.25`, `*0.8`) | sheen share |
| S4 | the coat (`coat*0.5`, `*2`; `coatrough`) | sheen share, spread |
| C1 | redness and mottling in our composition (skin_base compose `mottle`, `redness`; the mid layer's strength) | Lab a*, its spread |
| W1 | scattering (`sss*0.7`, `*0.5`): the waxy look | Lab L* spread, contrast |
| T1 | the forehead's tile (Ten24's: 0.0359 -> 0.0286 measured 11-08, not shipped) | DISTS forehead |
| T2 | the scans' fold relief on the forehead (`relief*1.5`, `*2`): his lines | DISTS; the look |
| T3 | pore depth and size per region (`pores`, `poresize`) | DISTS |

Measures for every trial, beside his: sheen share and spread (face, cheek, forehead windows), Lab and its spread
(`measure.py`), DISTS excess (`dists.py --patches`, cheek / forehead / nose), and the face sheet by eye. Tone is a
character's slider, not quality: compared at matched tone where colour is judged (`dists.py --tone`).

### Measured 2026-11-08 ~10:55 (`measure.py` on `.dev/gate/parts/2026-11-08new`, EEVEE; detail = RMS L* by band)

| Window | Who | L* | a* | b* | micro | pore | fold | form |
|---|---|---|---|---|---|---|---|---|
| cheek | HD Aaron | 73.3 | 13.0 | 12.6 | 0.64 | 1.73 | 1.35 | 0.70 |
| cheek | gate's man (library Average man) | 75.5 | 11.1 | 13.8 | 0.67 | 1.69 | 1.01 | 0.62 |
| cheek | New human (the app's default) | 82.2 | 6.7 | 8.2 | 0.37 | 1.10 | 0.73 | 0.47 |
| forehead | HD Aaron | 73.9 | 12.3 | 12.1 | - | 1.69 | 1.09 | - |
| forehead | gate's man | 76.0 | 10.8 | 13.5 | - | 3.23 | 1.82 | - |
| forehead | New human | 84.1 | 6.4 | 7.9 | - | 0.74 | 0.58 | - |

The New human - what a user gets from New human - is far below the gate's man: paler (L* +8-10 over him), half his
redness, about half the detail in every band. The gate's man is near HD Aaron on the cheek (detail 0.95-1.05 of his
but the fold band 0.75), above him on the forehead (pores 1.9x). So the first fix is what the New human gets that the
library's man doesn't (running: `scratchpad/diff_new_vs_man.py`, both built the gate's way, every skin input side by
side) - then the shine trials on whichever is the app's default.
**Found (`scratchpad/diff_new_vs_man.json`, 2026-11-08 ~11:00):** the two skin materials are identical - every image
and node value; the only differences are the tone (melanin New human 0.0104, man 0.03 - three times paler) and the
shape (gender New human 0.5, MakeHuman's default in-between face; man 1.0). So the "plastic" first look is the New
human's defaults (pale, half-male face), not other skin assets; the skin proof runs on our man (the same assets) at his
tone, against HD Aaron. The New human's defaults are a row of their own (a decision for the user's list; what CC5's
own new character starts from is unchecked).
**Baseline texture (DISTS `--patches`, the same renders, CPU, 2026-11-08 ~11:10; pass = within the chance band):**
cheek - the man +0.0179, the New human +0.0525 (chance +-0.0023); forehead (eye view) - the man +0.0423, the New human
+0.0599 (chance +-0.0029 / 0.0039). Not tone-matched (tone is a slider): `--tone` reruns structure alone.

### Run log

- 10:2x: the passes - Blender 5.3 picks multilayer EXR by `media_type = "MULTI_LAYER_IMAGE"` (its `file_format` enum
  lacks it otherwise) and writes a multi-part EXR, a part a pass ("ViewLayer.Glossy Direct"; EEVEE gives Diffuse and
  Glossy as "Direct" only - its whole light); `sheen.passes` reads every part (tests 2 passed).
- 10:35: HD Aaron's render with passes crashed Blender (EXCEPTION_ACCESS_VIOLATION in EEVEE's world capture,
  `CaptureView::render_world` -> `GPU_texture_mipmap_mode`, a null read; `F:\ClaudeCode\tmp\blender.crash.txt`); the
  same render without passes ran at 09:53 and his face view with passes ran once at 10:2x. Rerun alone after the trials
  before anything is built around it.

- 10:35-10:58: the 8 trials on our man rendered (`.dev/gate/parts/2026-11-08shine`, 32 renders with passes); 11:0x
  HD Aaron rerun alone with passes - no crash (the 10:35 crash was a one-off). **Seen** (`scratchpad/sheet_trials_face.png`):
  at the face view the eight trials look alike - none moves our face toward his. What separates the faces at that
  distance is the shape (his narrow, structured face - brow ridge, cheekbones, deep-set eyes, a defined nose - against
  MakeHuman's broad flat average), the eyes, the lips, the colour's variation - not the shine. So the skin is judged on
  the matched windows (the plan's pass 4) and the overall face look waits on the shape row; asked of the user: the face
  shape before the body skin (my rec: yes - it is what the face view is made of).

### Round 1 (face skin: shine and two texture levers) - measured 2026-11-08 ~11:55 (`scratchpad/shine_table.txt`,
`dists_shine.txt`; our man, EEVEE; sheen = specular / all light; DISTS excess, pass = within chance +-0.002-0.004)

| Trial | Sheen face forehead | Sheen face cheeks | Sheen cheek view | Spread | L* | a* | pore | fold | DISTS cheek | DISTS forehead | Kept? |
|---|---|---|---|---|---|---|---|---|---|---|---|
| HD Aaron | 0.578 | 0.376 | 0.583 | 0.67 | 73.3 | 13.0 | 1.73 | 1.35 | - | - | - |
| ours as built (`micro*1`) | 0.414 | 0.347 | 0.612 | 0.69 | 75.5 | 11.1 | 1.69 | 1.01 | 0.0179 | 0.0423 | - |
| coat x0.5 | 0.407 | 0.348 | 0.607 | 0.72 | 75.3 | 11.3 | 1.74 | 1.04 | 0.0181 | 0.0423 | no (no change) |
| coat x2 | 0.425 | 0.346 | 0.619 | 0.65 | 75.9 | 10.7 | 1.60 | 0.96 | 0.0177 | 0.0425 | no (no change) |
| micro x0.5 | 0.416 | 0.349 | 0.615 | 0.68 | 75.6 | 11.0 | 1.71 | 1.05 | 0.0363 | 0.0617 | no (worse) |
| pores x0.6 | 0.427 | 0.348 | 0.619 | 0.66 | 75.8 | 10.9 | 1.31 | 0.85 | 0.0247 | **0.0390** | forehead only: next round |
| rough x1.38 | 0.394 | 0.371 | 0.580 | 0.41 | 75.1 | 11.5 | 1.08 | 0.84 | 0.0514 | 0.0637 | no (worse) |
| spec x1.25 | 0.413 | 0.348 | 0.610 | 0.70 | 75.9 | 10.7 | 1.88 | 1.07 | 0.0210 | 0.0439 | no (worse) |
| sss x0.7 | 0.414 | 0.347 | 0.612 | 0.69 | 75.5 | 11.1 | 1.75 | 1.03 | 0.0177 | 0.0420 | no (no change) |

**Read:** our skin's shine already matches his where the skin is matched (the cheek view 0.61 vs 0.58, spread 0.69 vs
0.67); no shine lever moved the texture score toward his - raising roughness to his 0.66 (S2) made it much worse
(0.018 -> 0.051: our sheen goes too even, spread 0.41). The face view's forehead gap (0.41 vs 0.58) is his forehead's
shape facing the key light - the shape row, not a skin setting (none of these moved it). So: S1-S4 and W1 done, none
kept. Left for the face skin: the texture (cheek 0.018, forehead 0.042 - the gap), the fold band (ours 1.01 vs his 1.35),
the colour (a* 11.1 vs 13.0; L* is the tone slider). Round 2: pores x0.6 on the forehead alone, Ten24's forehead tile
(T1), the scans' fold relief (T2 `relief*1.5`), the redness (C1, a rebuilt skin).

### Round 2 (face skin: texture) - set up 2026-11-08 ~12:20

- **T1 kept (mine, from measurements already made):** the checklist's row 1 (block C, 2026-11-08) had Ten24's
  forehead pore tile better or equal everywhere against HD Aaron - forehead 0.0359 -> 0.0286, nose 0.0785 -> 0.0737,
  torso 0.0493 -> 0.0310, hand and cheek within noise - waiting only on its licence row: the same scan and grant as the
  shipped cheek tile (Ten24: "free for commercial and personal projects ... a credit"), the same size (154 px, 33.5 mm,
  so every material's tiling stays right and no library rebuild is needed - `pore_relief` loads the file by path).
  `pore_tile.py` now cuts the forehead (`TEN24_CROPS`, `TEN24_PLACE`); ATTRIBUTION's row says so; the old tile backed up
  in `.dev/backup/pores_2026-11-08`. Not repeated: red mottling (row 1 says it doesn't move the cheek).
- **2a** (`scratchpad/batch_r2a.sh`, out `.dev/gate/parts/2026-11-08r2a`): the tile regenerated and checked equal to the
  trial's; our man with it as built, and with the scans' fold relief x1.5 and x2 (the fold band 1.01 against 1.35).
- **2b in the same build:** the forehead's own pore depth as region-map variants (round 1's `pores*0.6` helped the
  forehead and hurt the cheek - so the forehead alone): `make_face_regions.py -- --out .dev/gate/regions/<name>
  --pores forehead=1.2` (x0.6) and `=1.5` (x0.75), swapped in by `factors.py regions*<name>`; the shipped map is
  changed only if a variant wins. Each is one change against the as-built baseline in the same build.
- 12:5x: the tile regenerating (CPU); the variants generating (CPU); just voice has the card (~25-30 min); then 2a.
- 13:08: the tile regenerated, equal to the trial's (`r2a_tile.log` "TILE SAME AS TRIAL") - our shipped pore tile now;
  both variants written (`regions_variants.log`).
- **14:05: the computer locked up and restarted** (round 2a not yet started - it waited on just voice's card; nothing
  lost). This job's scratchpad is the previous session's:
  `F:/ClaudeCode/tmp/claude/bff537e12af9b769/5a1c3314-77f3-4a60-8d1a-9d80b40bc2f8/scratchpad`.
- **14:2x, found before rendering:** the variants differ from the shipped map not only in the forehead's pores but at
  region borders in every channel (R, G, B: 287k / 45k / 51k pixels, up to 8 levels in G and B) - the map is made on
  today's New human, whose default shape has changed since the shipped map (2026-11-07 18:57). So today's map unchanged
  (`--out .dev/gate/regions/base`, no `--pores`) is in the round as `regions*base`: it differs from the shipped map at
  81,213 border pixels (max 8 levels), and the two variants differ from it in R alone (the forehead's pores; ratio
  down to 0.603 / 0.750 at the region's core). Each forehead variant is judged against `regions*base`, not against
  `micro*1`. 14:2x: both peers gave the card; round 2a running (`batch_r2a.log`).

## Mistakes to avoid

- A transplant is not a verdict. A side fix (speed, tooling, layout) is not the job unless the proof step needs it.
- Read the code before saying what a test used (I said the gate had its own lights - it uses the app's stage).

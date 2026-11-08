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
| 1 | Face skin: texture, colour, shine (the "plastic" look) | doesn't match yet | DISTS excess cheek +0.006, forehead +0.022, nose +0.031 (11-08 a.m., gate man); roughness ours 0.43-0.48 flat vs his 0.66 (p10-p90 0.62-0.70) | - |
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

## Mistakes to avoid

- A transplant is not a verdict. A side fix (speed, tooling, layout) is not the job unless the proof step needs it.
- Read the code before saying what a test used (I said the gate had its own lights - it uses the app's stage).

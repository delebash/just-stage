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

## THE PLAN, IN MY WORDS (2026-11-08 ~14:50 - governs; replaces "The test" and the order below)

The user, ~14:45 (TASKS, verbatim): rewrite a simple plan in my own words, my own quality bar - "it has to look as
real as cc5" - my own decisions, each attacked until it doesn't change.

**The goal.** Our character - the model and every part: skin, eyes, nose, lips, teeth, tongue, hair, nails - looks as
real as CC5's HD Aaron does in Blender's EEVEE, built only from what we may give away free: our code, free assets, and
assets we make or combine. Or: proof that a part can't, naming what is missing.

**The bar (mine).** Side by side with HD Aaron - the same stage, EEVEE, the gate's views (whole face, three-quarter,
and close-ups of the eye, cheek, forehead, nose, lips, open mouth with teeth and tongue, ear, hand, nails, scalp hair,
whole body) - nothing in ours looks less real than his. "Less real" means a fault no real person has: plastic or waxy
shine, rubbery or puffy shapes, one flat colour, skin too smooth or too regular, painted-on detail, hard edges where
skin should blend, seams, a dark or wrong-coloured part, hair that reads as a helmet, glassy or doll-like eyes.
Identity is not a fault (face shape, lip size, age, tone, build - character settings). Numbers back the eye, only on
the same skin on both renders with nothing over it: skin texture (DISTS excess) at most his own skin's score on our
head + 0.005 (about twice chance); detail per size band within 15% of his. A part passes when my written fault list
for ours is empty (or matched by the same fault in his), its numbers are inside, and its side-by-side sheet is saved
for the user. Then the same check on three other characters (a woman, an older man, a darker skin).

**The order (mine): the worst-looking fault first**, from one fresh side-by-side of every view - not the smallest
measured gap. A fault I can't see on the sheet is not worked on.

**The loop.** Name the fault -> list the ways to fix it (a setting, code, our texture, a free source, an asset we make
or combine) -> try them one at a time, each trial one change -> keep it if the fault visibly shrinks and nothing else
gets worse -> into the product and the library, seen on a fresh New human. A fault that survives every route: "can't",
with what's missing.

**Rules against my own mistakes (each happened today).** Before any render, check the measure reads the same skin on
both with nothing covering it, and that each trial changes one thing. While the card is busy, prepare the next round
of the same fault. Never pick a trial from a hunch when a number or the sheet says where the fault is.

Attack passes (what each changed): (1) "my eye could pass my own work" -> the written fault list, the numbers where
valid, and every sheet kept for the user's final look; (2) "worst-first breaks riskiest-first" -> the worst visible
fault is also the likeliest "can't", so it answers feasibility sooner; (3) "the DISTS limit lets the cheek pass" ->
the cheek sits at +0.006 over his skin's own score, still outside; it waits behind visible faults; (4) "identity vs
realism" -> rubbery lips are a fault, full lips are not; (5) "which character" -> the library's Average man (an app
character on our assets) at the views, every kept fix checked on a fresh New human. A sixth pass changed nothing.

## The test (superseded 2026-11-08 ~14:50 by the plan above - kept as the record)

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
| 1 | Face skin: texture, colour, shine (the "plastic" look) | doesn't match yet | shine matches on the matched window (cheek sheen 0.61 vs his 0.58); texture DISTS excess cheek 0.018 (his skin on our head 0.012; chance +-0.002), forehead 0.0286 on its valid view (block C, the Ten24 tile, now shipped; the "0.042" first written here was the eye view - VOID, see round 2); fold band 1.01 vs 1.35; a* 11.1 vs 13.0 | round 1 (8 trials): none kept; round 2a (fold relief) and 2c (the forehead on its valid view) |
| 2 | Body skin: torso, hands, feet | doesn't match yet | torso 0.049 vs 0.023 (his skin on ours), hand 0.047 vs 0.016, foot 0.102 vs 0.002 | - |
| 3 | Scalp hair | doesn't match yet | - | - |
| 4 | Eyes: eyeball, iris, sclera, lids | doesn't match yet | eyeball 14.8 mm vs 13.2 | - |
| 5 | Brows, lashes, stubble | doesn't match yet | - | - |
| 6 | Lips, teeth, mouth | doesn't match yet | - | - |
| 7 | Smile, blink, speech, wrinkles | doesn't match yet | - | - |
| 8 | Nails, ears | doesn't match yet | - | - |
| 9 | Whole body; four characters | doesn't match yet | - | - |

## Step 1's fault list (2026-11-08 15:0x, every view fresh: `.dev/gate/parts/2026-11-08all`, sheets `scratchpad/all/all_<view>.png`, grids `grid_g1-5.png`)

The user, ~15:00: good enough = "a human cant visually tell the difference on closeup" - not a score of 0. So the
cheek's 0.018 against his skin's 0.012 on our head passes. Each part has a one-hour box (two fix rounds); then the
verdict - matches / close / not possible with free assets (what's missing) - and the next part (the user, ~14:55: "give
up on it and say it is not possible ... you job is not to keep trying until the universe ends").

| # | Part | Verdict now | What a person sees (ours against his) |
|---|---|---|---|
| 1 | Scalp hair | far | a grey helmet with a hard fringe line over the forehead, a bowl outline in profile and from behind, orange strands at the nape; his a layered short cut, darker roots, light tips |
| 2 | Face shape and eyes' look | far | broad, flat, puffy face with small squinting eyes - reads as a doll; his bone structure (brow ridge, cheekbones, nose) |
| 3 | Lips | far | smooth pink rubber, hard outline, no lines, broad plastic sheen; his lines, darker border, small wet highlight |
| 4 | Eyes (eyeball, lids) | far | the white too bright and bluish-grey, a thick orange ledge on the lower lid, no crease; the closed lid's skin smears into a stretched blur in the blink |
| 5 | Stubble | far | a dense fuzzy mat over the lower face and chin; his short, sparse, greying |
| 6 | Forehead and nose skin | far | a pebbly orange-peel bump all over; his smooth with lines (forehead), fine pores and redness (nose) |
| 7 | Teeth, mouth | far | small evenly spaced pegs; his natural teeth |
| 8 | Feet | far | smooth plastic, no detail (no free scanned foot - known) |
| 9 | Torso, neck | far | flat and smooth, two light blotches by the sternum, a darker patch on the neck's side; his defined (his build is identity, the blotches are faults) |
| 10 | Ears | close-far | small, smooth, little inner detail; his detailed, redder inside |
| 11 | Nails | close | the plate reads set in with a dark ring, the fingertip skin pitted; his natural |
| 12 | Hands | close | real tendons and creases; ours paler (tone, a setting) |
| 13 | Cheek skin | **matches** (the user's bar) | a touch softer and less red if you hunt for it |

Order of work (worst first): 1 hair, 2 face shape, 3 lips, 4 eyes, 5 stubble, 6 forehead and nose skin, 7 teeth, 9
torso and neck, 10 ears, 11 nails, 8 feet (its route is the user's download).

**The user's hour (15:12-16:15, "you control all pc resources ... complete this in under an hour"):** the peers hold
heavy work until "PC free". Runs: hair round 1 (`.dev/gate/parts/2026-11-08hair1`), the quick round
(`2026-11-08q`: forehead and nose pore depth, lip tint and shine, eye white, stubble density and grey), the face shape
round (`2026-11-08face`: leaner cheeks with cheekbones, the brow up with the eyes more open, both). **15:14 our Blender
reached 17.6 GB RAM / 43.8 GB committed, free RAM 0** - four `--alone` builds of a 183k-strand scalp in one process
pile up; killed at once (free RAM back to 18 GB). Since: one Blender process per new-groom or new-shape trial
(`batch_rest.sh`), and `scratchpad/ram_guard.ps1` stops our Blender by itself below 3 GB free.
- Hair round 1, read: flatter sides (`scalpstyle*sides`) bare the scalp at the side and keep the helmet - not kept.
  The sheet shows the cause: our hairline ~30 mm above the brows and the hair over the temples - a wig's edge round a
  small forehead; his hairline far higher. Trials queued: the scalp grown one ring (`hairline`) and none
  (`hairline0`) past MakeHuman's hedgehog roots (56 mm above the eye), and lighter tips (`hairtip*0.5`).
- The foot: Thunk3D's CC BY scan downloaded (RESEARCH §14.11) - its fit and bake after the quick parts.
- **The quick round, read by eye (15:3x, rows `scratchpad/row_q_*.png`):** forehead pores x2 -> x1 takes the orange
  peel away at the eye and forehead views - **KEPT** (`make_face_regions.py` REGIONS forehead 2.0 -> 1.0; the shipped
  map and the library rebuilt at the hour's end). Nose pores 0.6 -> 0.3: no visible change; the nose reads close to
  his (his redder - tone) - **nose: matches**. Lip tint (0.95, 0.58, 0.62): orange and waxy - not kept. Lip shine
  rough 0.5 / coat 0.15: a little less plastic, still a smooth tube - kept for round 2. Eye white x0.85: no visible
  change - not kept; the eye's fault is the lid's shape and the missing darkness round the eye, not the white.
- **Stubble (15:40, rows `row_q_stubble*.png`):** 100 a cm2 (160 shipped) reads lighter, no longer a mat, close to
  his at the lips and face views - **KEPT** (`stubble.DENSITY` 160 -> 100; the library's characters carry it after the
  rebuild). A greyer mix (0.45) reads closer to him too, but grey is age - a character setting, not a fault: 0.25 kept.
  Left: our beard region reaches higher up the cheeks than his.
- **Face shape round 1 (15:51, rows `row_face_{face,eye}.png`):** leaner cheeks with cheekbones, the brow raised with
  the eyes more open, both (our MakeHuman sliders at 0.4-1.0) - each moves the face a little; at the face view it still
  reads as a doll - not kept. What makes the doll look, read off the sheets: the eyes (a narrow opening, no lid crease,
  no darkness round the eye - his has a deep crease and dark, reddish lids and under-eyes), the hair's frame, the lips -
  more than the cheeks' width. Round 2 queued: the sliders at full strength with the brow ridge forward
  (`faceshape*strong`), and the skin round the eyes darker and redder (`eyedark*0.8`, by the region map's eyes region).
- **15:54, a second runaway, caught by the RAM guard at 0.2 GB free:** `scalpstyle*hairline` removed the scalp mask
  image the fill group's node pointed at - hair grew over the whole body (3,545,891 strands, 30 GB committed). My bug:
  the trial now writes the new mask INTO the fill's own image. The guard now checks every 2 s and stops our Blender at
  6 GB free (10 s / 3 GB let it reach 0.2). The hairline trials rerun after face round 2 (`batch_hair2.sh`).
- **Hair colour (16:00, `row_hairtip_*.png`):** lighter tips (`hairtip*0.5`) turn our hair orange-brown, not his
  ash-light tips over dark roots - not kept. The back view shows the gap is the cut: ours one blocky helmet with a
  straight edge at the nape, his layered, lifted on top, tapered. Our generator's settings (round 1) can't make that;
  the route left: an artist's free cut - VincentFreelance's CC BY men's collections on Sketchfab (RESEARCH §14.14, ~100
  cuts as cards), downloaded by us through the signed-in Chrome, as the foot was. Also seen: a skin patch on the back of
  the neck (a body-skin fault). 16:02: the Chrome extension disconnected ("Browser extension is not connected") - the
  download waits for it.
- **Lip lines (16:04, `row_lip2.png`):** our shader-made lines at 0.25 and 0.5 mm depth barely show; the lips still
  read as a smooth tube - not kept. The thinner-lip shape follows.
- **Thinner lips (16:10, `row_lip3.png`):** `faceshape*lipthin` gives a slightly better shape with a cupid's bow, but
  our pink tint (MPFB2's lips mask on hm08's UVs) then spills above the new lip edge; with the shine and lines too they
  still read as a smooth tube. **Lips, the box spent: not reached by settings, sliders or shader lines. Missing: a lip
  detail map of our own (colour darkening to the border and seam, a lighter centre, fine lines) fitted to the lip's
  shape - a made asset, its own job; no free scan resolves it (Ten24 ~220 texels across the lips).**
- **Face round 2 (16:15, `row_face2_{face,eye}.png`):** the eyes' surround darker (`eyedark*0.8`) barely shows - not
  kept; the sliders at full strength (`faceshape*strong`) give a heavy shadowed brow ridge - worse - not kept. **Face
  shape, the box spent: our MakeHuman sliders don't make the face read real. Missing: a scan-based face shape - the
  route is the mixer's scan identities (stopped by the user at 09:55); the transplant of 11-08 (his shape on our mesh,
  `aaronshape*upper`) showed our mesh carries a real face's shape.**
- **Hairline (16:23, `row_hair2_{face,profile}.png`, the mask fix working: 145,707 / 138,564 strands):** one ring
  past the hedgehog's roots raises the hairline and shows a real forehead - the face reads much less like a doll; no
  bare line at the side - **KEPT** (`scalp.MASK_RINGS` 2 -> 1); none left a hard edge at the temple. The cut is still a
  helmet: **hair, the box spent: our generator's settings don't make a real cut. Missing: an artist's cut - a free CC BY
  one (VincentFreelance's collections) through Chrome, which disconnected at 16:02.**

### The hour's verdicts (15:12-16:23, the user's bar: a person can't tell at close-up)

| Part | Verdict | Kept in the product | What's missing |
|---|---|---|---|
| Cheek skin | matches | - | - |
| Nose skin | matches (his redder - tone) | - | - |
| Forehead skin | orange peel gone (kept; to confirm at the face view after the rebuild) | forehead pores x2 -> x1 | - |
| Stubble | close (lighter, sparse like his) | density 160 -> 100 a cm2 | the beard region reaches higher on the cheeks |
| Scalp hair | not reached | the hairline one ring (higher, softer) | an artist's cut (free CC BY on Sketchfab) |
| Face shape | not reached | - | a scan-based face shape (the mixer, stopped by the user) |
| Lips | not reached | - | a lip detail map of our own (colour to the border and seam, lines) |
| Eyes | not reached | - | the lid's shape (crease, margin) - the white and the surround's colour don't move it |
| Teeth, ears, torso and neck patches, nails, feet | not tested this hour | - | - |

Kept changes go into the app once: the region map regenerated and the library rebuilt (backup first), booked with the
peers (after family-release's e2e).

**16:3x, found: two of the hour's trials were VOID - `eyedark` and `liplines` rewired the film BSDF alone; the skin has
a live-view copy (`skin.material.LIVE_BSDF`, an EEVEE-only output) that `sync_live` must refresh, so EEVEE never saw
them.** Fixed (`factors._skin_materials`: the product's `principled()` and `sync_live` after); both rerun in the next
card slot (`batch_slot.sh`, after just-voice's piece), with face round 3: a real scan's face shape on our man
(`mix*hsr0040`, `hsr0042`, `hsr0161` - HSRD-100's scan identities, CC BY 4.0, through the mixer's own command; a local
proof that a scan shape reads real, not the mixer's feature work). The lips' and eyes' verdicts above wait on them.

**The foot's route (written while the PC is the peers', 16:4x):** Thunk3D's scan is a leg and foot alone (STL,
2,971,647 triangles from its size: (148,582,434 - 84) / 50), geometry only. `body_scan.py`'s sources place a scan by
our torso (`_place_rigid` on tile 1) and fit the whole body through Anny - a lone leg has no torso. The standard route
stays (the face's and the hands' - a rigid placement, Amberg NICP, Selected-to-Active bake of the normal), with one
new step: the placement by our foot itself - our foot's faces on tile 1004 (below the ankle joint) against the
scan's foot, scale from the STL's units (read at load), then the wrap of the foot vertices only and the relief baked
into tile 1004's normal map, the edge faded at the ankle (`EDGE_FADE`). A new SOURCES row `thunk3d_foot` ("fit":
"foot"). Booked as a CPU job (trimesh on 3M triangles ~2-4 GB) when the peers' order allows.

**16:5x, the fixed trials (slot cut short at 16:59 - family-release's e2e put Gemma 4 26B on the card; rows
`scratchpad/row_slot_{eye,lips}.png`):** lip lines at 1.2 mm / 0.5 mm, now on both BSDFs - the rubber look is gone,
the lips read as lip skin; too dense and crinkly against his fewer, finer, upright lines - **the route works, tuning
next** (sparser and upright: distortion 2-3, period 1.6, depth 0.3-0.4). The eyes' surround at 0.8 - a slight gain;
his lids and under-eyes are much darker - 0.65 next. Both, and face round 3, in the rebooked slot after family-release's
"CPU free" (~17:20; `batch_slot2.sh`).
- Lips round 2 queued (`batch_lip2.sh`, `.dev/gate/parts/2026-11-08lip2`): our own lip lines in the shader (`liplines`:
  a Wave texture in bands across the lips, noise-distorted, masked by the lips' share, a bump - no free scan resolves
  lip lines), the lips thinner with a cupid's bow by our sliders (`faceshape*lipthin`), and all three together.

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

| Trial | Sheen face forehead | Sheen face cheeks | Sheen cheek view | Spread | L* | a* | pore | fold | DISTS cheek | DISTS "forehead" (the eye view's top patches - VOID, see round 2) | Kept? |
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
- **14:36 renders done (30); 14:4x found, looking at the sheets (`scratchpad/sheet_r2a_{forehead,cheek}.png`): the
  forehead numbers of rounds 1 and 2a are VOID.** Round 1's "DISTS forehead" column was the eye view's top patches,
  declared void on 11-07 late (the gate report: his forehead above the brow against our skin under ours) - so "pores
  x0.6 helped the forehead" and round 2b's forehead variants rested on a void measure. Round 2a rendered the forehead
  view with the fringe over its top half, where `dists.py`'s forehead patches assume the scalp hidden (`nohair`). Valid
  for the forehead: block C's forehead view with `nohair` (0.0359 -> 0.0286 with the Ten24 tile). Round 2a's cheek and
  nose numbers stand. So round 2c (`batch_r2c.sh`): the forehead view only, `nohair` on every trial - as built, the
  map's base, the two pore depths, and his skin on our head (the floor this view never had). By eye, round 2a's cheek:
  relief x1.5 / x2 look like as built; his reads finer, crisper and redder.
- **Round 2a's valid numbers (14:42, `scratchpad/dists_r2a.txt`):** cheek as built 0.0179, relief x1.5 0.0174, x2
  0.0167 (chance +-0.002); nose 0.0735 / 0.0727 / 0.0710 (chance +-0.003). Within or near chance and unchanged by eye -
  **not kept**. The region-map variants change neither (as they shouldn't). Round 2c (the forehead) is set aside: under
  the new plan the order comes from step 1's fault list.
- **14:50: step 1 of THE PLAN, IN MY WORDS** - every view (22) rendered fresh, ours then his, in one batch
  (`scratchpad/batch_all.sh`, out `.dev/gate/parts/2026-11-08all`), sheets by `scratchpad/sheet_all.py`; then the
  fault list, worst first.
- Prepared meanwhile (lips, seen 05:36 renders `.dev/gate/parts/2026-11-08brow/eevee_lips_*`, sheet
  `scratchpad/sheet_lips_now.png`): ours one flat saturated pink, a broad plastic sheen, smooth as rubber, a hard
  outline; his a darker red at the seam and border, a paler lower-lip centre, vertical lip lines, a small wet highlight,
  the colour fading into the skin. Our lips are one tint (`maps.LIP_TINT` (1.0, 0.56, 0.90) over MPFB2's lips mask),
  roughness 0.33, coat 0.3, no relief of their own. Ten24's scan as a lip-line source: its lips span ~220 texels
  (4.6 / mm) and its Level_01 normals show the lips' form but no lines (`scratchpad/ten24_lips_pair.png`) - too coarse.

## Mistakes to avoid

- RAM and the processor are booked like the card (the global rule, 2026-11-08 after the lock-up; just voice read
  Windows' log: at 10:34 a low-virtual-memory warning on the 32 GB PC - its audiocpp_cli 22.8 GB, audiocpp_server
  16.5 GB and our blender.exe 9.0 GB - services timing out from 11:00 until the hang at 13:53). Before a Blender build,
  render or CPU scoring: tell the peers what, the GB and the minutes, wait; one heavy job at a time; a watcher
  (`scratchpad/ram_watch.ps1`) logs free RAM and alerts below 4 GB. Our render: ~5 GB RAM, 9.3 GB committed (measured
  14:3x).
- Before any trial, check its measure is valid for the area: which view and patches it reads, what covers them
  (hair, brows), and the gate report's corrections (2026-11-08: two rounds' forehead numbers came from the eye view the
  report had voided on 11-07, and from the forehead view with the fringe on).
- A transplant is not a verdict. A side fix (speed, tooling, layout) is not the job unless the proof step needs it.
- Read the code before saying what a test used (I said the gate had its own lights - it uses the app's stage).

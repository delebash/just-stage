# The gate's first measured baseline (2026-11-07)

THE ONE PRIORITY's first proof (face mid-scale relief) and the body views, on today's code: the clean inputs of
`../2026-11-06/report.md` (its inputs table holds; since then the oiliness link and no pores on lips or lining, commit
0e95ddc), measured with the standard measures of `tools/gate/measure.py` (`../../standards/quality-gate.md` §4).
Renders `.dev/gate/parts/2026-11-07a` (`tools/gate/parts_gate.py render`, views eye, cheek, face, front, torso, hand,
foot; ours = the library's Average man in the Scan man A skin; HD Aaron from the user's export).

## How to read the numbers

Per window: CIE L* a* b*; detail as the RMS of L* per band of real size on the skin (micro 0.06-0.3 mm, pores 0.3-1.5,
folds 1.5-7, form 7-30), each window's form removed first; ours as a ratio of Aaron's, "=" within that measure's band
on Aaron (the window moved 1.5% of the frame, ~1 mm), "<" or ">" outside it. Windows were set by looking at their
outlines (`windows_<engine>_<view>_<who>.png`): the cheek above the stubble, the forehead above both brows.

## EEVEE (the live view)

| View / window | Ours L* a* b* | Aaron's | micro | pores | folds | form |
|---|---|---|---|---|---|---|
| cheek / cheek | 75.5 11.1 13.8 | 73.3 13.0 12.6 | 0.75 < (9%) | 0.86 < (8%) | 0.72 < (9%) | 0.91 = (16%) |
| eye / forehead | 77.2 10.4 13.1 | 71.8 12.5 12.1 | - | 0.92 = (13%) | 0.83 = (18%) | - (window too small) |
| face / face | 54.2 13.8 16.9 | 47.0 16.1 16.0 | - | 1.45 > (8%) | 0.94 < (5%) | 0.81 < (3%) |
| torso / chest | 64.6 13.4 19.3 | 57.9 14.3 21.7 | - | - | 0.85 < (2%) | 0.68 < (17%) |
| foot / top of foot | 67.8 12.4 17.8 | 54.4 16.4 21.7 | - | 0.47 < (32%) | 0.25 < (17%) | 0.29 < (19%) |
| hand / back of hand | (window moved below the knuckles; re-measured with Cycles) | | | | | |

**Read:**
- **Face skin: below Aaron at the cheek** - microrelief, pores and folds each beyond the band (0.72-0.86). This replaces
  the "cheek equal" of 2026-11-06 (pore / fold 1.135 / 0.884 vs 1.154 / 0.894), which was measured before four relief
  fixes and with the old band measure. The forehead's pores and folds are equal within their bands.
- **The face window's pores above (1.45)** - the window takes in our stubble and brows (our stubble's chin share 0.099
  against his 0.061, commit 3c04b4a): to diagnose before it counts.
- **Tone: ours paler and less red** everywhere (L* +2 to +13, a* -1 to -4) - Aaron's tone is his; the gate's man may
  take Aaron's tone as he took his hair colour, so only the content differs (to do, as a factor).
- **Body: below** - the torso's folds and form (a narrower, smoother man than Aaron's sculpted physique), and the feet
  far below (25-47%: flat, as run 11 saw).
- **Hands, by eye** (`windows_eevee_hand_*.png`): ours flat and pale; Aaron's tendons, veins and knuckle creases.

## Cycles (the film, the live view's oracle)

| View / window | Ours L* a* b* | Aaron's | micro | pores | folds | form |
|---|---|---|---|---|---|---|
| cheek / cheek | 74.7 11.9 14.2 | 72.7 14.3 13.3 | 0.44 < (7%) | 0.55 < (6%) | 0.51 < (8%) | 0.74 < (13%) |
| eye / forehead | 76.4 11.1 13.6 | 73.7 13.1 12.5 | - | 0.68 < (13%) | 0.61 < (17%) | - |
| face / face | (Aaron's window cover 0.875 - his face view frames lower; window to move) | | | | | |
| hand / back of hand | 76.5 10.4 14.1 | 67.1 15.7 17.9 | - | 0.29 < (15%) | 0.35 < (20%) | 0.53 < (18%) |
| foot / top of foot | 68.0 12.9 18.0 | 54.7 16.8 21.2 | - | 0.29 < (28%) | 0.17 < (15%) | 0.20 < (20%) |
| torso / chest | 64.0 14.1 19.5 | 57.6 15.2 21.6 | - | - | 0.53 < (2%) | 0.57 < (16%) |

**Read:** in the film, ours is about half of Aaron's detail at the cheek and 0.6-0.7 at the forehead - the face proof
is **not proved in either renderer**, and the gap is larger in Cycles. Aaron's own detail reads ~1.6x stronger in
Cycles than in EEVEE (cheek pores 2.69 against 1.73), ours the same in both (1.47 / 1.49). Why is not yet known - a
hypothesis to test one factor at a time: his maps (normal + micro normal) gain from Cycles' many samples per pixel
where EEVEE's texture filtering softens them, and our bump-node relief behaves differently. Hands and feet: a third of his or less.

## Why Aaron's detail is stronger in Cycles

CC Blender Tools builds his head skin differently per engine (`aaron_hair_eevee.blend` against `aaron_hair_cycles.blend`,
read 2026-11-07): Cycles' Normal Strength 1.25 against EEVEE's 1.0, Micro Normal Strength 0.396 against 0.317 (both
+25%), Roughness Power 0.75 against 0.56, Subsurface Scale 1.0 against 1.43 (EEVEE scatters farther). So the CC5
reference's own Blender pipeline gives each engine its own relief and scatter - as our skin's EEVEE output scatters x2
(approved). Ours reads the same in both engines (the oracle rule holds on our content); each engine is compared with
his build for it. The live view first (the user's bar), then a per-engine relief strength for the film, measured.

## The cheek one factor at a time (EEVEE, `tools/gate/factors.py`)

| Ours with | micro | pores | folds | form |
|---|---|---|---|---|
| everything (baseline) | 0.482 | 1.485 | 0.975 | 0.636 |
| microrelief off | 0.166 | 1.559 | 1.001 | 0.649 |
| pore tile off | 0.512 | 0.526 | 0.728 | 0.675 |
| the scan's relief off | 0.508 | 1.487 | 0.889 | 0.567 |
| colour flat | 0.496 | 1.445 | 0.776 | 0.383 |
| Aaron | 0.639 | 1.727 | 1.345 | 0.697 |

**Read:** the pore tile makes the pore band and a quarter of the folds; the microrelief the micro band; the scans'
mid-scale relief only ~9% of the folds; the colour ~20% of the folds and ~40% of the form. At the forehead the
microrelief (x5 there) *lowers* the pore and fold bands by 20-30% (off: 1.56 -> 1.90, 0.91 -> 1.26) - its fine bumps
average the larger ones. (The first colour factors read identical to the baseline: the library's images are packed,
so changing their path did nothing - fixed by loading new tiled images.)

## The hands' donor, first try (Ten24)

Our hands fitted to Ten24's sample (Anny, then the wrap: p50 2.8 / p90 4.8 mm, after a fix - Blender's OBJ importer
puts the Y-up turn in the object, not the mesh), its 8K Level_01 normal map baked through the 100k mesh: blotches and
holes, not tendons and veins - the Level_01 map holds everything between its coarse level-1 surface and the scan, so on
the 100k mesh the medium shape counts twice. Kept detail under 12 mm: still patchy. Output deleted (nothing shipped).
Next, the structural option: the relief taken in the map's own texture space (Frankot-Chellappa height, high-passed -
the pore tile's method) and carried to our hands through the fit's correspondence.

## The face: the first fix (EEVEE)

Trial settings first (`factors.py`, each layer scaled everywhere): pores x1.15 + microrelief x1.35 took the cheek to
micro 0.93 / pores 0.92 and kept the forehead equal; + the scans' relief x2 lifted the folds 0.75 -> 0.85 but pushed
the form past Aaron (1.11); microrelief x3 read as crackle-glaze cells at full resolution and lowered the larger bands
(it acts as roughness). So `tools/make_face_regions.py` scales every head region's pores x1.15 and microrelief x1.35
(the head tile only). Re-rendered (`.dev/gate/parts/2026-11-07b`): **cheek micro 0.93 =, pores 0.92 =, form 0.90 =,
folds 0.76 < (9% band); forehead pores 0.96 =, folds 0.85 =**. Still below: the cheek's folds; and by eye at full
resolution our cheek's bumps read soft and round where Aaron's show a crisp, irregular, directional network of fine
furrows - our microrelief generator's cells are too regular (the method gap the plan's §9 microrelief row names: a
direction field per region). Cycles: next.

## The hands: Ten24's relief in texture space

`tools/body_scan.py texture ten24`: Ten24's normal-map tilt high-passed at 8 mm inside its own UV islands, its hair
strands (found in its colour) filled, anti-aliased to our texels, carried through the fit's nearest point and turned
from its tangent frame into ours (fit gap p50 0.9 / p90 2.8 mm). Two bugs on the way, both found and fixed: a crop box
past the 8K map's edge came back shifted ~900 texels (the "stripes"), and Blender's OBJ importer keeps its axis turn in
the object. Blended into the gate character's arm tile in memory (`factors.py handspart`; no library skin rebuilt):

| Back of the hand | pores | folds | form | ridges |
|---|---|---|---|---|
| EEVEE, before | 0.51 | 0.51 | 0.71 | 0.29 |
| EEVEE, Ten24's hands | 0.51 | 0.59 | **0.95** | **0.47** |
| Cycles, before | 0.29 | 0.35 | 0.53 | 0.21 |
| Cycles, Ten24's hands | 0.29 | 0.40 | 0.70 | 0.35 |

**Re-measured:** `image.pixels` reads only a UDIM image's first tile whatever tile is active (measured 2026-11-07), so
the first factor's "arm tile" was the face tile's normals under the part; `handspart` now blends the part in the shader
(no pixels read). The numbers came out the same - the window lies where the part's weight is 1 - and the strength and
colour trials (EEVEE, back of the hand, Aaron's bands: form 29%, ridges 9% / 18%, folds 20%):

| Ours with | pores | folds | form | ridges dark / light |
|---|---|---|---|---|
| nothing (before) | 0.51 | 0.51 | 0.71 | 0.29 / 0.29 |
| Ten24's hands x1 | 0.51 | 0.59 | 0.95 | 0.47 / 0.48 |
| x1.5 | 0.53 | 0.67 | 1.12 | 0.61 / 0.64 |
| x1.5 + its colour | 0.55 | 0.78 | **1.24 =** | 0.74 / 0.80 |

**Adopted:** x1.5 with its colour (`body_scan.py` SOURCES["ten24"]["strength"]); the library backed up
(`.dev/backup/library_2026-11-07`) and the scan skins rebuilt. By eye: tendons fanning to the knuckles, veins, knuckle
and finger creases on ours; Aaron's still glossier, more tanned, his veins higher. Still below: ridges (his sculpted
veins), folds, pores; tone (L* 77 against 68 - his tone is his).
**In the rebuilt skins** (`parts_gate --skin` with the old skin from the backup and the rebuilt one - both through the
same path, which renders the hand paler, L* 84 against his 68, so contrast is lower than in the character's own tone),
back of the hand, Aaron = 1: EEVEE ridges 0.17 -> 0.51-0.54, folds 0.36 -> 0.56, form 0.57 -> 0.78; Cycles ridges 0.14
-> 0.41-0.44, folds 0.26 -> 0.42, form 0.44 -> 0.58. The library's characters still wear the skins as they were when
they were built - then rebuilt (`tools/build_library.py -- characters`, 14:27): the six on the new skins. Seen,
not explained: the four face-test characters (Amara, Daniel, Mei, Walter) carry save times of 13:11 today though no
step of mine was meant to save them; the backup (13:55) holds those files. Next on the hands: the donor's colour (knuckles, veins) in the same route,
the part's strength measured, our hand's tone (L* 77 against his 68), then the skins rebuilt (library backed up first).

## The face's folds, and what the bands miss

The scans' relief boosted below 7 mm only (`factors.py reliefband`): x2 folds 0.76 -> 0.83, form 0.90 -> 1.10; x3 folds
0.92 = but form 1.32 > and micro / pores just below - the high-pass leaks into the form band; a true 1.5-7 mm band-pass
is the cleaner version. By eye at full resolution none of it changes the look: **ours reads as soft round bumps,
Aaron's as a crisp, sharp, cross-hatched network with sharp little highlights** - the bands measure energy per scale,
not that character, so the cheek is "equal" on three bands and **below by eye** (the gate's rule: the eye decides
inside the band). The next measure is the plan's DISTS (a texture-structure similarity, "only if the bands and the eye
disagree" - they do). The likely fix is a crisper microrelief; our generator is a NOT STANDARD piece waiting for the
user's word (plan §19.2 item 2), and no shippable scanned micro-normal was found - not developed further meanwhile.
**DISTS** (`tools/gate/dists.py`, piq's implementation; 256 px crops of each window moved 1.5%): Aaron against himself
0.059 (cheek) / 0.073 (forehead); **ours against him 0.188 / 0.188** - about 3x his own floor; the fold boosts change
nothing (0.187); with our tone set to his first (`--tone`) 0.184 / 0.189 - **the gap is texture structure, not
colour**. The face proof stands: **not proved** - the bands' energy is there, the structure is not.

## The hair bound's gate (rec 1, approved 11-04: "two days to its 10% gate under both lights, then hair cards take
## the live view"; the clock to 2026-11-08 09:37)

Ours (the library's "JustStage short combed", the gate's colour), the back of the hair (`hair_back`), EEVEE against
Cycles, the stage and the image light alone (`parts_gate --lights world`), mean linear luminance of the scalp hair's
window and its highlights (p95), `.dev/gate/parts/2026-11-07c`:

| Light | EEVEE / Cycles, mean | highlights |
|---|---|---|
| stage | 0.0712 / 0.0347 = **2.05** | 0.209 / 0.110 = 1.90 |
| image light alone | 0.0020 / 0.0009 = **2.20** | 0.009 / 0.004 = 2.50 |

**Fails, both lights** (the 11-06 pass, 0.112 / 0.121, was the front view's window under the stage light). By eye: a
grey haze over EEVEE's hair where Cycles' is dark with defined highlights. Not the parked sky-only flatness - the stage
light fails too. Factors next, inside the clock: the body's light in its own shadow (`BODY_LIGHT_THROUGH` 0.5) and the
constant image-light ambient (checker D: "a constant ambient of the world's mean frozen at build").

One factor at a time (`factors.py hairthrough`, `hairambient`, `hairmodel*body*lobes*ambient`; EEVEE / Cycles, mean):

| Setting | back, image light | back, stage | front, stage |
|---|---|---|---|
| as built (body 0.4, lobes 1.0, ambient 1.0, light through 0.5) | 2.20 | 2.05 | 0.77 |
| ambient x0.45 | **1.02** | 1.98 | 0.76 |
| light through 0.15 / 0 | - | 1.80 / 1.70 | - |
| body 0.2 | - | 1.50 | 0.66 |
| lobes 0.5 | - | 1.30 | 0.58 |
| body 0.2, lobes 0.5 | - | 0.84 | 0.49 |

**Read:** the image light's half is the constant ambient - x0.45 meets the gate (1.02), adopted (`hair_shading.AMBIENT`).
Under the stage light the front of the head reads darker than Cycles and the back brighter, and every global share
moves both together - no calibration meets 10% on both views: the model's angular response is wrong (the rim light
behind the head, the TT / body balance), not its level. **The bound's gate fails for the hair's own reasons.** By the
approved rule ("then hair cards take the live view") the live view goes to cards at the clock's end (2026-11-08 09:37);
no cards exist for our generated styles (Strands2Cards' method, the plan's §14 "Cards", TO BUILD) - the plan's §19.2
item 27.

## Evening: the face loop - EEVEE only, the plan's §0

The user, 2026-11-07 evening: the bar is the live view - ours against HD Aaron in EEVEE, nothing else (plan §0). So
this section is EEVEE only; the Cycles tables above are diagnostics of ours, and the hair bound's verdict above was
judged against our own Cycles, not against Aaron in EEVEE - it is re-measured against his hair (plan §19.2 item 27).

**Why ours reads soft** (RESEARCH §14.9): our pore tile is 4.6 px/mm (Ten24 Level_01), his head normal 3.9 - at the
cheek view's 34 px/mm neither draws a pore's edge; his crispness is his 388 px/mm micro normal (tiled 50x, strength
0.317) of pillowed ~0.6-1 mm cells with finer cells inside, ours thin walls round flat cells (texture-space slope power
at 0.25-0.6 mm: his 51%, ours 15%). The strengths already matched.

**The texture measure corrected.** The 0.06 floor above was his window against itself moved 1.5% - nearly the same
pixels; "about 3x his own floor" overstated the gap. Measured as two samples of skin (`dists.py --patches`: ours
against his beside his against his own; the excess is ~0 for the same texture): his own cheek patches differ by 0.198,
his forehead's by 0.189. Excess (5 patches; a 24-patch grid with a permutation test follows):

| Skin (`.dev/gate/parts/2026-11-07d`) | cheek | forehead |
|---|---|---|
| today's | 0.060 | 0.100 |
| layered tile s0 (`microtile*s0+micro*1.97`) | 0.041 | 0.072 |
| layered tile t1, no per-cell tilt (`microtile*t1+micro*2.686`) | **0.035** | **0.064** |
| s0 + roughness x1.38 (toward his 0.66) | 0.069 | 0.057 |
| s0 + roughness x0.75 | 0.058 | 0.092 |
| s0 + coat x3 | 0.041 | 0.062 |
| s0, the forehead's microrelief at 1/5 (his mask's level) | - | 0.059 |
| s0, our colour set to his | 0.040 | 0.073 |

His own patches split at random against each other: 0.000 +- 0.027 (cheek), +- 0.019 (forehead).

**On a 24-patch grid with the energy test's permutation band** (`dists.py --patches`, features cached - piq's own DISTS to 1e-4): the chance band is +-0.002-0.004, so every row below is a real difference; `--flat` (each patch's light level out - the two faces' shapes) changes it by < 0.007: the excess is texture.

| Skin | cheek | forehead |
|---|---|---|
| today's | 0.047 | 0.107 |
| tile s0 | 0.026 | 0.104 |
| tile t1 (no tilt) | **0.018** | 0.100 |
| s0 + coat x3 | 0.025 | 0.096 |
| s0 + roughness x1.38 | 0.043 | **0.076** |
| s0, microrelief at 0.4 (the forehead's x5 factor toward his mask's 1) | - | **0.074** |

The cheek: the tile closes ~60% of its gap; the forehead: the tile barely moves it (the 5-patch table above said 0.072 - its patches sat lower), its two levers are roughness toward his and the microrelief toward his mask - tried together in the t1 batch. **Read:** the tile
is the one clear gain; the cheek with t1 sits inside his own chance range, the forehead does not; colour is not the
gap. His shine read at each pixel (`shine_probe.py`): roughness 0.66, even over face and body; ours 0.37-0.48, flat in
a region - raising ours helps the forehead and hurts the cheek (ours then varies less than his skin: 0.149 against
0.198 patch to patch). Next: the t1 batch (coat, scatter x2 / x3, roughness with deeper pores, the forehead's micro at
his level with roughness, the scans' relief x1.3), scored on the 24-patch grid.

## Night: the rest of the loop (EEVEE against Aaron; RESEARCH §14.9-14.14 hold the details)

| Part | Start of the evening | Now | What moved it |
|---|---|---|---|
| Cheek (excess) | 0.047 | 0.018 | the layered microrelief (shipped) |
| Forehead | 0.107 | 0.021 | the tile + his mask's micro level + roughness 0.50 (shipped) |
| Nose (new view) | 0.171 | 0.053 | micro x1, pores 0.6 (shipped) |
| Back of the hand | 0.085 | 0.047 | the hands' rebuild + the arms' micro x2 (shipped) |
| Torso | 0.052 | 0.049 | the scan's red dots unreddened (shipped) |
| Foot | 0.107 | 0.10 | nothing in our control: no scan relief - Thunk3D's foot (the user's download) |
| Hair back L* (his 20.4) | 27 | 23 | real density 2.2M a m2 and clump 0.1 (shipped; clumping had parted the strands into bare lines) |
| Hair highlights p95 (his 60) | 43 | 37 | open: his light-tipped strands - the shading's shares, tips, melanin only trade mean for highlights |
| Eye | DISTS 0.267 | 0.261 (trials) | open: the lower lid's thick roll is its skin's shape - no film, shine, slider, margin width or carry setting removes it |

Not the lever, measured: HD Aaron's own body shine values (coat 0.10 at 0.35, specular 0.40, base 0.72) on our skin;
his coat values on the face; lower body roughness (it matched his look against his values - rejected).

## Next

The hair's highlights and style (the nape too long, the front taller than his); the lower lid's shape; the smile
(the expression sets' scoring, plan §19.2 item 9); the foot when its donor is downloaded.

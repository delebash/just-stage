# The open items after the scan route — the working doc (read this FIRST after any compaction)

> Kept current at every step (the user's rule: a working doc per job, `save-results-as-they-arrive`). The scan route
> itself: `2026-11-02-scan-skin-base.md`. TASKS: "THE SKIN'S SOURCE" / "THE SCAN ROUTE".

## 1 · The go

The user, verbatim (2026-11-03): "keep going on the open items, go" - on the open items listed after rounds 74-79:
(a) the sharper face (2K hero, a denser face texture); (b) stubble as a per-character setting; (c) each character's
face from its own painting - true variety needs varied paintings and shapes; (d) the base's own eye / nostril / lip
shading (hidden under the painting now). Under a finish-everything go I decide each choice myself, argued
(`decide-and-finish`), and record it here and in TASKS.

## 2 · What we already have (coverage map) and the picks

| Item | Our research / spec says (file:line) | Pick (attacked) |
|---|---|---|
| (b) stubble | MetaHuman's texture index has stubble as a control (RESEARCH skin §2.1, TASKS:926); CC5 SkinGen layers; no tool derives it from scans | in `skin_base`: each scan tagged with its sex and whether it has stubble (seen at 1:1, research file's tables); `compose` takes the character's sex and a stubble amount; the pores come from scans of its sex first, a smooth scan fills before a stubbled one; on a stubbled scan's fine layer the small dark marks (its black top-hat) in the beard and scalp regions are kept by the stubble amount. Regions from our head's own geometry (fixed topology). Covered by the skin-base builder's NOT STANDARD word. Attack: pores in the beard area thin out at stubble 0 - acceptable, a shaved face shows follicles less than pores elsewhere anyway; a full beard is hair (the groom system), not skin |
| (c) variety | the face test's clay stage takes `head.set_identity(seed, strength)`, `body.create(gender)`, `skin.set_tone(melanin)` (`test_face_clay.py:62-66`); the paintings from `face_paint_seq.py`; the base by `compose` | new characters through the whole face test - a different identity seed, sex and tone, three paintings (hero + the two 30-degree views, the approved structure), a base of the same sex and skin type; each character's files kept apart. Attack: card time (~15 min a character, shared with web-4c - ask first); women bald (hair is the groom system's job; the test is skin) |
| (a) sharper face | our spec: tile 1001 "head and neck", max 8192 (`docs/standards/character-data-model.md:186`); FLUX 3 at 2048² fits (355 s, 7,540 MiB) and paints real pores (TASKS ~913); the face texture is the limit at 6.0 texels a mm (round 49), 8192 gives ~12 | the projection at 8192 only where the face views see (the rest from the base at 4096, upsampled) and a 2K hero; every face-test tool audited for 1024-px assumptions first. Attack: the whole head at 8192 would hold ~28M texels x ~20 float64 arrays (~13 GB) - too much beside web-4c's 14-15 GB |
| (d) base's eye / lip shading | hidden under the painting (rounds 77-79) | not now: shows only on a bare base; noted |

## 3 · Where things stand (update at every step)

2026-11-03: (b) DONE; starting (c). The user asked to see the app: JustStage (Blender 5.3 with our template) opened
on round 79's scene (`tools/dev.py blender .dev/facetest/round.blend`), comparison pictures sent.
2026-11-03 later: that session closed by accident; the user saw the grey Solid view. The scene checked in a
background Blender: Cycles on the GPU, camera `cam`, 512x512, all six 4096 face maps on disk; the Shading tab
opens in Material Preview. (c) NOT started - its paintings need the card; web-9e (just-mocap) asked for a card
run, told to wait until the user is done viewing, then "card free" goes to web-9e first.
2026-11-03, the card order agreed with the peers (from the just-stage foreground session, which only opens Blender
windows for the user): 1) the user's Cycles view, 2) web-9e 3-5 min, 3) web-4c's planner test 30-40 min, 4) this
session's FLUX paintings - after web-4c's "card free". (c) is BUILT and waits for the card: `face_character.py`
(amara - a woman in her thirties, dark brown skin; walter - a man in his sixties, light weathered skin, grey stubble;
mei - a young East Asian woman), `test_face_clay.py` takes FACETEST_GENDER / AGE / ETHNIC / IDENTITY /
IDENTITY_STRENGTH / MELANIN, the paint prompts FACETEST_PERSON, `flow_views.View` loads a view's albedo / normals only
if painted, `test_face_project.py` eyes from the three face views with a base and the clay as the comparison where a
view isn't painted, `skin_base compose SEED 'json'` with `pores_first`. The runner clears the working folder (copied
to chars/<name>/ first) - not while the user has round.blend open. Meanwhile: (a) audited (CPU).
2026-11-03: round 79's whole set copied (only copied) to `.dev/facetest/chars/man_a/` (153 files, 379 MB) and the
foreground session told, so it can repoint the user's viewing copy (`round79_rendered.blend` reads the face_*.png
maps by path). The foreground session then packed its nine images into `round79_rendered.blend` (58 MB): clearing
.dev/facetest can't touch it - no "user done" needed. The foreground session has the user's go on a live view and
will edit the skin material (`modules/skin/material.py`), part materials, grooms, the template and later
`test_face_project.py`'s save step (a viewport call + an EEVEE still) - asked to land those BEFORE the runner (all
three characters on one code state) or to wait for "runner done". Agreed: its edits land first - it commits on the
CPU before web-4c's "card free", then takes ~15 min of EEVEE renders on round 79, then sends "edits landed" with the
commit. WAITING for that message only (not web-4c's card free alone). Then: `face_character.py amara walter mei`,
then the (a) test.
Update: the foreground session is running round 80 (its mouth fix and new lashes in `test_face_project.py`, an EEVEE
column, the round scene saved through `core/viewport.py`), then web-4c's round B (~40 min). Start = the later of its
"edits landed" and web-4c's "card free". When the runner starts it re-copies the working folder (then round 80's man)
into chars/man_a - the latest man; round 79's PNGs stay there too.
EDITS LANDED: 9d1a0b7 (the mouth from the hero alone, finer clumped lashes, EEVEE soft shadows, an EEVEE still beside
each Cycles render, the round scene saved as the live view; round 80 verified by the foreground session). Checked
beside mine: the render loop keeps the per-camera size and the clay fallback. Round 79's archive renamed
`chars/man_a_r79/`; the runner writes round 80's man to `chars/man_a/`. WAITING for web-4c's "card free" (round B,
~40 min), forwarded by the foreground session.
After a session restart: the foreground session added e2d31e4 (`parse_paintings.py`: SegFace eye masks on the
aligned paintings, so their eye whites never colour our lids - the pale lower-lid band; reuses scan_skin's SegFace).
It runs round 81 (~7 min) after web-4c's round B to verify them, then forwards "card free". The runner already has
the step (feb6500: after the 30-degree paintings; `eyes_*.png` kept and cleared per character) - out again if round
81 fails.
CARD FREE (web-4c via the foreground session; rounds 81-82 done - the parse step now masks the lower half of each
painted eye only: whole-eye masks gave the upper lid a pale rim). RUNNER STARTED: `face_character.py amara walter mei`
(log: the job tmp `characters.log`); chars/man_a/ gets round 82's man. When it ends: "card free" to the foreground
session (web-4c wants ~50 min next).
First run: amara's clay (64 s), hero painting (101 s) and alignment ok; the 30-degree paintings FAILED - 
`face_paint_seq.composite` sized its picture from the target view's albedo, which an unpainted view no longer loads
(my `View` change) → sized from the view's coverage. Re-run started (all three).
Second run: amara through to the projection, which FAILED (KeyError 'face' in landmarks.json - the foreground
session's mouth-from-the-hero step reads it). Cause: MediaPipe found no face in amara's close hero painting (its
crop cuts forehead and chin); `align_paintings` printed "not found - kept" and went on unaligned. Brighter (gamma
0.8-0.45) and CLAHE copies didn't help; a margin of repeated edges (an eighth of the width) did → both readers
(`align_paintings.landmarks`, `landmarks.points`) retry padded. amara's hero then aligned (the AI had moved the eyes
31 px and the lips 21 px from the clay). Third run started from scratch (her 30-degree views had been painted from
the unaligned hero).
THIRD RUN (`.dev/facetest/chars_check.png`): amara done (932 s), walter done (944 s), mei FAILED at the projection.
- walter WORKS: an older man with deep wrinkles and grey stubble, convincing close, front and 40-degree; the base
  on his scalp fits the painted face.
- mei: her clay close view was EMPTY - the cameras aim at fixed points tuned for the first man, and she is shorter
  (MakeHuman's Asian female proportions): her head below the frame; FLUX invented a face in the empty picture (an East
  Asian woman), the 30-degree views a different woman; no clay face → no alignment → no aligned_marks.json.
- amara: the same camera fault, milder - the close view cut at the mouth, the front / 40-degree views high; a tone
  edge on her temple in the 40-degree view; the painting's features read masculine.
Fixes: the clay cameras aim from each character's own eyes (`FIRST_EYES` = the first man's eye centre, the aims kept
as offsets from it - his framing unchanged; the eyeballs' box centres, as test_face_export_head measured); amara's
description + "soft feminine features". Card handed back to web-4c ("card free" sent); amara and mei re-run when it
returns (~30 min of card). Queue (from the foreground session): web-4c ~50 min → this session's ~35 min (amara, mei;
start on the forwarded "card free", which will name the foreground session's catch-light commit in
test_face_project.py - committed before my run so these characters get it) → the foreground session's ~10 min check.
Run: `face_character.py amara mei`.
CARD FREE (web-4c via the foreground session; 6d541f2 the catch light on the cornea and tearline only - carried, not
verified yet). RE-RUN STARTED: amara, mei (log: job tmp `characters2.log`). When done: "card free" to the foreground
session (its ~10 min check).
RE-RUN RESULT (`.dev/facetest/chars_all.png`): amara properly framed - a feminine face, dark skin; a faint tone change
where her painted forehead meets the base scalp. mei rendered as CHROME: face_albedo all zeros. Cause: the projection's
absolute heights were set on the first man - mei's face sat below the 1.5 m "face zone", the brightness calibration's
median ran over nothing → NaN → every map 0. Fix (d1f4746): the neck fade, the head selection, the face zone, the lip
line (relief option) and the light rig's centre shift with the character's eyes (`_eye_shift`; the first man 0);
`_head_tile` picks its polygons on the rest mesh (hm08's neutral base), the same for every character, so the tile -
and the bases baked into it - stays one. `face_character.py NAME --from STEP` resumes with the character's files put
back. Catch light 6d541f2 verified by the foreground session on mei's eyes. NEXT: `face_character.py amara mei --from
"projected and rendered"` (~14 min card) after web-4c's ~45 min - asked for the slot.
PROJECTION RE-RUN (481 s / 455 s; lowest free RAM 3.8 GB beside the user's CC5): (c) WORKS -
`.dev/facetest/characters_four.png`: four distinct people through one pipeline - the first man (round 82), amara
(a dark-skinned woman in her thirties), walter (an older man, grey stubble), mei (a young East Asian woman); mei's
albedo mean 158 (was 0). Found in them, to fix next: (1) a light band where the painted forehead hands over to the
base scalp (all four, strongest on amara / walter / mei); (2) walter's scalp a little green and blotchy (his base's
mid layer). Then (a)'s test.
Measured (1): along the head's middle line from the eyes up, the painted forehead ~3 cm above the eyes is 10-17%
brighter than the base above it (amara 0.82 / 0.68, walter 0.74 / 0.62, mei 0.72 / 0.64; the step within ~8 mm).
Causes: the carried tone averaged the whole painted face (darker brows and sockets in it), and the base kept the
scans' own broad brightness. FIXED (33efa83): the tone carried from the painting's edge band only (fade 0.5-0.97, or
within ~1.5 cm of where it falls away), and the base divided by its own ~3 cm average (detail only) - Waechter's seam
levelling between the painting and the base; (2) compose keeps skin's hue order (green at most 2% over red, blue over
green). WAITING for the card (~25 min: `face_character.py amara walter mei --from "skin base"`).
2026-11-04: that run (33efa83) changed the base a little but NOT the step (amara 0.82 → 0.67 still). Measured instead
of guessed: `FACETEST_DUMP=1` stops the projection after the maps (CPU only) and saves every 4th texel's fade,
painting, base, trust. mei's forehead: the close views' frames end ~3.5 cm above the eyes - the painting's share fell
from full to none within 8 mm (trust 0.75 → 0.20) - and the "edge band" had taken 13% of the head (the 3D blur counts
hidden cavities beside the features as outside). FIXED (commit after 33efa83): (1) the ramp also on the face's outer
border - above 2.5 cm over the eyes, past |x| 5 cm, below the chin - never round the features (round 76); (2) the edge
band only there; the tone carried 1.5 cm wide, prior 0.005 (offline: 3 cm gave 0.96 at the edge against the painting's
1.20; 1.5 cm 1.10); (3) the base levelled to the painting in that band (a gain carried out, settling to 1). Mei's final
forehead (dump): 1.23 / 1.19 / 1.14 / 1.13 / 1.09 / 1.05 / 1.02 at 1.8-5.4 cm - no step; the temple 0.80-0.85
throughout. Waiting for the card to re-render the three (projection only).
(a) MEASURED on the CPU (FACETEST_SIZE=8192 + FACETEST_DUMP, mei): the free-RAM guard stopped it at 1.7 GB free from
21 GB - the whole head at 8192 needs > ~19 GB, not workable beside CC5 and web-4c. Options: (1) 8K only where the face
views see, the rest at 4K (a rework of the projection's core); (2) the industry's close-up route already in our
shader - the albedo at 4K plus a tiling pore detail (MetaHuman's tiling micro-normal, research skin-detail-shading
:520). Decision rule: in the card slot, `render_close.py 2048` renders the finished 4K scene's close camera at 2048 px;
if its skin holds against the painting, (a) closes without 8K; if soft, build (1).
2026-11-04 RESULTS (card slot; lowest free RAM 9.5 GB): the hairline band GONE in the renders (amara, walter, mei:
`.dev/facetest/characters_hairline.png`); the albedo up the forehead middle line eases smoothly (amara 0.82 / 0.80 /
0.77 / 0.77 / 0.77 / 0.72 / 0.68 from 1.6 to 6.4 cm above the eyes, walter and mei alike - was a 10-17% step in 8 mm).
The 2K close render of mei (`close_2048.png`, crop `close_crop.png`, the painting upscaled beside it): pores, freckles
and fine texture as rich as the painting's - the 4K tile plus the shader's tiling pore detail carry a 2K close-up; the
1024-px painting, not the texture, sets the limit → (a) CLOSED without 8K (decision rule above); a 2K hero + an 8K face
pays only in 4K film close-ups - in IDEAS. Found, open: at 2K the nostril rim shows a bright orange edge (the nostril's
trouble spot - earlier its green rims).

## 4 · Run log (newest last)

- (b) stubble BUILT (`skin_base.py`, `scan_list.py`): every scan tagged `sex` / `stubble` (men scan02, lps, yaro13,
  rudavin, d3d_african_man stubbled; the six women not); `regions()` - beard (upper lip, chin, jaw, throat; 10.7% of
  the tile) and scalp (above the hairline, back and sides above the ears; 18.2%) from our head's geometry measured
  from the eyes, cached `scans/regions.npz`; `compose` takes `sex` (pores from that sex's scans first, a smooth scan
  filling before a stubbled one, the mid layer from that sex's scans), `stubble` and `scalp_stubble` (0-1; women 0);
  on a stubbled scan's fine layer the black top-hat (7-texel ellipse) is lifted by (1 - keep), all but a floor.
  Measured (char 12, fine detail |lum - blur3|): stubble 1 - beard 2.76, scalp 2.40, elsewhere 1.96; stubble 0 at
  floor 0.30 - beard 1.40 (smoother than the face), at floor 0.55 - beard 1.86, scalp 1.63, elsewhere 1.96 → 0.55.
  Crops: `scans/stubble_crops.png`, regions `scans/regions_check.png`. A woman (char 11) took head03a /
  d3d_african_woman / portrait_3130 for her pores, her mid from women's scans.
- (c) BUILT, not run (waits for the card and the user's viewing): see §3; plus `landmarks.py` skips a view without a
  picture and reads each picture's own size (it assumed 1024), and the runner runs it (the iris band reads
  `landmarks.json`).
- (a) BUILT, not run - every face-test tool audited for 1024-px assumptions: `test_face_clay` renders the face view at
  FACETEST_HERO_SIZE (default 1024); `face_paint_cli` paints at the edited picture's own size (PNG header);
  `align_paintings` scales its pixel lengths (warp grid 4 px apart, the seam's 8 / 16 px reaches, the 40 px eye
  search) by width / 1024; `delight_views` its 9-px inset; `view_normals` reads a picture over 1024 at 1024 (its two
  768-px windows cover 1024 only - at 2048 the middle got nothing) and scales the normals up; `test_face_project`
  takes FACETEST_SIZE (default 4096) with its texel lengths scaled (TEXEL = SIZE / 4096: the levelling cell, the
  pad, the pore high-pass), doubles the 4K base for an 8K tile, gives calibration the photo and its points at 1024
  (`_at_1024`: what it was tuned on), and renders each view at its camera's size. All defaults keep today's numbers.
  Why it waits: the face view renders at 1024 px (~4.7 px a mm) - below today's 6 texels a mm - so an 8K tile shows
  only in a 2K close render; the test is a 2K hero + 8192 tile + a 2K render, after (c). Memory at 8192 (~16M head
  texels) to be measured on a maps-only run first.


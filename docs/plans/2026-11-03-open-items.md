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


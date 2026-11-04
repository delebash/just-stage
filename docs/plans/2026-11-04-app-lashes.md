# The app's own lashes — the working doc (read this FIRST after any compaction)

> Kept current at every step. TASKS: "THE CC5-STYLE WINDOW", the 2026-11-04 line ("move the face test's clumped
> lashes into the app's hair module"); under THE WORKING GO (the user, 2026-11-03: "keep working, keep fixing bugs,
> making things better, and building the actual app ... think adverserily on your recs").

## 1 · The job and why

The library's lashes are MakeHuman's pack lashes: measured 2026-11-04 (RESEARCH §1), 99 strands for both eyes, and
at a 256-px thumbnail they vanish. The face test already builds lashes at real counts: `_strand_lashes` in
`tools/face_test/test_face_project.py`.
- 120 upper and 75 lower per eye.
- Measured angles, lengths and the fan from the front.
- Clumps of 4, 12 points each.

They were approved 2026-10-30 as rec 7 ("brows and lashes at real counts (lashes 90-160 upper)"). But they are fixed
world-space curves made for one face, so they don't follow the lid when the shape changes, and the app never got them.

## 2 · The rec, attacked

- **The generator moves into the app (one way per job).** `modules/hair/lashes.py` gets the specs, the clumping and
  the strands. The eye opening (`eye_opening`, `direction`, `angles`, `world_points`, `gaze`) moves from
  `tools/face_test/face_shape.py` to `modules/head/eyes.py`. `face_shape` re-exports those names, so the face test's
  other callers (the occlusion shell, the tearline, the lid key) are unchanged, and the face test's `_strand_lashes`
  calls the app's.
- **Attached to the surface, as every groom is.** Blender's standard hair attachment: the Curves' `surface` is the
  body, `surface_uv_map` is "UVMap", and each curve has a `surface_uv_coordinate`. A Deform Curves on Surface node
  (`GeometryNodeDeformCurvesOnSurface`) carries the strands from the surface's rest position to its current shape.
  Generated on the current shape, each strand is moved into rest space by its root triangle's frame (current to rest),
  the inverse of what the node does.
  - Attack: on a different character, will the roots still sit on the lid margin? hm08's topology is fixed, so the
    triangle is the same; checked by the test, as test_hair checks the pack styles: root to skin.
- **One groom holds both lids (part "eyelashes")**, saved as the library asset "JustStage lashes".
  - Attack: the pack's upper and lower lashes are both "eyelashes", so under one-groom-per-type applying one replaced
    the other (a bug in the library as built today). Fixed by the build: the library's lashes are JustStage's (both
    lids), and the pack's two lash assets leave the library build. `hair.add`'s styles keep them (the API).
- **No new command:** the lashes reach characters through the library, like the pack styles. The generator runs in
  `tools/build_library.py` (a "lashes" section) and in the face test.
- **Regression check without a card round:** the moved generator, given the same body, openings and seed, must give
  the face test's strands point for point before the rest-space step (headless, CPU).

## 3 · Where things stand

2026-11-04: plan written; next the tests (red), then the move.

DONE 2026-11-04 (tests: test_lashes 2, test_body's shared-rest test; with test_hair, test_library, test_head: 23 green).
- **Move.** `modules/head/eyes.py` and `modules/hair/lashes.py` hold the code. The face test's `_strand_lashes` is a
  call into the app, and `face_shape` re-exports the eye helpers. Regression check (Average woman, seed 7): the moved
  generator gives the face test's 390 strands point for point (0.0 mm difference, radii and melanin too).
- **Found: Blender's node turns strands its own way.** My triangle frame put the tips up to 1.9 mm off. Rather than
  copy its frame, `place` measures the node's rigid move of each curve on a probe shape (12 points over 1 mm) and
  inverts it (Kabsch). The lashes now land within 0.0003 mm of where they were made.
- **Found: every character's base mesh was lifted by its own amount.** `stand_on_floor`, MPFB2's `feet_on_ground`,
  lifted 0.8177-0.8203 m per shape. Blender's hair attachment measures from the base mesh, so every groom moved to
  another character landed off by the difference: MakeHuman's own styles 0.7-1.9 mm off a tall or muscular
  character's skin.
  - Fixed: every base mesh is lifted by one constant (0.817743 m, the default macros', where MakeHuman's styles were
    groomed). Each shape's own few millimetres go in a "JustStage floor" shape key, re-set after slider changes, so
    the feet stay on the floor.
  - The evaluated shapes are unchanged. Characters made before keep their lift in the base and work as before;
    library grooms fit them less well (by their own lift's difference, as before the fix).
  - Measured, the root median on the skin, tall / muscular: hedgehog before 0.84 / 0.66 mm, now 0.08 / 0.09; pack
    lashes before 1.88 / 1.36, now 0.28 / 0.27 (the default character: 0.07 and 0.31).
- **Library.** Characters rebuilt on the shared base. "JustStage lashes" (both lids, 390 strands) in Hair/Lashes.
  The pack's two lash assets were removed from the library build, and their two files and thumbnails deleted (my own
  build output from earlier today). Under one groom per type they replaced each other.
- **Seen.** Close eye renders on the Average man (lashes made on the woman, carried over) and the Average woman,
  EEVEE and Cycles (`jl_compare.png`): a fine dark fringe along both lids, following each one's lid.
- **Found, open:** EEVEE's cornea shows the lid skin and the light as blotches on the iris in close-ups; Cycles' eye
  is clean. This is the live view's eye, the next eye item.

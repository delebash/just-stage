# The quality gate, part by part — 2026-11-05 (baseline)

Procedure: [`docs/standards/quality-gate.md`](../../standards/quality-gate.md). The bar: CC5's HD Aaron (TASKS "HD AARON
IS THE BAR"; "THE GATE PART BY PART, HD AARON IN BLENDER THE STANDARD"). The user's words: "it has to be all parts of
body meat quality bar not just skin"; "toe nails too, all body parts"; "dont stop coding unitl you have fixed all
quality issue or determine it cant be dont".

## Set-up

- **The standard:** HD Aaron as the user exported him (CC5's Blender Pipeline plugin, SubD 1, Classic Slick Back and
  Stubble on) and Reallusion's CC Blender Tools 2.4.5 imported him - its EEVEE build for EEVEE, its Cycles build for
  Cycles. CC5 content: a local test, the renders kept out of the repo (§2: Reallusion's content EULA) - they are in
  `.dev/gate/parts/2026-11-05/` (each view, `sheets/` ours left | Aaron right, `numbers.json`).
- **Ours:** built the app's way (`tools/gate/parts_gate.py` `build_ours`): the library's Daniel, the hair library's
  "Short hedgehog" and "Wild eyebrow", the face's ARKit 52 (`juststage.head.add_face_units`); nothing hidden.
- **Same for both:** the app's stage (key, rim, Studio Small 09 at 0.25, AgX), 85 mm, 2048 x 2048, every camera placed
  from anatomy measured on each character (pupils, front teeth, ear, the right hand's and foot's joints).
- **21 views:** front, three-quarter, profile (head and shoulders); face; back of the hair; eye; lips; lip corner;
  cheek; ear; torso; hand; nails; foot; toenails; full body; jawOpen (face, mouth), smile (face, mouth), browInnerUp.
  Expressions: ours by ARKit's names, Aaron's by CC5's as CC Blender Tools maps them (jawOpen 0.5 -> Jaw_Open;
  mouthSmileLeft/Right 1 -> Mouth_Corner_Pull_L/R; browInnerUp 1 -> Brow_Raise_In_L + _R).
- **Engines:** EEVEE done; Cycles (256 samples, OIDN) next.

## Found and fixed on the way

- **Our teeth stayed when the jaw opened** (the face units moved the skin only). Fixed: the teeth part gets the jaw
  units - the lower teeth, their gums and the tongue turn about the jaw bone's head (MakeHuman's `mouth` joint) by the
  angle the unit turns the chin, a driver keeps them in step with the body's key, a refit rebuilds them
  (`face_units.add_to_teeth`; test `test_the_lower_teeth_and_tongue_ride_jaw_open_and_survive_a_refit`).

## The parts (EEVEE) — my reading; the verdict is the user's (§5)

| Part | Ours against Aaron | Reading |
|---|---|---|
| Skin, face | paler and yellow-white where his is pink with red capillaries; painted dark eye bags; at the cheek the pore band (0.06-0.23 mm) equal - 0.92 against 0.97 - but the finest band half - 0.23 against 0.45 | below |
| Skin, body | plain and pale; no muscle relief (his torso's detail halves without his normal map: 0.93 -> 0.47; ours 0.62) | below |
| Hands, feet | smooth, no veins, knuckle or joint creases; pale | below |
| Nails, finger and toe | no nail plate, lunula or free edge - skin-coloured caps | below |
| Scalp hair | sparse clumps (MakeHuman's pack) against dense cards with fine flyaways | below |
| Facial hair | none (no stubble) | below |
| Brows | thick clumped strands against fine single hairs | below |
| Lashes | thin, sparse | below |
| Eyes | iris fine; a flat dry white, no lid-margin wetness or catch light; narrow painted lids | below |
| Lips | swollen, dull brown-pink, no lip colour border; a pale gap inside the corner | below |
| Teeth, gums, tongue | lower teeth now follow the jaw; the upper hidden by the lip; to judge in Cycles close-up | open |
| Ears | shape fine; flat colour, no redness or translucency | below |
| Nose | pale inner surfaces show in the nostrils (a fault to find) | below |
| Expressions | the smile weak and lopsided (Faceunits' `mouthSmile`); brows and jaw move | below |

## What Aaron's skin owes to which map (one factor at a time, his cheek, a hair-free window)

| | finest band (< 0.06 mm) | pore band (0.06-0.23 mm) |
|---|---|---|
| Aaron | 0.448 | 0.965 |
| micro-normal off | 0.211 | 0.888 |
| every normal map off | 0.124 | 0.400 |
| + colour blurred (0.8 mm) | 0.099 | 0.124 |
| cavity, specular off (normals off) | 0.126 | 0.435 |
| ours | 0.231 | 0.915 |

(Fine detail = the standard deviation of L* above a 1-px Gaussian; the pore band = between 1 and 4 px; 1024 px over
6 cm. The first measure's central window held his stubble, which swamped it - re-measured above the stubble.) So at
the cheek our pore band already matches; the finest band is what his micro-normal adds - a ~6.8 mm tile of domed
polygonal cells ~0.2 mm across with fine furrows (the skin's microrelief; studied, not used). Rec 18's graph-based
contender (Weiss et al. 2023, `2026-10-30-research-skin-detail-shading.md` §2.2) generates exactly that structure.

## Rec 18 done: the microrelief (2026-11-05)

- **Built:** `tools/make_microrelief.py` - the skin's microrelief generated after Weiss et al. (SGP 2023): Poisson-disk
  nodes 0.3 mm apart, their Voronoi cells as domed plateaus stretched along the line direction, the walls as furrows
  (deeper along it), pores at wall junctions; a 10 mm tileable 16-bit tile, 2048 px. In the skin
  (`modules/skin/maps.py`): a second bump after the pores - the spec's `micro_normal` - 0.035 mm deep.
- **The contenders on our cheek** (`.dev/gate/parts/rec18/`; finest / pore band against Aaron's 0.448 / 0.965): the
  pore tile alone (today) 0.231 / 0.915; the generated tile in place of the pores 0.611 / 0.850 (0.05 mm); the pores
  kept plus the generated tile 0.416 / 0.920 (0.03 mm); as the app now builds it 0.450 / 0.924. The scan tiles made
  earlier (`.dev/gate/relief/`): Ten24's cheek a clean pore network but 4.6 px/mm; the Marigold tiles from HSR0040 and
  the Pexels photo blobs or blur - not used. The pick is mine under the user's "dont stop to ask questions unless
  absolutley necessary" (the rec's gate said the user picks from the side-by-side: the montage is
  `.dev/gate/parts/rec18/`, reversible).
- **Found on the way:** the pores ran on hm08's `UVMap`, which spans 1.1 m a UV unit on the face, 2.1 on the torso,
  1.7 on the forearm and 7.0 on the thigh - the body's pores were 2-6x their size. Both relief layers now run on the
  UDIM layer with each tile's own scale (`MM_PER_UV`), one real size everywhere (test
  `test_the_relief_layers_keep_one_size_on_every_tile_and_the_microrelief_shades`).
- **Still below:** the torso at its view's scale (~0.5 mm a pixel): ours 0.42 / 0.36 against 0.96 / 0.75 - his body's
  normal map (muscle and skin relief; the factor test halves it without), recs 7 + 17; the face's colour (his pink
  and capillaries), recs 2 + 3 + 6.

## Done since the baseline (2026-11-05, later)

- **Nails (rec 14 v1):** each nail's own coordinates on tile 1005 (`tools/make_nail_coords.py`: 20 nails); a plate with
  a curved cuticle edge and rounded sides, a lunula by digit (subtle; rare on toes), a thin free edge, faint ridges, the
  fold's groove, gloss and a raised edge (`maps.py` `_nail_layer`). Reads as a nail now; still squarer and paler than
  Aaron's (`.dev/gate/parts/2026-11-05/eevee_nails_ours_nails3.png`).
- **Brows (rec 8):** `modules/hair/brows.py` - 800 single hairs a brow spread over the brow's band (MakeHuman's
  `wild_eyebrow` gives the region), flowing up at the head and along to the tail with converging rows, lying flat; a
  library asset "JustStage brows"; dressed humans and the library's characters wear them. Close to Aaron's in kind and
  density (`eevee_eye_ours_brows3.png`); his are more arched.
- **Eyes - the opening:** every one of our men had a ~6 mm opening against Aaron's 9.3 (an adult's 9-10): the upper lid
  hid the iris's top third, the pupil and the catch light (no catch light even with the cornea's gloss x4 or the eye
  shell off - `.dev/gate/parts/eyes/`). MakeHuman's own `eye-height2` slider at +1 gives ~8.7 mm; dressed humans and
  the library's characters get it.
- **Skin colour from scans (recs 2, 17; the likeness rule):** HSRD-100 through the scan route (fixed: Z-up OBJs; each
  scan keeps the head its fit was made on); HSR0040's own colour on our man reads as real skin
  (`eevee_face_ours_hsr0040.png`); the composer's delit `low` layer from 2+ scans (`skin_base.py`, `"colour": "scans"`)
  gives a natural face with no painting (`eevee_face_ours_comp503.png`), paler and softer than Aaron - the scans'
  choice and tone next.
- **No user docs** exist in this repo yet (docs/ holds dev, gate, plans, standards) - none to update.

## The fix list, worst first, in the approved order (brief §10)

1. **Skin** - rec 18 DONE (above); then 2 + delighting (scan bases), 3 (tone: his pink and capillaries), 17 + 7 (shared detail; the body's relief from
   scanned bodies - the torso's missing half), 6 (layers: capillaries, ear and lip colour).
2. **Eyes** - rec 12 (wet lid margin, sclera, parallax iris), the lid shape.
3. **Scalp hair** - rec 1 (bounded) then cards for dense styles (rec 11).
4. **Brows, facial hair, body hair, lashes** - recs 8-10.
5. **Mouth, nails, ears** - recs 13-15; the nostril fault found first.
6. **Expressions** - better shapes under the same ARKit names (quality-gate.md §4, item 3).

# Research — the base mesh: is MakeHuman's hm08 the right foundation for CC5-level realism? (2026-11-05)

Why (the user, 2026-11-05 late): "resarch this, you should research anything that might help the overal use instead
of just trying to fix little by little". Two workarounds today had one root cause - hm08 lacks anatomy: (1) the lid
margin (its lower lid's free edge stands up to 3.3 mm off the eyeball, one vertex ring - a dark crevice; sealing that
ring gave a 4-8 px band against HD Aaron's ~36 px; ICT's tearline strip shaded pink stood in for it); (2) the body's
muscle definition (MakeHuman's muscle macro gives bulk, not definition - RESEARCH "Body relief and muscle definition").

## 0 · What we already had (rule 0, read before searching)

| Question | Covered where | Evidence | Our code follows it? |
|---|---|---|---|
| hm08's counts, quads, subdivision | `2026-10-29-research-05-bases-pass2.md` §2 | MakeHuman's topology doc [page]: 14,766 faces, all quads, poles <= 5; body 13,380 vertices | yes |
| Other open bases (MHR, SOMA-X, GNM head, MB-Lab, CharMorph) | same §2, top findings | their repos [page]; counts | n/a |
| Realism of any open base against CC5 / MetaHuman | same, finding 7 | "still unsourced"; a photoreal MakeHuman example "needed a custom eyelid target" (Polito thesis) | - |
| HD detail (CC5's HD morphs) | `docs/standards/character-data-model.md` §1.4 (APPROVED 2026-10-29, NOT STANDARD N3) | an HD slider = a displacement map at subdivision level 2, faded by the slider | not built |
| Whether hm08 has lid-margin / caruncle geometry | - | - (measured today: no) | - |
| A better topology under MakeHuman's sliders | - | - | - |

Gaps researched below: the last two rows. Body definition is the approved HD-slider design (a researched rec never
built), not a research gap.

## 1 · Queries run and what they returned (standard mode)

1. "best open source realistic human base mesh topology eyelids mouth CC0 2026" - Blender Studio's Human Base Meshes
   (CC0, CG Channel 2023; devtalk asset tracker), a Fab listing "derived from the MakeHuman CC0 base" naming eyelid and
   lip parts (unread), OpenGameArt low-poly bases (dated).
2. "MakeHuman proxy custom topology high poly realistic face eyelid MPFB" - MakeHuman's proxy concept pages
   (static.makehumancommunity.org: "a 'proxy' (also known as 'proxymesh' or 'topology') is an alternative mesh topology
   that can be applied to a human model"; made "as full body clothing", the `.mhclo` renamed `.proxy`; refit when the
   base changes); an MPFB2 issue on per-topology morph targets. No tested high-poly-face proxy found.
3. "Blender Studio Human Base Meshes CC0 topology realistic head" - CG Channel and 80.lv (2023): "closed volumes with
   clean quad topology", multi-resolution detail, UVs; Blender 4.0 release notes: an update with "improved topology".

## 2 · Blender Studio's Human Base Meshes — downloaded and inspected

- Downloaded 2026-11-05: `human-base-meshes-bundle-v1.4.1.zip` (50.6 MB) from Blender's demo-files page
  (www.blender.org/download/demo-files/ -> mirror.blender.org/demo/asset-bundles/human-base-meshes/), in
  `.dev/downloads/blender_human_base_meshes/`. Licence from the file's own asset metadata [file]: "Eye - Realistic"
  CC0 (Dan Ulrich), "Foot - Realistic" CC0 (Dan Ulrich), "Eye - Stylized" CC0 (Julien Kaspar); the realistic heads and
  bodies carry no per-object metadata - the bundle is published as CC0 (CG Channel [article]; the bundle page itself
  unread - read before anything ships).
- Contents [file]: realistic head for animation (3,242 vertices, Multires 1 level, separate sclera 546 v and iris 400 v
  per eye), realistic head for sculpting (3,307 v), realistic male and female bodies (female 10,582 v, Multires),
  realistic hand, foot (Multires), jaw, skull, skeleton, eye; stylized and primitive sets.
- **The realistic animation head's eye region [rendered, `.dev/gate/parts/proof_eyes/hbm_eye.png`]: a modelled lid margin - two to three
  tight edge loops make a thick margin band on both lids, turning in toward the eyeball - and a dense pocket of loops at
  the inner corner (the caruncle's place).** hm08 has one ring there. Its lips have proper loops (`.dev/gate/parts/proof_eyes/hbm_mouth.png`).

## 3 · Open (the next step's questions)

- Can that head sit under MakeHuman's sliders? Two routes: (a) MakeHuman's own proxy system (`.mhclo` / `.proxy`, the
  standard - our parts already fit this way: `core/mhclo.fit`); (b) MakeHuman's CC0 targets transferred onto the new
  topology by a wrap (our NICP tools) - a new base with every slider. Unknown: how well an mhclo fit holds fine lid
  geometry when the eye sliders move; what our skins (in hm08's UDIM layout) need - a re-bake onto the new UVs.
- The bodies' Multires detail: how much muscle definition they hold (a source for HD sliders).
- The Fab listing's licence and contents; MB-Lab / CharMorph eye regions; Anny's topology.

## 4 · Audit sheet 1 (2026-11-05, measured: `.dev/gate/parts/audit/sheet_eye.png`, `sheet_mouth.png`)

hm08 at level 1 (53,514 vertices with helpers) beside CC5's HD Aaron as exported (SubD 1, 56,412 body vertices), the
same Blender stage, flat grey with each mesh's own edges drawn (Blender's Wireframe node): **the two meshes are about as
dense at the same level** - similar triangle sizes round the eye and mouth. The difference is anatomy and shape: Aaron's
lids are thick flaps - a real upper-lid margin and a lower-lid ledge - set back round a recessed eyeball; ours are thin
edges with the eyeball forward. His lip line has a deep crease into the corners; ours is as dense, flatter. So the fix
is modelled anatomy (loops that make the margin's two edges and its lining, and the shape that sets the eye back), not
more polygons. (His face is a sculpted character; the same-shape comparison - his topology and ours on one face - is
still to do.)

## 5 · Audit sheet 2 (2026-11-05, measured: `.dev/gate/parts/audit/sheet_regions_a.png`, `_b.png`)

The gate's anatomy-placed views (profile, ear, lips, hand, foot, torso), hm08 at level 1 against Aaron's SubD 1 export,
flat grey with each mesh's own edges, hair hidden on ours: **density again alike** at the same level. The differences
are sculpted shape and anatomy: Aaron's hand has knuckles, tendons and modelled nail beds, ours smooth tube fingers;
his toes have nail beds and toe pads, ours rounded blobs; his torso a sculpted athletic figure (a character choice,
partly); ears comparable (his deeper concha); lips comparable at this view (his stubble groom hides the line). So
beyond the eye's lid margin and the lip crease, hm08's gaps are mostly SHAPE at level 0 / detail at levels 1-2 (hands,
feet, nails) - sculpt and HD-detail work on the existing topology, plus nail-bed loops to check.

## 6 · Slider resolution, first pass (2026-11-05, measured; PRELIMINARY)

The scan route's 20 fits (`.dev/facetest/scans/*/fit.npz`: our head at subdivision level 1, wrapped by NICP onto each
real scan; `dist` = each vertex's distance to the scan), per region, median over the 20 scans (p50 / p90 mm): eyes
2.03 / 19.08, nose 1.04 / 7.84, mouth 1.13 / 4.54, cheeks 0.80 / 7.73, forehead 0.74 / 2.10, ears 1.76 / 4.68. **Not
yet usable to rank regions:** the eye region's p90 is inflated by hidden vertices (socket lining, eyeball parts) that
no scan shows - the three scans with closed, clean eye surfaces (lps, scan02, rp_carla) give eyes p90 1.8-2.2 mm; the
nose's p90 likewise by the nostrils' insides; the NICP's stiffness and scan holes add to all. Next: the same on the
visible surface only (vertices seen from the gate's front and three-quarter cameras), and on level 0 with sliders only
(the honest "can the sliders reach this face" number).

**Second pass - the visible surface only** (vertices seen from the gate's front and both three-quarter cameras,
ray-tested against the head; median over the 20 scans, p50 / p90 mm): nose 0.91 / 2.42, mouth 0.99 / 1.91, cheeks
0.85 / 2.07, forehead 0.75 / 2.28, ears 1.63 / 4.43; the eye region split by distance from the eye's centre - within
15.5 mm (against the eyeball) 0.91 / 2.32, **the lid ring 15.5-24 mm (lids, margin, fold) 0.96 / 14.66**. Even with the
fit free to move every vertex, a tenth of the visible lid ring stays more than 14 mm off real lids; elsewhere hm08
follows real faces within ~2 mm (ears 4.4). **The lids are where hm08's topology can't take a real face's shape** -
the measured case for lid anatomy in the base. (Three scans with clean, simple eye surfaces - lps, scan02, rp_carla -
fit the whole eye region within ~2 mm p90; the HSRD scans with open, real lids 9-10 mm.)

## 7 · Build step 1, the lid prototype (2026-11-05, measured; scratchpad `lid_proto.py`, renders `.dev/gate/parts/audit/lid_proto_*`)

- **Finding the lid-edge loop:** the edges between skin faces facing away from the eyeball and socket faces facing it,
  near the eye. Threshold 0.15 on the normal-to-eye dot: 19 edges / 22 vertices an eye (three corner edges missed - a
  folded flap at the inner corner after shaping); 0.05: open ends; **0.0: closed (46 edges / 45 vertices left, 44 / 43
  right) with one branch point each - to trim.**
- **The cut:** Blender's subdivide on the 88 edges crossing that loop (one cut each) adds **88 vertices, appended after
  the 19,158** (every old index kept), faces 18,564; all 60 shape keys carried and interpolated.
- **Before shaping (shaped mesh, mm off the eyeball, p10/50/90):** old ring 0.19 / 0.75 / 2.16; new loop, socket side
  -0.63 / 0.51 / 1.70; new loop, skin side 0.73 / 1.25 / 2.58.
- **Shaped** (each vertex moved along its own line from the eye's centre; the move added to the basis and every shape
  key so their offsets stay): lash line 2.0, margin 1.1, eyeball rim 0.25 mm on all 44 triplets; 76 rim edges creased
  0.6. In flat grey the lid now hugs the eyeball - the crevice gone.
- **Blink** (MakeHuman's `eyeBlinkLeft/Right` at 1): the new eyeball rim stays 0.3 mm off at the median (min -0.16 mm);
  the closed lids' gap 2.0 mm median, 3.1 max - **and the original mesh's lid edges leave the same 2.0 mm (max 4.0)**: the
  face unit's blink doesn't close from our opened eye (EYE_OPEN). The gap belongs to the blink shape (build step 3,
  expressions), not the new loops.
- **Next:** trim the branch, re-shape on the closed loop, render subdivided with the margin tinted, measure the band
  against Aaron's (~36 px at the gate's eye view).

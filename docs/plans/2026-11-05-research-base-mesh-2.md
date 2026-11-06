# Research - the base mesh, pass 2: moving sliders between topologies, production topology, other open bases, UV layout (2026-11-05)

Feeds the base-mesh decision (`2026-11-05-base-mesh-first.md` Phase 2): (A) hm08 + appended loops, (B) Blender Studio's CC0
realistic base with MakeHuman's sliders wrapped on, (C) a new topology of our own with all sliders transferred, (D)
MakeHuman's proxy system. Gaps researched: only the four in the brief. Evidence marks: **[page]** page read, **[snippet]**
search snippet only, **[code]** code read, **[file]** file downloaded and read, **[API]** API record or a live Blender query,
**[inferred]** my reasoning or arithmetic.

## 0 · What we already had (rule 0, read before searching)

| Question | Covered where | Evidence |
|---|---|---|
| hm08 counts, quads, helpers, MHCLO format | `2026-10-29-research-05-bases-pass2.md` §2; spec `character-data-model.md` §1.1 | page, file |
| MHR, SOMA-X, GNM, MB-Lab sizes (inferred), CharMorph's Reom morph counts | same §2 | page; MB-Lab counts were file-size inferences |
| Transfer tools list (Surface Deform, ShapeKeyWrap, ShapeKeyTransferBlender, mesh-expression-retargeter, Sumner-Popovic DT in MIT numpy, EBFR) | `2026-10-31-audit-face-edits.md` §1.3; `RESEARCH.md` ~2198 | API, READMEs |
| Robust Skin Weights Transfer (MIT), trimesh Amberg NICP (MIT, our wrap) | `2026-10-29-research-07-building-blocks.md`; `libs/wrap/gnm_to_hm08.py` | page, file |
| Blender's CC0 Human Base Meshes v1.4.1 downloaded; head 3,242 v with a 2-3 loop lid margin and an inner-corner pocket | `2026-11-05-research-base-mesh.md` §2 | file, rendered |
| hm08 vs HD Aaron density alike at SubD 1; anatomy and shape differ (lid flaps, lip crease, knuckles, nail beds) | same file §4-5 | measured |
| Slider resolution: hm08 follows real faces within ~2 mm p90 except the lid ring (p90 14.66 mm) | same file §6 | measured |
| CC5 / MetaHuman counts (17,683 polys at SubD 0; MetaHuman head LOD0 24,000 v, 669 shapes) | `2026-10-29-research-02-cc5-pass2.md`; `RESEARCH.md` | page |
| CC UDIM tiles 1001-1006; our UDIM = hm08 islands packed per region; a chest seam defect | `RESEARCH.md` ~164, ~278 | measured |

Not covered before (this pass): how CharMorph's / Anny's / MakeHuman's / Surface Deform's transfers actually compute;
the quality limits of each on lids and lips; topology rules for the lid margin, caruncle, mouth, nose; the other open
bases' real counts; seam placement.

Search-mistake check (memory `search-mistakes`): a - licence quoted beside each item, never filtered; b - every verdict
marked, snippets marked as such; c/d - piloted three plain queries, read hits, then narrowed; e - first queries in plain
words; f - "anything better than" run for MakeHuman, CharMorph/Surface Deform, Blender's base meshes; g - map above from
passages; h - all four gaps in one pass; i - no gate pending; j - Maya's standard tool for option A found; k - no
filters in any query; l - no agents used; m - picks go to RESEARCH via the caller; n - on-disk assets checked (ICT, MPFB2
source, Blender, Aaron) before claiming.

## Top findings

1. **CharMorph's "alternative topology" is a fixed sparse averaging map, not deformation transfer** [code]. Each
   new-topology vertex is bound to its 16 nearest base vertices (weight (1 - d/dmax)/d), plus the nearest base-face
   points within 0.75x that distance (barycentric weights), plus base vertices that project onto the new faces within
   min(largest bind distance, 0.125 units) (reverse projection); weights under 1/32 of the largest are cut, the rest
   normalised (the "Soft" binder; a "Hard" option starts from the nearest face instead, a UI choice). Every slider then moves a new
   vertex by the weighted average of the base vertices' displacements; at "finalize" every expression goes through the
   same map, and skin weights too. No local frames, no gradients. Consequence [inferred]: nearest-in-3D binding crosses
   the closed lid gap and the lip seam, so a margin vertex can average upper- and lower-lid motion; new anatomy only
   follows hm08's motion. - [lib/fit_calc.py](https://github.com/Upliner/CharMorph/blob/master/lib/fit_calc.py),
   [morphing.py](https://github.com/Upliner/CharMorph/blob/master/morphing.py), [finalize.py](https://github.com/Upliner/CharMorph/blob/master/finalize.py) (GPL-3).
2. **MakeHuman's proxy (option D) uses world-axis offsets, and refits only on demand** [code][page]. MPFB2 places each
   proxy/clothes vertex at w1·v1 + w2·v2 + w3·v3 + an offset whose x/y/z are scaled by three body measurements (distance
   between two reference vertices per axis); the offset never rotates with the surface [code,
   `services/clothesservice.py` ~200-266 in our MPFB2 copy]. MPFB's FAQ: "the basemesh indeed does change with the
   sliders, but since it is hidden by the proxy, the change is not visible" - fixed by "refit assets to basemesh" or
   "auto refit", which may be slow with dense meshes [page]. A lid-margin vertex 1.5 mm off its base face, on a lid
   turning ~45° in a blink, lands up to 2·1.5·sin(22.5°) = 1.15 mm wrong [inferred arithmetic].
3. **Blender's Surface Deform does rotate offsets with the surface; Data Transfer can't move positions** [code][API].
   Surface Deform binds each vertex to nearby target polygons (tri, n-gon or centroid weights, falloff power, default 4)
   and stores a distance along the polygon's normal, re-applied along the moved polygon's normal
   ([MOD_surfacedeform.cc](https://projects.blender.org/blender/blender/src/branch/main/source/blender/modifiers/intern/MOD_surfacedeform.cc)
   ~1370-1420). Data Transfer (Blender 5.3 RNA, queried): vertex groups, bevel weight, colours; edges; custom normals,
   colours, UVs; smooth flags - no shape keys or positions.
4. **Anny (NAVER, Apache-2.0) moves MakeHuman's blend shapes and skin weights to other topologies by closest-point
   projection and barycentric interpolation** - `apply_retopology_from_mesh`: "projecting target vertices onto a source
   mesh to compute barycentric coordinates", then "interpolating blendshapes and skinning weights barycentrically"; its
   `soma` topology goes through a wrapped `SOMA_wrap.obj`; `smplx` is "non-commercial use only" [code][page]. -
   [model_transforms.py](https://github.com/naver/anny/blob/main/src/anny/models/model_transforms.py), [README](https://github.com/naver/anny).
5. **Plain deformation transfer fails at lids and mouth corners; the known fixes are contact steps** [page]. Saito's
   patent US9202300B2 (Marza Animation Planet, granted 2015-12-01, "Active", anticipated expiry 2034-06-19 per Google):
   deformation transfer "is not contact-aware, which for facial blendshapes causes eyelids to penetrate, or not shut
   completely" and "is not smoothness-aware, often yielding crumpling artifact where the mesh is extremely concentrated";
   its fix (virtual triangles + a weighted Laplacian term) is patented - [Google Patents](https://patents.google.com/patent/US9202300B2/en).
   OmniFaceRig (Meta, SIGGRAPH Asia 2026): sparse Sumner-Popovic transfer, eye regions inset round "virtual eyeball
   centers" before transfer, then "upper eyelid vertices are snapped to lower lids and edge-relaxed for closed-eye
   shapes", and a teeth-hull SDF penalty (inner-mouth penetration 0.08 % human); whole-rig error against artist rigs MAE
   0.92 mm, Q95 2.71 mm (human) - [arXiv 2606.08043](https://arxiv.org/html/2606.08043) [page, first 100k of 126k chars];
   its dataset is under the "FAIR Noncommercial Research License" [code: repo LICENSE].
6. **Option A has an industry-standard precedent: Maya's "Bake Topology To Targets"** - "make changes to the topology
   of the base object and then propagate those changes to all target objects" [page,
   [Autodesk help](https://help.autodesk.com/cloudhelp/2017/ENU/Maya/files/GUID-FD9D539B-BEC0-4F2F-B4E1-E96AFC88756B.htm)];
   a 2018-19 tech-artists thread on adding an edge loop after blend shapes settled on it [page,
   [tech-artists.org](https://www.tech-artists.org/t/maya-modifying-topology-i-e-adding-edges-after-the-blendshape-set-up-am-i-screwed/10708)].
   Older Maya help warns of "vertex swapping on dense meshes where vertices sit close together" [snippet].
7. **No source gives loop counts for the lid margin, caruncle, mouth bag or nasolabial fold** [searched: queries 2, 14,
   15, 18, 20, 21]. The best written rules are Reallusion's CC face topology guide [page]: outer rim on "the absolute
   outer edge of the subject's eyelids", inner rims "mapped to the inner edges", rims "can be occluded (placed slightly
   inside the eyes) if needed to improve animation", "The tear-line should hug the shape of the eyeballs", the lacrimal
   caruncle "properly positioned and sized"; lip inner edge = "the inner visible boundary of the lips" when open, not
   pulled into the mouth; nostril crease at "the deepest, most recessed part"; and Epic's: cardinal loops ("all the
   various folds, the eyelids, the ridges of the ear") keep their meaning - "A neighboring loop can't be used instead"
   [page]. Counts must come from measuring the references we hold (Blender's CC0 head, ICT-FaceKit, HD Aaron, MetaHuman's
   `SKM_Face.dna`).
8. **Density: CC5 animates a cage like hm08's; MetaHuman's face is ~5x denser; Blender's CC0 head is coarser than
   hm08's** [measured earlier + inferred]. hm08 level 1 ≈ HD Aaron SubD 1 round eye and mouth (audit sheet 1); MetaHuman
   head LOD0 24,000 v vs hm08's head tile 4,986 v; Blender's realistic animation head 3,242 v at level 0 (body 10,582 v
   vs hm08's 13,380). Option B lowers level-0 slider resolution everywhere except where its loops are better placed.
9. **Other open bases, counted** [file]: MB-Lab female 18,210 v / 17,288 quads (AGPL-3 file in its folder); CharMorph's
   Antonia 36,030 v / 35,990 quads ("Creative Commons Attribution 3.0 Unported"); Reom 8,434 v ("license: CC-BY"), ships
   a `Tearline` asset and a `Reom_CaruncleMask.png`. None has sliders beyond its own morph set (MB-Lab ~470, AGPL).
   A Fab pack "Derived from the MakeHuman CC0 base" ($4.99, ~71k / ~22k-vertex meshes, 50+ parts incl. eyelids and
   lips) shows no licence in its licence field [page]. Ben Morgan's Head Base Mesh ($6.49, 4,338 v, "eyes have
   caruncles", "Eye and Mouth bags", "Creative Commons" variant unstated) [page]. Blender Studio's Einar ("the Studio's
   first attempt at a realistic character", CC-BY, 553 MB) [page].
10. **UV: CC merges head and neck in one tile; MetaHuman splits head and body meshes at the neck and fights the seam in
    shading** [page][snippet]. CC: "merged in one UV for enhanced scan head and animated blend-map", UV space
    "Enlarged … for face, nose, hand, and nail" [page, Reallusion manual]. MetaHuman: head and body materials differ
    (Bent Normal on head, off on body - Epic's reply: the body "intentionally lacks a bent normal"; fix: fade it to flat
    toward the neck) [snippet, Epic forums]. Practice: face on one tile; seams under the chin, behind the ears, back of
    the skull, inner limbs, armpits; density set by the closest shot [snippet, Polycount and others].

## 1 · Moving 1,000+ morph targets, weights and UVs to another topology

### 1.1 How each method computes (read in code or docs)

| Method | How it computes | Local frame? | Evidence | Licence (label) |
|---|---|---|---|---|
| Barycentric projection (Anny `apply_retopology_from_mesh`; MorphBridge) | project each new vertex onto the old surface; every target delta and weight = the 3 corners' barycentric mix; MorphBridge adds optional Laplacian smoothing of deltas ("recommended 1-5" iterations) | no (vertex on the surface) | [code] Anny; [page] MorphBridge docs | Anny Apache-2.0; MorphBridge GPL-3.0, $12.50 |
| CharMorph alt-topo binding | §Top 1: kNN-16 inverse distance + nearest faces + reverse projection, normalised; applied to every morph, expression, weight | no | [code] | GPL-3 code |
| MakeHuman MHCLO / proxy | 3 vertices + weights + world-axis offset scaled by three body measurements; refit on demand | no (offset in world axes) | [code] MPFB2; [page] FAQ | GPL-3 code, CC0 data |
| Blender Surface Deform (apply per shape key: ShapeKeyWrap etc.) | polygon-weighted point + distance along the moving polygon's normal | **yes** (normal) | [code] Blender | GPL (Blender); ShapeKeyWrap GPL-3 |
| Maya Bake Topology To Targets | edit the base's topology, push it into each target | n/a (same mesh edited) | [page] Autodesk | Maya (paid) - method reference |
| Deformation transfer (Sumner & Popovic 2004) | per-triangle deformation gradients copied through a correspondence, Poisson solve | **yes** (gradients) | existing; [page] patent and OmniFaceRig on its failures | method; MIT numpy and BSD-3 C++ implementations (existing) |
| Saito's smooth contact-aware DT | DT + virtual triangles over open areas + weighted Laplacian | yes | [page] patent | **patented, active to 2034** |
| OmniFaceRig | keypoint registration to a template, sparse DT, inset eye centres, lid snap + edge relax, teeth-hull SDF penalty, Delta Mush blend | yes | [page] arXiv | method published; dataset FAIR Noncommercial |
| R3DS / Faceform Wrap | wrap the template onto the target (point pairs, non-rigid fit; prior research), Match Topology (2021.11), DeltaTransfer node (2025.11) "transferring deformation deltas from one neutral mesh to another" | not documented | [page] CG Channel; algorithm unread | paid: Indie $570, Pro $1,070 node-locked |
| NFDT (Disney, EG 2025 short) | decoder-only transformer, trained on synthetic template/target pairs; "good results across varying mesh topologies" | learned | [page] project page; no code or numbers stated | no release found |
| NFR (SIGGRAPH 2023) | learned face codes drive any mesh | learned | existing (`2026-10-30-research-all-functions.md`) | MIT code, weights' terms unclear |
| Neural Jacobian Fields (2022) | predicts per-triangle Jacobians, Poisson solve; used for DT between triangulations | learned | [snippet] | Adobe research |
| Faceit | not a transfer: builds a face rig "with the same structure like the Rigify face rig" on the mesh, then bakes expressions | - | [page] Faceit docs | paid |
| Blender Data Transfer | vertex groups, UVs, normals, colours only | - | [API] Blender 5.3 RNA | GPL |

### 1.2 Quality on fine regions (what is known)

- **Numbers found:** OmniFaceRig whole-rig vs artist rigs MAE 0.92 mm / Q95 2.71 mm (human), penetration 0.08 % [page];
  our NICP wrap GNM → hm08 0.87 mm mean (existing). No source gives lid- or lip-specific numbers for any method;
  NFDT reports a user study and "quantitative evaluations" without numbers on its page [page].
- **Known failure modes:** DT not contact-aware - lids penetrate or don't shut - and crumples where the mesh is dense
  (lids, mouth corners) [page, patent]. Pure transfer "can move the outer face surface through the inner-mouth
  geometry", especially AU12 [page, OmniFaceRig]. Projection methods: "Extreme pose differences or non-overlapping
  surfaces produce poor results" [page, MorphBridge].
- **Where every projection method breaks for us** [inferred]: identity sliders transfer almost exactly between two
  topologies that share one neutral surface - except where the new topology has surface the old one lacks (the lid
  margin's inner face, the caruncle, a mouth bag). Those vertices project onto the nearest hm08 face - often the wrong
  lid or lip. These are exactly the regions a new topology is wanted for. Fixes: bind by region (upper-lid vertices only
  to upper-lid faces - a mask per region), local-frame offsets (Surface Deform's normal distance), and a contact step per
  closing expression (OmniFaceRig's snap and relax).
- **Do face units survive?** Identity sliders: yes with any method on a shared neutral [inferred]. Expressions (blink,
  lips together, jawOpen): only with a contact step; none of the methods closes lids or seals lips by itself [page,
  patent + OmniFaceRig].
- **Weights and UVs:** weights through the same map (CharMorph, Anny) or Robust Skin Weights Transfer (existing, MIT);
  UVs come from the new layout - every texture and mask re-baked (Blender's Selected-to-Active bake, existing practice).

### 1.3 What option A needs from this

The appended vertices are born on hm08 faces, so their slider deltas are the face's interpolation - the same math as
Anny's barycentric transfer, applied to a few hundred vertices instead of all. The two gaps are the same as everyone's:
(1) a born vertex moved off its face (the margin turned in toward the eyeball) needs its offset stored in the face's
frame, not world axes - Surface Deform's normal distance is the standard pattern [code]; (2) closing expressions need the
contact step. Blender's edit tools interpolate shape keys for new vertices (the plan's prototype); Maya's Bake Topology
To Targets is the industry tool for the same job [page].

## 2 · Production topology for a realistic animatable head and body

| Region | What sources say | Evidence | Our state |
|---|---|---|---|
| Lid margin | outer and inner rims mapped to the lid's outer and inner edges; rims may sit "slightly inside the eyes"; lid edges "vertically smooth" (topology checker) | [page] Reallusion face guide | hm08: one ring (measured); Blender CC0 head: 2-3 loops (rendered); Aaron: thick flaps (audit 1) |
| Lid crease and fold | upper crease loop aligned to the subject's crease; Microsoft-topology research keeps the crease "represented with the same edge-loop across all meshes" and pinches the loops round the fold with a blendshape for hooded eyes | [page] Reallusion; [page] arXiv 2410.13760 | unmeasured on hm08 |
| Caruncle / lacrimal | "properly positioned and sized"; tear line "hug[s] the shape of the eyeballs"; MetaHuman models it as separate meshes (`cartilage`, `eyeEdge`) | [page] Reallusion; existing (MetaHuman names) | hm08: none (measured); Reom ships a caruncle mask; Ben Morgan's head "eyes have caruncles" |
| Eyelid support | "proper supporting topology to deform the eyelid around the eyeball"; else lids "clip through the eyeball or be visibly far from it"; model lids half-closed to set the loop count | [snippet] Polycount | hm08 lid ring p90 14.66 mm off real lids (measured) |
| Lips, inner lip | inner edge = visible inner boundary, not deep in the mouth; even spacing so lips don't offset when corners droop; corners "tend to intersect"; Softimage docs: corner the most complex part, inner lip continues the outer lip's flow | [page] Reallusion; [snippet] Autodesk Softimage | hm08 lips comparable at view (audit 2); crease shallower (audit 1) |
| Mouth bag | no written rule found; MetaHuman requires the neutral lips "completely sealed" (existing) | searched (q15) | hm08 has a mouth lining (helpers; unmeasured) |
| Nostrils, nasolabial | nostril crease at the deepest point; inner ridge where the shape turns; fold runs nose wing → mouth corner; at least two loops over the nostril (crease + bulge) | [page] Reallusion; [snippet] Polycount | unmeasured |
| Semantics | each cardinal loop serves its feature only ("A neighboring loop can't be used instead") | [page] Epic | - |
| Joints | ≥3 loops across elbow and knee, tighter on the compressing side; circular loops round the deltoid; no poles on bend lines; triangles acceptable where placed well | [snippet] Blender wiki, CG Cookie, ZBrush tip, Blender Artists | hm08 shoulders/elbows need Corrective Smooth (existing) |
| Density | no standard; film heads "tens of thousands of polygons" (marketplace listings); CC5's HD = 4x per SubD level; MetaHuman LOD0 head 24k v | [snippet]; existing | hm08 head tile 4,986 v at level 0, x16 at level 2 |
| CC5 HD rules for custom heads | keep "as close to the neutral mesh as possible"; eyeballs "within the eyelid borders", no gap; check blink and look-down at full strength; wrinkle normals at SubD 1 | [page] Reallusion CC5 HD wiki | - |

## 3 · Other open base meshes

| Base | Counts | Anatomy (lid margin / caruncle / mouth bag) | Sliders / morphs | Licence (quoted) | Evidence |
|---|---|---|---|---|---|
| hm08 (MakeHuman, ours) | body 13,380 v; 19,158 with helpers | one lid ring; no caruncle (measured) | 1,258 CC0 targets | CC0 1.0 | existing |
| Blender Studio realistic head / bodies | 3,242 v head; female body 10,582 v; Multires | 2-3 loop margin, inner-corner pocket (rendered) | none | CC0 (asset metadata; bundle page unread) | existing [file] |
| MB-Lab female / male | 18,210 v, 17,288 quads (female) | unread | ~470 morphs (v1.5.0) | AGPL-3 file in `characters/mb_female/` | [file] npy headers |
| CharMorph Antonia | 36,030 v, 35,990 quads | unread | L2/L3 packed | "Creative Commons Attribution 3.0 Unported" | [file] |
| CharMorph Reom | 8,434 v | tearline asset, caruncle mask texture (geometry unread) | 111 L2 / 51 L3 files (existing) | "license: CC-BY" (config; author ComplexAce, morphs Hope) | [file] |
| Anny (NAVER) | MakeHuman topology (13,718 v existing); also `anny-quads`, `soma`, `smpl`, `smplx` | as hm08 | MakeHuman targets + Face Units (CC0) | code Apache-2.0; data CC0; `smplx` "non-commercial use only" | [page] README, [code] |
| Fab "Human Body Base Mesh - Full Body + Modular Anatomy Parts" (Iqbal Muhammad Yasin) | ~71k v full skin; ~22k v quad base | 50+ parts named incl. eyelids, lips (contents unverified) | none mentioned | licence field "-"; description: "Derived from the MakeHuman CC0 base", public domain claim; $4.99 | [page] |
| Head Base Mesh (Ben Morgan, Superhive) | 4,338 v, 8,642 tris | "eyes have caruncles", "Eye and Mouth bags", "thick mouth corners" | none mentioned | "Creative Commons" (variant unstated); $6.49 | [page] |
| Sketchfab "Human Male/Female Basemesh Rigged" (Niclas) | 18.8k v, 37.3k tris | unstated | rig | "CC Attribution" | [page] |
| Einar (Blender Studio, *Charge*) | unstated | realistic, lip drivers, eyelid displacement maps (comments) | rig | "CC-BY" - "you must give attribution to Blender Studio" | [page] |
| ICT-FaceKit | face 9,409 v; full ~26.7k v | eye occlusion, lacrimal fluid (two-rim ring), teeth, gums | 100 identity + ARKit-named expressions | MIT | existing; on disk `.dev/cache/ict/` |
| GNM head (Google) / MHR (Meta) | 17,821 v / 18,439 v LOD1 | fitting meshes | 253 / 45 identity | Apache-2.0 | existing |
| Audio2Face-3D Mark / Claire / James (NVIDIA) | `bs_skin.npz` per actor | unread | skin + tongue blend shapes | HF tag "nvidia-open-model-license" (terms unread) | [API] |
| OmniFaceRig templates | 3 `rest_template` files | radial loops round eyes and mouth (paper) | up to 155 FACS shapes | FAIR Noncommercial Research License | [code][page] |
| MetaHuman Conform Topology (Fab, named in a forum) / MetaHuman head | 24k v LOD0 | eyeshell, eyeEdge, cartilage, saliva meshes | 669 shapes | MetaHuman EULA (reference only) | [snippet]; existing |
| Microsoft face model (Hewitt 2024) | - | - | - | not released (SynthMoCap is images, landmarks, masks) | [snippet] |

"Anything better than hm08 / Blender's base meshes?" (queries 3, 34): no source compares realism; the community answers
name MB-Lab, CharMorph, Daz, CC (paid) [snippet]. Nothing found that is open, realistic, sliders-included and has a
modelled lid margin together.

## 4 · UV layout for UDIM human characters

- **CC3+/CC5:** UDIM since CC 3.2; head and neck "merged in one UV for enhanced scan head and animated blend-map"; UV
  "Enlarged … for face, nose, hand, and nail"; avoids "head paint affecting the body" [page,
  [Reallusion manual](https://manual.reallusion.com/Character-Creator-4/Content/ENU/4.0/05_Character/UV-Optimizations.htm)];
  "the head UV now includes areas of the neck which helps to maintain head to neck texture continuity" [snippet,
  Reallusion forum]. The exact neck seam line: not on the page (diagrams only) - measurable on HD Aaron's export.
- **CC5 HD texture sizes:** skin base colour and normal 2K/4K/8K per tile (head normal x3 for SubD levels), roughness
  1K-4K, cavity 2K-8K; wrinkle normals at SubD 1 [page, CC5 HD wiki].
- **MetaHuman:** head and body separate meshes and materials; neck seams traced to bent-normal and vertex-normal
  mismatch, fixed by fading the head's bent normal to flat near the neck or copying normals [snippet, Epic forums].
- **Seam placement (general practice):** face on its own island / one tile; cuts under the jaw, behind the ears, over
  the back of the skull (hidden by hair, shows on bald heads); body front/back with seams down the sides and inner
  limbs, at neck, wrists, ankles; hide in armpits and groin [snippet, Polycount, ZBrushCentral, course notes].
- **Texel density:** set it from the closest shot ("figure out what the closest close-up shot will be") and keep
  contiguous shells (the face) at close density; uniform density across all tiles is called impractical by Daz users
  [snippet]. Ours: face 6.0 texels/mm (measured earlier, `RESEARCH.md` ~924); CC5 8K tiles.
- **For us** [inferred]: hm08's UDIM keeps its islands, so its seams are hm08's; the chest band seen on Average and
  Muscular man is a tile-assignment seam crossing visible skin - CC's practice (head + neck in one tile, the cut low
  on the neck / under clothing) is the reference.

## 5 · Queries run and what they returned (standard mode; one line each)

1. "best way to transfer blendshapes to new topology" - mGear Flex (wrap-based), a Blender mesh-deform gist, Maya
   Laplacian tool (same topology only), Wrap Match Topology, paid tutorials.
2. "realistic head topology eyelid edge loops lid margin caruncle" - Reallusion CC Face and Head/Body topology guides,
   arXiv 2410.13760 (eyelid fold), SynthesEyes (arXiv 1505.05916), Blender Artists caruncle advice.
3. "is there anything better than MakeHuman base mesh" - MakeHuman proxy page, alternativeTo/FitGap lists (MB-Lab,
   CharMorph, Daz, 3D-Coat), old forum posts.
4. "MetaHuman head topology documentation edge loops eyelid mouth bag template mesh" - Epic "from template mesh"
   (cardinal loops), forum on per-part topologies, "MetaHuman Conform Topology" on Fab.
5. "CharMorph alternative topology morphs transfer how it works" - CharMorph docs (Alt Topo workflow, faces.npy), no
   algorithm -> code read on GitHub.
6. "deformation transfer blendshapes eyelid closure lips contact artifacts new topology" - Saito patent, OmniFaceRig,
   BSGen (IEEE VR 2023), Onizuka ICCVW 2019, SideFX/tech-artists threads.
7. "R3DS Wrap transfer blendshapes to different topology node" - Toolfarm (403), CGPress, Match Topology node, WrapX.
8. "latest techniques for transferring morph targets between different mesh topologies 2025" - oxihuman-morph
   (nearest vertex), MorphBridge, Mesh Match (Maya), ZBrush Project All.
9. "neural facial deformation transfer different topology 2025 Eurographics blendshapes" - NFDT (Disney, EG 2025),
   OmniFaceRig, BSGen, Onizuka.
10. "Faceit Blender transfer shape keys to different topology how it works" - nothing on Faceit; MorphBridge, forum
    threads.
11. "Faceform Wrap documentation Wrapping node algorithm smoothness control points blendshapes extraction" - only
    Maya wrap-deformer docs (noise).
12. "Faceit documentation transfer shape keys surface deform different topology" - nothing on Faceit -> docs read
    directly.
13. "\"Faceform\" Wrap manual \"Blendshapes\" node transfer topology" - CG Channel Wrap 2024.11 / 2025.11 (DeltaTransfer),
    Toolfarm tutorials.
14. "eyelid topology for animation lid thickness how many edge loops realistic character" - Polycount threads (no
    count), Reallusion guide, CC4 topology page.
15. "realistic character mouth bag topology inner lips edge loops animation guide" - Reallusion, Softimage mouth docs,
    Blender Artists corners, Follygon (paid), no mouth-bag rule.
16. "Character Creator 5 new base mesh topology eyelid HD what changed from CC4" - CC5 HD wiki, CG Channel, Digital
    Production, forum threads (no topology diff published).
17. "Detailed spatio-temporal reconstruction of eyelids Bermano lid margin mesh topology" - SIGGRAPH 2015 paper page,
    patent; no topology detail.
18. "MetaHuman face topology breakdown polycount eyelid loops mouth interior vertex count LOD0" - forum vertex counts
    (34,615-34,617), no loop layout.
19. "how many polygons should a realistic animated head have for close-up facial animation film game cinematic" -
    marketplace listings (~71k polys head), an old patent; no standard.
20. "nostril topology inside nose loops animation realistic head and nasolabial fold edge loop" - Reallusion,
    Polycount (two loops over the nostril), textbook excerpt.
21. "\"Art of Moving Points\" eyelid topology lid thickness face topology for animation" - book not reachable;
    Polycount critique ("some thickness around the eyelids").
22. "Fab base mesh derived from the MakeHuman CC0 base eyelid lips modular" - the Fab listing (read), OpenGameArt 2013
    posts.
23. "free realistic human head base mesh with mouth bag and eyelid thickness animation ready topology download" -
    Superhive / CGTrader / RenderHub paid heads (Ben Morgan's read).
24. "new open source parametric human body model 2026 mesh topology released quads face" - Anny, SOMA, MHR.
25. "MakeHuman community proxy high poly topology realistic face subdivision MPFB" - proxy FAQ, MPFB FAQ ("sliders stop
    working with a proxy" - read).
26. "where to put UV seams on a realistic human character head neck body UDIM so seams don't show" - course notes,
    Polycount, ZBrushCentral.
27. "MetaHuman head body UV seam neck where texture seam blend between face and body" - Epic forum threads (bent
    normal), BG3 modding wiki.
28. "texel density target hero character film close-up face UDIM 8K pixels per cm" - Maxon texel docs (game
    numbers), general articles.
29. "topology-agnostic deformation transfer neural Jacobian fields 2024 2025 shape transfer meshes" - NJF (2022),
    arXiv 2601.06484 (cross-species).
30. "Blender Studio Charge open movie character download rig realistic human CC-BY topology" - Einar, Huginn, Rain,
    Snow pages.
31. "NVIDIA Audio2Face-3D open source 2025 head mesh Mark Claire James license download" - arXiv 2508.16401, news;
    then GitHub/HF APIs.
32. "sketchfab realistic human base mesh subdivision ready free download CC0 CC-BY head body" - Niclas' CC-BY mesh,
    OpenGameArt CC0 low-poly, CGTrader paid.
33. "Microsoft SynthMoCap face model mesh released license Hewitt 2024 \"Look Ma, no markers\" topology" - SynthMoCap
    datasets only.
34. "is there anything better than Blender Studio Human Base Meshes free realistic topology" - CG Channel, 80.lv,
    paid packs; no comparison.
35. "is there anything better than CharMorph alternative topology or Surface Deform for moving shape keys to a new
    mesh" - MorphBridge, ShapeKey Doctor Pro, ShapeKeyWrap, a Diffeomorphic issue (404).
36. "shoulder elbow knee topology deformation edge loops best practice realistic character rigging" - Blender wiki,
    CG Cookie, ZBrush tip, Blender Artists.
37. "Character Creator CC3+ base UV layout head body seam neck location Std_Skin_Head texture seam" - CC3+ base page,
    UV Optimizations manual (read), forum.
38. "UDIM layout human character film VFX how many tiles face head texel density consistency across UDIMs best
    practice Mari" - Polycount, Daz forum, a Reddit mirror.
39. "Maya \"Bake Topology to Targets\" shape editor documentation" - Autodesk help pages (2009-2023; one read).

Pages and code read (beyond search results): Reallusion CC Face Topology Guide, CC Head Body Topology Guide, CC5 HD
Character wiki, CC4 UV Optimizations; Epic "from template mesh"; arXiv 2606.08043 (abs + html to 100k chars), 2410.13760;
NFDT project page; Google Patents US9202300B2; CG Channel Wrap 2025.11; CGPress Wrap; Faceit docs (index, getting
started); MorphBridge docs; MPFB FAQ proxy page, MakeHuman proxy FAQ, mhclo.md; Fab listing; Superhive Head Base Mesh;
Sketchfab Niclas mesh; Blender Studio Einar; Autodesk Bake Topology To Targets; tech-artists thread. Code: CharMorph
`lib/fit_calc.py`, `lib/fitting.py`, `lib/morpher_cores.py`, `morphing.py`, `finalize.py`, `lib/charlib.py`; CharMorph-db
tree, configs, licences, npy headers (Reom, Antonia, MB-Lab); Anny README, `retopology.py`, `model_transforms.py`; MPFB2
`services/clothesservice.py` (our cache); Blender `MOD_surfacedeform.cc`; Blender 5.3 RNA (Data Transfer enums); GitHub
APIs for Audio2Face-3D-SDK (MIT), OmniFaceRig (LICENSE); HF API for Audio2Face models.

## 6 · Couldn't verify

- **Loop counts** at the lid margin, caruncle, mouth bag, nostrils in any written source (queries 2, 14, 15, 18, 20,
  21). Next: count them on the references on disk - Blender's CC0 head, ICT-FaceKit (`.dev/cache/ict/`), HD Aaron
  (reference only), MetaHuman `SKM_Face.dna` (reference only).
- **R3DS / Faceform Wrap's algorithm and the DeltaTransfer node's math** - no official manual reached; Toolfarm 403.
- **NFDT** code, weights and numbers; **OmniFaceRig** full text past 100k characters; per-region lid/lip errors for any
  method.
- **Saito's DigiPro 2013 paper** (same method as the patent) - not searched; the patent status is Google's assumption.
- **Faceit's** internals beyond its docs' getting-started page.
- **MB-Lab, Antonia, Reom eye and mouth regions** - counts only, geometry unread (`char.blend` not downloaded); the
  **Fab pack's** parts (seller text only, licence field blank); **Ben Morgan's** CC variant; **Audio2Face** model
  licence text; **Einar's** counts.
- **Maya's dense-mesh "vertex swapping" warning** - snippet only.
- **docs.blender.org** (403) for Data Transfer - answered from Blender's RNA instead; SynthesEyes PDF unreadable by the
  fetcher; Diffeomorphic issue 1664 404.
- **CC's exact neck seam line** - the manual shows it only as a picture.

## 7 · Assessment of A-D (ASSESSMENT - my reasoning on the facts above, not a sourced finding)

| | Quality ceiling | Cost | Risk |
|---|---|---|---|
| **A** hm08 + appended loops | Fixes the one measured shape gap (lid ring p90 14.66 mm; elsewhere ~2 mm) at CC5's density (hm08 L1 ≈ Aaron SubD 1); every old index, target, UV, mask, weight and fitted part exact; only new vertices are interpolated | low-medium: a loop-insertion tool + per-target extension + local-frame offsets for shaped vertices + lid contact per closing expression | can't relocate a misplaced cardinal loop without reshaping old vertices (allowed: targets are deltas); appended margin vertices on blinks need the Surface Deform-style frame or they err ~1 mm; Maya's precedent shows the method is standard practice |
| **B** Blender CC0 base + wrapped sliders | better-placed lid loops, but a coarser level-0 head (3,242 v) and body (10,582 v) than hm08 - lower slider resolution; all 1,258 targets resampled, and the margin/caruncle surfaces have no hm08 counterpart to project from - the transfer is weakest exactly where B is better | high: every target, weight, mask, part fit and skin re-baked | high: the gain region is the failure region of every projection method |
| **C** new topology to best practice | highest (MetaHuman-like face density, our own loops) | highest: a topology design without published counts, then everything in B | high: same transfer limits as B, plus design time; no written loop standard to aim at |
| **D** MakeHuman proxy | MakeHuman's own route, but offsets in world axes and refit only on demand - fine lid geometry drifts in blinks and on eye sliders; expressions not covered by its docs | medium: re-bakes as B | high for the lids specifically |

My ranking: **A first**, with two conditions the research adds - store each appended vertex's offset in its birth
face's frame (Surface Deform's normal-distance pattern) and give every closing expression a contact step (OmniFaceRig's
snap-and-relax, not Saito's patented virtual triangles). **C** is the only option with a higher ceiling; it becomes
worth its cost only if the Phase 1 audit finds hm08's existing loops misplaced (not just missing) in several regions.
**B** and **D** are dominated: they cost re-bakes and lose exactly where they would gain. What the attack changed: B's
level-0 counts (lower than hm08's) moved it below A on quality, not only on cost.

# The character, redesigned — every piece, verified (for the user's approval, 2026-11-05)

The user, 2026-11-05 (TASKS "THE BASE MESH FIRST; THE WHOLE CHARACTER REDESIGNED"): "really think on the design and make
sure you have it correct and ll the pieces correct, think adverserially multiple times on this desing of the charctaer
and how the pieices fit from mesh to texture to hair to slider to everything"; "please get this correct this time ...
verifying it multple time that it is the correct path". The aim: better than CC5 and MetaHuman, part by part
(`2026-11-05-base-mesh-first.md`, "the best of both").

**How this document is verified before it reaches the user:** every fact marked [page] / [code] / [measured] at its
source, anything else marked unverified; each research agent's file audited (query log, evidence marks, search
mistakes a-n) and its key claims spot-checked; the design attacked in passes - (1) each piece, (2) how the pieces fit,
(3) my own claims, (4) the tests that would catch a mistake, (5) the untouched neighbours - until a fresh pass finds
nothing; each risky choice proved by a small measured test before adoption.

## Facts established today (measured unless marked)

- **Density is not the gap.** CC5's HD Aaron (SubD 1 export, 56,412 body vertices) and hm08 at level 1 (53,514) are
  about equally dense round the eye, mouth, ear, hand, foot and torso (`.dev/gate/parts/audit/sheet_*.png`). CC5's base:
  17,683 polygons at SubD 0 [page, CC5 spec table]; hm08: 14,766 faces.
- **The lids are where hm08's topology fails.** Real scanned faces wrapped onto hm08 (20 fits, visible surface only):
  within ~2 mm (p90) at nose, mouth, cheeks, forehead; ears 4.4 mm; **the lid ring 14.7 mm**
  (`2026-11-05-research-base-mesh.md` §6). CC5 models the lid as a thick flap with a margin and a ledge round a recessed
  eyeball; hm08's lid edge is one ring standing up to 3.3 mm off the eyeball.
- **Elsewhere the gaps are sculpted shape and detail, not topology:** hands (knuckles, tendons, nail beds), feet (toe
  pads, nail beds), torso definition (audit sheet 2).
- **Blender Studio's CC0 realistic head models the lid margin (2-3 loops) and an inner-corner pocket** [measured render].
- **The live view keeps the film render's detail on our skin** (EEVEE 113-117% of Cycles' fine/pore/fold bands with the
  calibrated scattering) - the renderer is not the limit (RESEARCH, rec 1).
- **The proven pieces:** face skin from scans (cheek pore band equal to Aaron's on six characters); eye white, iris
  (photo), pupil and the lower-lid wet margin equal by measure on one character and holding on five; the Artec scan
  carries real torso definition (form band 3.12 vs ours 2.27, Aaron 4.34).

## The design, piece by piece

Each piece: what CC5 does, what MetaHuman does, our choice, the standard it follows (or NOT STANDARD), and the attack.
Sources: the three research files of 2026-11-05 (audited above), `2026-10-29-research-*`, the spec.

### 1 · Base mesh: hm08 kept whole, anatomy appended where the measurements show a gap

- **CC5:** one artist-made base (17,683 polygons at SubD 0) with modelled lid flaps, lid ledge, lip crease; HD levels
  by subdivision. **MetaHuman:** one template topology every head must match ("the MetaHuman Template mesh in terms of
  topology" [page]); 24,000-vertex head at LOD0; separate `eyeshell`, `eyeEdge`, `cartilage`, `saliva` meshes.
- **Ours:** hm08's 19,158 vertices stay with their indices; new vertices are **appended** only where the measurements
  show topology can't follow real anatomy - today, **the lids** (lid ring p90 14.7 mm against real faces; one ring at the
  margin). Each further region (inner lips and mouth bag, nail beds, nostrils, ears at 4.4 mm) gets a loop only if its
  own measurement says so; otherwise its gap is shape (base sculpt) or detail (HD maps), not topology.
- **How an appended vertex lives** (the research's two conditions): born on an hm08 face, it stores barycentric weights
  on that face plus an **offset in the face's local frame** (tangent, bitangent, normal) - Blender's Surface Deform
  method [code], so it turns with the face in a blink; for every target and expression its position is recomputed from
  the deformed face (baked into the target files, which grow by the appended indices); UVs and rig weights come from
  the face's barycentrics. **Closing expressions** (blink, lips together) get an authored contact correction on the new
  loops (the margin snapped to the opposite lid and relaxed - OmniFaceRig's step is the published reference [page]).
- **The loops themselves** are placed by measurement against references on disk, never copied: Blender Studio's CC0
  realistic head (2-3 margin loops, inner-corner pocket), Blender Studio's "Einar" (CC-BY; lid drivers, eyelid
  displacement), Ben Morgan's head base (caruncles, eye and mouth bags; "Creative Commons", $6.49), CharMorph's Antonia
  (36,030 v, CC-BY 3.0), HD Aaron (CC5; reference only); Reallusion's and Epic's placement rules (margin rims on the
  lid's outer and inner edges; "each cardinal loop serves its feature only") [page].
- **Standard:** Maya's "Bake Topology To Targets" is the industry's tool for exactly this (change the base, push into
  every target) [page]; Surface Deform's face-frame offset is Blender's own; MakeHuman's target format holds the result.
  **NOT STANDARD (approved 2026-11-05 "if you cant find any other way"):** appending to MakeHuman's base and extending
  its data - no better way found: switching topology (Blender's CC0 base, MakeHuman's proxy) loses exactly at the lids,
  where hm08 has no surface to transfer sliders from, and Blender's head is coarser at level 0 (3,242 v) than hm08's
  head (4,986).
- **Attack:** (a) appended vertices break MakeHuman-format tools - we are their only reader; exports carry the final
  mesh; `baseVersion` 2 with a vertex map (spec §1.1). (b) The margin intersects the eyeball on extreme eye sliders -
  the eye clearance step (a shape key per refit) and a test over every eye slider's range. (c) The new loops' UVs are
  slivers - they get relaxed UV space inside their region. (d) A new region need appears later - the same mechanism adds
  it, `baseVersion` bumps, nothing earlier breaks. **Escalation:** if the appended lid fails its measured check (margin
  band against Aaron's ~36 px; blink without gap or clip), the head alone moves to a new topology built to the measured
  references (option C), the body staying hm08.

### 2 · Subdivision and HD detail

- **CC5:** HD morphs act at SubD 1-2 (70,732 / 282,928 polygons); per-level normal and displacement maps.
  **MetaHuman:** detail in normal maps; wrinkles in animated maps.
- **Ours (spec R4, §1.4, approved N3):** level 0 for sliders and rig; levels 1-2 by Multires; HD sliders = displacement
  maps authored at level 2, faded by their slider. Edge creases on the appended margin loops keep its two rims crisp
  under subdivision (Blender's edge crease, read by Catmull-Clark).
- **Attack:** texture memory per active HD slider on the 8 GB card - baking on release keeps one map live (spec).

### 3 · Parts

- **Eyes:** GNM's eyeball and cornea (Apache-2.0); our photo-iris shader (polar unwrap; pupil 0.45 of the iris by
  default, a slider; iris specular 0 - the cornea glosses) with an iris library from Wikimedia Commons (CC BY / CC0,
  every colour); the white x0.71 with a warm tint (measured equal). **Eye layers:** the occlusion film (ICT, MIT) refit
  to the lids' opening on every change (fixed 2026-11-05); the tearline returns to a thin tear meniscus (CC5's and
  MetaHuman's role) once the margin is real geometry; the margin's pink, wet look moves to the skin (a margin region on
  the new loops' UVs), the caruncle likewise (the appended pocket plus a wet pink region) - MetaHuman's `cartilage`
  role. **Teeth, gums, tongue:** GNM's geometry and its 80 teeth components (Apache-2.0); shape variety from Poseidon3D's
  dental scans (CC BY 4.0) wrapped on; colour from MIO's photos (CC BY 4.0); a thin wet `saliva` film on teeth and lips
  (MetaHuman's layer; pass 6). **Lashes and brows:** our strand
  generators (lashes at 180 upper, 0.08 mm radius, melanin 1.0 - measured to make a lash line).
- **Attack:** the eye's measured results came from a test shader - they become the eye module's own code with its own
  tests; the iris photo shows one photo's structure on every character until the library has several per colour.

### 4 · UV layout and seams

- **CC5:** UDIM 1001-1006 (head, body, arm, leg, nails, eyelash); head and neck in one UV "for enhanced scan head and
  animated blend-map" [page]. **MetaHuman:** head and body separate meshes; neck seams handled by normal fading.
- **Ours:** hm08's UDIM layout kept (CC5's tile assignment); appended loops get space inside their islands. The chest
  seam (measured: colour, plus unpadded island edges) is fixed where textures are made: every map is generated
  **seam-continuous** - padding past island edges and colour matched across each tile border by sampling the 3D
  neighbour across the seam (the bake's margin, and a border blend in the skin builder).
- **Attack:** moving the seam line alone wouldn't fix it - CC5 has body seams too; continuity is a texture-generation
  rule, tested by rendering every tile border at the gate's views.

### 5 · Shape spaces, sliders and mixing

- **CC5:** thousands of morph sliders (general, HD, mixer); ActorMIXER mixes **only its Mixer Sliders** - "leaves the
  HD sliders and General morph sliders influences unchanged" [page]; parts head shape, eyes, nose, mouth, chin, ears,
  forehead, torso, arms, legs, body ratio; a wheel of 3+ targets per part; skins swapped. **MetaHuman:** blend up to 3
  presets per region or locally, features / proportions / both, a strength; Head Sculpt finds the closest combination
  in its scan database; skin picked from a list [page].
- **Ours (spec §1.2-1.4):** shape spaces on the level-0 base, extended to the appended vertices by the face-frame rule:
  `makehuman` (1,258 CC0), `mhr` (Meta, 7,110 body scans, Apache-2.0), `gnm` (Google, 253 head components incl. eyes
  and teeth, Apache-2.0; `mhr` reaches hm08 through Anny, whose MakeHuman topology is edited - 13,718 body vertices
  against 13,380 - so the Anny-to-hm08 correspondence is a measured step of its own, pass 1), `scans` (every person our scan route wraps - HSRD heads, Artec's body, the user's finds),
  `user` (sculpts saved as sliders). **Mixing:** a library of identities (scan identities and saved characters); soft,
  overlapping region masks (CC5's part list); per region up to N identities with weights (CC5's wheel), a features /
  proportions mode and a strength (MetaHuman's); ordinary sliders stay outside the mix (CC5's rule); skins blend per
  detail layer.
- **NOT STANDARD:** the mixer (no public standard; CC5 and MetaHuman are closed). Patents to check before it is built:
  Disney US8922553 (region PCA, to 2033), Soul Machines US11354844 (narrow claim) [page] - our design is a weighted
  blend of whole identities per mask, not region PCA; the claims to be read in full before building (not legal advice).
- **Attack:** a slider set is only as good as the mesh under it - hence piece 1 first; mixing many identities blurs
  features - the strength control and few identities per region.

### 6 · Face rig, expressions, wrinkles

- **CC5:** 262 expression morph sliders + 128 corrective combination sliders; per-character fixes in the Facial
  Profile Editor; wrinkle sets as preset libraries per actor (`HD Aaron 2K.rlWrinkle` - five maps per set, three sets)
  [page, measured]. **MetaHuman:** DNA rig (713 joints, 669 shapes at LOD0) solved in Epic's cloud; wrinkles chosen from
  153 scanned characters (3 animated normal variants each) [measured].
- **Ours (spec §2, approved):** the DNA rig evaluated by OpenRigLogic (MIT), MetaHuman's control names; ARKit 52 always
  present. **Expression shapes:** candidates scored, not picked - MakeHuman's Faceunits 01 (CC0, on hm08), FACSHuman's 133
  FACS action units (LGPL-3.0, on hm08 - no transfer), Meta's 72 artist FACS shapes (Apache-2.0), ICT (MIT), GNM's
  expression space (Apache-2.0); each shape measured against real expression scans (D3DFACS, test only) and HD Aaron's;
  the best per shape wins; all extended to the appended loops with the contact step. **Wrinkles:** RigLogic's animated
  maps (3 colour + 3 normal variants, MetaHuman's model); their weights from mesh tension (Raman et al., MIT code);
  their content generated per character by the published orientation-bin method (Weiss et al. EG 2024, CC-BY paper -
  our code - after a patent check, it being Disney research) because no open scanned wrinkle library exists.
- **Attack:** no source ranks the expression sets - so the score decides; FACSHuman's LGPL is a label (data in a GPL
  app); generated wrinkles may read synthetic - the gate's smile and brow views judge them against Aaron's set.

### 7 · Body rig and correctives

- **CC5:** UE-style skeleton, corrective expressions; **MetaHuman:** RBF and twist-swing correctives in the body DNA.
- **Ours (spec §3):** UE5 skeleton by its own names, placed from MakeHuman's joint cubes; correctives in the body DNA's
  RBF layer; **their shapes from SOMA-X's learned corrective model** (Apache-2.0; ~80,000 MHR poses; one model for every
  body it supports, Anny's MakeHuman topology among them [page]) mapped onto hm08 through Anny's SOMA correspondence and
  baked into RBF targets. Measured against plain skinning and HD Aaron at the shoulders, elbows, hips, knees.
- **Attack:** correctives independent of body shape (MHR's and SOMA-X's own statement) may under-correct heavy or very
  muscular bodies - measured on four body types before adoption.

### 8 · Skin

- **CC5:** SkinGen layer stack (skin base, normal effects - muscle, sinew, fat crease, veins - details, blemishes,
  acquired, body hair, nails); micro-normal licensed from Texturing.XYZ; Digital Human Shader [page].
  **MetaHuman:** texture synthesis from 153 scanned characters, region masks, micro detail [measured].
- **Ours (proven parts kept):** one master UDIM texture set (spec §3.1 channels); colour from the scan route's composed
  people (the likeness rule - never one scan's face); relief from the scans' geometry baked to normal maps (face proved
  equal on six characters); pores and microrelief as tiled layers by region; tone from the skin-optics model (melanin,
  blood); regions for margin, caruncle, mouth lining, lips, nails; body definition as HD maps from bare-body scans
  (Artec's carries real definition); every map seam-continuous (piece 4). Re-run on the new base (old UVs unchanged, so
  everything proven carries over).
- **Attack:** body variety needs more bare-body scans (the user's search: women, heavier, older, darker skin); until then
  the HD definition map comes from one man - a strength slider, not a default on everyone.

### 9 · Hair

- **CC5:** cards with its Smart Hair shader; **MetaHuman:** strand grooms in Unreal; Indiana Jones ships strands at 60
  fps (~2 ms) with self-shadowing baked per hair point and random-subset LODs [page, SIGGRAPH 2025].
- **Ours:** strands are the master (Blender's hair nodes, our generators, MakeHuman's CC0 styles, Blender's demo styles
  CC BY-SA); **film:** Cycles' Principled Hair (Chiang) with measured melanin (black ~0.999, brown ~0.81, blonde ~0.12
  [calc]); **live view:** strands with (1) the hair shader work already half built, (2) self-shadowing baked per hair
  point (the published fix; EEVEE's hair is 1.4-2.3x off Cycles under image light), (3) a minimum strand width with
  matching transparency (EEVEE draws sub-pixel strands at zero width [code]), (4) random-subset LODs; cards baked from
  strands for far views and export (Strands2Cards' published method, our code - its repo has no licence).
- **Attack:** scalp hair is not yet proved against CC5 - the proof (step 3) runs on this pipeline; frame time on the
  2070 Super unmeasured - measured at the gate.

### 10 · Materials and the two renderers

- Principled BSDF / Principled Hair (OpenPBR-mapped, spec §3.2). **Live view = film render's detail:** measured -
  our skin's calibrated scattering keeps 113-117% of Cycles' fine bands in EEVEE. Cycles is the film render and the
  oracle (AGENTS.md); neither CC5 nor MetaHuman ships a path tracer.

### 11 · Live-view budget, LODs, export

- Spec §3.1: 2K working textures per tile, 4K on request, 8K for film and bakes; the gate measures VRAM. Level 1 in the
  live view, level 2 for film; hair LODs (piece 9); DNA LODs 0-3 first. Export per spec (USD package, FBX + sidecar,
  glTF/VRM), HD detail baked to per-level normal and displacement maps.

## Adversarial passes (each from a new angle; what it found and what it changed)

**Pass 1 - each piece alone.**
- Base mesh: the eye's look against Aaron is not only the missing margin - his eyeball sits **recessed** behind thick
  lids; ours bulges forward (audit sheet 1). That is shape: the base's lid thickness and the eyeball's depth in the
  orbit. *Changed:* piece 1's lid work includes the recess, set from the 20 real faces our scan route already fitted
  (their eye depth measured, not guessed).
- Sliders and correctives reach MakeHuman's mesh "through Anny" - but Anny's MakeHuman topology is an **edited**
  figure (13,718 body vertices against hm08's 13,380; `2026-10-29-research-05-bases-pass2.md`). *Changed:* pieces 5 and
  7 name the Anny-to-hm08 correspondence as a step of its own, measured (it may be near-identity plus edits).
- Wrinkles: Weiss et al.'s orientation-bin method is Disney research - a patent may cover it. *Changed:* piece 6 checks
  for one before code (as for the mixer).

**Pass 2 - how the pieces fit (mesh -> UVs -> sliders -> rig -> textures -> hair -> library).**
- Appended vertices leave every old index, UV and `.mhclo` binding valid: clothes, eyes, teeth and the occlusion
  refit (it finds the lids' opening by ray casting each time) keep working. Per-vertex masks (face regions, mouth,
  margin) need values on the new vertices - their tools re-run.
- **Grooms are bound to the body by Surface Deform, whose bind breaks when the vertex count changes.** *Changed:* the
  build re-binds every groom on the new base; library hair assets are migrated.
- **The library** (characters, skins, hair) is hm08-based. *Changed:* step 1 ships the vertex map (spec §1.1) and a
  library migration, with the backup first.
- The DNA's geometry layer must list the new vertices; it is built from our mesh, so it follows.

**Pass 3 - my own claims.**
- "The live view matches the film render" rests on one view of one character (the cheek, our Average man). *Changed:*
  the claim is scoped so, and the gate's face and torso views on two more characters are added to the check.
- "The lids are the only topology gap" rests on head scans: hands, feet and torso were judged by eye only (no body-scan
  fits yet). *Changed:* build step 2 measures them (the Artec body fitted for torso and arms; hand and foot scans when
  found); no claim for them until then.
- "Maya's Bake Topology To Targets is the industry tool" - the agent's [page]; kept, marked.

**Pass 4 - the tests that would catch a mistake.**
- Base: every target loads and moves each appended vertex where Blender's own loop-cut interpolation would put it (a
  reference built in Blender for a sample of targets); a full blink closes with no gap and no clip (lid-to-lid and
  margin-to-eyeball distances); no margin vertex inside the eyeball over every eye slider's range; the margin band
  measured against Aaron's (~36 px at the gate's eye view); creases keep both rims at level 2.
- Seams: every tile border rendered at the gate's views; colour step across each border (Delta E) under a threshold.
- Expressions: each candidate shape's distance to real expression scans after fitting (the scoring harness).
- Hair: frame time on the 2070 Super; EEVEE against Cycles on the hair views (bands, coverage).

**Pass 5 - the neighbours this doesn't touch.**
- Tests asserting hm08's 19,158 vertices change with `baseVersion` 2. The face-test tools export the head at level 1
  (`head_export.npz`): re-exported; the scan skins are UV-based and stay valid. Exports (USD, FBX, glTF) read the mesh
  as it is. The Unreal plugin's MetaHuman names are untouched.

**Pass 6 - what CC5 or MetaHuman have that this design leaves out.**
- MetaHuman's `saliva` film on the teeth and lips - *added* to piece 3 for the mouth step (a wet film like the
  tearline). CC5's Headshot (photo to head) is a feature, not the character model - out of scope here (the scan route
  is ours). Clothing, accessories and makeup layers stay as the spec has them.

**Pass 7 - the riskiest assumption, and whether the order tests it first.**
- That an appended lid with face-frame transfer and a contact step blinks and looks like Aaron's. It is build step 1,
  with its measured checks and an escalation (the head on a new topology). A fresh look at passes 1-6 against this
  order found nothing further to change.

## Build order (after the user's approval of this design)

1. **The base mesh's lids** - the appended margin and caruncle, the recess, the face-frame transfer, the contact step;
   checked against Aaron's margin band and through a blink (pass 4's tests). If it fails: escalate (piece 1). With it:
   the vertex map, the library migration (backup first), groom re-binding (pass 2).
2. **The audit's remaining regions** (inner lips / mouth bag, nail beds, nostrils, ears; torso and arms from the Artec
   body fit; hands and feet when scans are found) measured the same way; loops only where measured.
3. **Expressions and the face rig** on the final base (the scored sets, wrinkles).
4. **Sliders:** `mhr`, `gnm`, `scans` wrapped onto the base; the mixer (after the patent read).
5. **Textures** re-run on the base, seam-continuous; eyes into code; body HD maps.
6. **Hair** live view (piece 9) and its proof.
7. **Body correctives** (SOMA-X) and the multi-character gate in EEVEE and Cycles.

## Research files audited (2026-11-05)

- `2026-11-05-research-face-animation.md` (agent): 36 queries logged; 28 [page], 20 [code]/[measured], 11 [snippet]
  marks; the a-n check written in. Spot-checked by me: FACSHuman's licence LGPL-3.0, last push 2026-04-18 (GitHub API);
  CC5's wrinkle set `HD Aaron 2K.rlWrinkle` on disk under `F:\Reallusion Content\Reallusion Templates\Actor\Expression
  Wrinkles\CC5 2K\`. Usable.
- `2026-11-05-research-base-mesh-2.md` (agent): 39 queries logged; 46 [page], 14 [code], 6 [file], 18 [snippet], 6
  [inferred]. Spot-checked by me: CharMorph's binding is `kd.find_n(v, 16)` nearest hm08 vertices plus nearest-face
  points (`lib/fit_calc.py`) - an averaging map, as the file says. Usable.

What they change: (1) the append (option A) ranks first and is the industry's own move (Maya's "Bake Topology To
Targets"); switching topology (B, D) loses at the lids, where no hm08 surface exists to transfer from; Blender's CC0
head is coarser at level 0 (3,242 v) than hm08's head (4,986). (2) Two conditions on A: each appended vertex keeps its
offset in its birth face's local frame (turns with the face; plain averaging puts a margin vertex ~1 mm wrong in a
blink - the file's arithmetic), and every closing expression gets a contact step (lids meet, lips seal). (3) A second
expression source on hm08 itself: FACSHuman's 133 FACS action units (LGPL-3.0); the expression sets are to be scored
against real expression scans, not picked. (4) Wrinkles: no shippable scanned library exists; mesh tension (MIT) drives
RigLogic's wrinkle maps. (5) Body correctives: SOMA-X (Apache-2.0) has one learned model reaching MakeHuman's mesh
through Anny's SOMA topology.

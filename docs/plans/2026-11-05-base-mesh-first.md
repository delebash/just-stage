# Plan — the base mesh first, then everything on it (2026-11-05)

The user, 2026-11-05 late: "why wasnt this route taken from the beggining you keep true for force little fixes instead
of doing the right thing from the beginingk, get that base mesh correct first one that has all the sub div needed high
poly like metahuman with all the sliders cc5 and muthuman and actormixng ect, if you dont have this corect how can you
texture it correclty, I want you to right now come up with a new plan on how to do it correctly, think adversierly".

## Why it went this way (honest)

The spec (R4, approved 2026-10-29) chose hm08 at subdivision level 0 with two Catmull-Clark levels, displacement for HD
detail (§1.4) and three shape spaces (§1.2) - a sound frame. What was never done: **an anatomy audit of hm08 against the
bar, region by region, before building on it.** The quality work went straight to skin, eyes and body, and every
missing piece of anatomy surfaced as a symptom (the lid margin's crevice, the torso's missing definition) that I patched
instead of tracing to the mesh. The proof order ranked "face relief" riskiest; the mesh under every part is riskier.

## The facts the plan rests on

| | Level 0 | Render level | Sliders / shapes | Source |
|---|---|---|---|---|
| CC5 HD base | 17,683 polygons | 70,732 (SubD 1), 282,928 (SubD 2) | base morphs + HD Ultimate Morphs 172 (displacement) | `2026-10-29-research-02-cc5-pass2.md`; RESEARCH (SkinGen) |
| MetaHuman head | 24,000 vertices (LOD0) | - | 669 blend shapes, 713 joints (LOD0) | RESEARCH (MetaHuman) |
| hm08 (ours) | 14,766 faces; body 13,380 v, head tile 4,986 v | level 2 (spec R4) | 1,258 CC0 targets; MHR + GNM spaces planned (§1.2) | spec; counted 2026-11-05 |
| Blender's CC0 realistic head | 3,242 v + Multires | - | none | `2026-11-05-research-base-mesh.md` |

hm08 at level 2 carries ~16x its faces - CC5's HD density. What hm08 lacks is not density but **anatomy at level 0**:
measured, the lid margin and the caruncle; unknown until audited, the rest.

## The aim: better than both — the best of CC5 and MetaHuman, part by part

The user, 2026-11-05: "and what about metahuman the idea is to make it even better than cc5 take best of cc5 and
metahuman that inlcudes base mesh imporvements and any thing else". What each does best (our research files; each
re-checked in Phase 1 against the real assets - Aaron in Blender, a MetaHuman in the user's Unreal):

| Area | CC5 (best known) | MetaHuman (best known) | JustStage takes / beats |
|---|---|---|---|
| Base mesh | modelled lid margins and lid ledge, mouth and nostril volume (audit sheet 1, 2026-11-05); 17,683 polygons at the slider level, SubD 1-2 for HD | 24,000-vertex head at LOD0 (denser face for deformation); separate eye layers incl. a `cartilage` (inner-corner) mesh and `saliva` | CC5's anatomy and MetaHuman's face density where the audit shows the need |
| Sliders | thousands of morphs incl. HD Ultimate Morphs (displacement at SubD 1-2); Actor Mixer | identity blending from a scan-based preset library | MakeHuman's 1,258 + MHR bodies (7,110 scans) + GNM heads (253) + our scans + HD maps; mixing over identities |
| Face rig | facial profiles, expression wrinkles (regions and wrinkle sets) | DNA rig: 713 joints, 669 blend shapes (LOD0), animated wrinkle maps, RigLogic | the DNA standard via OpenRigLogic (spec §2) on our mesh |
| Skin | SkinGen layer stack (muscle, sinew, veins, blemish ... ), micro-normal licensed from Texturing.XYZ, Digital Human Shader | scan-trained albedo, region masks, micro detail | the proven scan route (face equal on six characters) + layer stack + HD maps; Cycles film render (neither ships a path tracer) |
| Eyes | Digital Human eye shader, occlusion and tearline shells | eyeshell / eyeEdge / cartilage meshes, refraction model | measured today: photo iris, white, margin, caruncle; parallax iris (NOT STANDARD, waits) |
| Hair | cards + HD hair | strand grooms (Unreal groom) | strand grooms with Blender's hair nodes; cards for the live view (step 3) |

## The plan — five phases, each gated by a measured check

### Phase 1 · The anatomy audit (research; no code) — first

Every region, ours (hm08, level 0 and level 2) beside HD Aaron (CC5's mesh, in Blender), Blender's CC0 heads and body,
and a MetaHuman (the user's Unreal install; quality-gate §2): rendered at the gate's views with a wireframe and flat
grey, plus a cross-section where the anatomy is inside (lids, mouth, nostrils).
Regions: eye (lid margin, caruncle, lacrimal, lid fold), mouth (inner lips, mouth corners, the mouth's lining, gums),
nose (nostrils, alar crease), ears, neck, hands (knuckles, nail beds, palm creases), feet (toes, nail beds, soles),
torso (navel, nipples, clavicles), joints (shoulder, elbow, wrist, knee - deformation loops), face deformation
(jawOpen, smile, blink - the gate's expressions on each mesh).
**Slider resolution** (the user, 2026-11-05: "if you have sliders that maninupulate certain areas like fine control if you
dont have the mesh designed correctly, enough triangles enough sub div enough whatever the sliders wont work correctly"):
a slider moves only the level-0 vertices that exist, so per region measure how much real shape the level-0 cage can
express - the residual of real faces and bodies fitted onto it (the HSRD heads already fitted by the scan route; the
Artec body; GNM's and MHR's wraps - spec §1.2's recorded errors), p50 / p90 mm per region. High residual = too few or
badly placed loops there, whatever sliders sit on top.
Output: a gap list per region - missing loops, missing volume, too little resolution, deformation faults - each measured (loop count, band
width in px at the gate's views, the expression's shape), in `2026-11-05-research-base-mesh.md`. Also researched in this
phase: CC5's Actor Mixer and MetaHuman's blending (what they mix, on what data), and MetaHuman's face loops as reference.
**Check:** every region has a verdict (enough / gap) with its render.

### Phase 2 · Fix the mesh once — "JustStage base": hm08 plus the anatomy it lacks

- New loops only where Phase 1 found gaps, **appended after hm08's 19,158 vertices** so every existing index stays:
  MakeHuman's targets, `.mhclo` parts and clothes, our masks, the UDIM layout and rig weights keep working.
- Each new vertex is born on an old face: its UV, every target's delta, every rig weight and every face unit are the
  weighted mix of that face's vertices (one sparse matrix, applied to all per-vertex data). Then the new loops are shaped
  once in the neutral base (the margin against the eyeball, the mouth's lining inward).
- Standard: Blender's mesh tools (loop cut / subdivide interpolate custom data and shape keys - verified in the
  prototype), MakeHuman's target format (spec §1.2). **NOT STANDARD (needs the user's word by name):** appending
  vertices to MakeHuman's base and interpolating its data - the standard alternatives are MakeHuman's proxy system
  (another topology fitted like clothing; refit per slider change - every texture and mask re-baked) or a new base
  (everything rebuilt). Trade-off: append keeps all we have; the proxy keeps MakeHuman's own tooling.
- **Check:** every one of the 1,258 targets loads and moves the new vertices with their face; the parts still fit; no
  vertex of the margin inside the eyeball over every eye slider's range and a blink; old faces' UVs unchanged; the eye
  view beside Aaron - the margin band measured (ours 4-8 px today, his ~36 px).

### Phase 3 · Sliders to CC5's and MetaHuman's range (spec §1.2-1.4, approved)

- `makehuman` (1,258, CC0) as today; `mhr` (Meta, Apache-2.0: bodies from 7,110 scans) and `gnm` (Google, Apache-2.0:
  253 head components - face, eyeballs, teeth) wrapped onto the JustStage base (deformation transfer, offline; errors
  recorded); scan identities (HSRD heads, Artec body - our scan route) as targets; HD sliders as displacement maps
  (definition, wrinkles, pores at level 2 - §1.4, NOT STANDARD N3 approved).
- Mixing (CC5's Actor Mixer, MetaHuman's blend): a character as weights over a library of identities - the same targets,
  blended. Its exact behaviour from Phase 1's research.
- **Check:** a slider coverage table against CC5's morph categories and MetaHuman's face regions (count and region);
  four characters made only with sliders, at the gate.

### Phase 4 · Expressions and rig on the final mesh

The face rig (spec §2: DNA + OpenRigLogic; ARKit 52 from MakeHuman's CC0 face units, MHR's 72 artist FACS shapes as a
reference set) built after Phase 2 so blinks carry the margin and smiles the mouth's lining; the gate's expressions
(jawOpen, smile, browInnerUp) measured on four characters.

### Phase 5 · Texturing on the final mesh

The UDIM layout stays hm08's (new loops get UV space inside their faces); the proven skin method (scan colour + relief
layers - face proved on six characters) re-run on the JustStage base; body definition as HD sliders from bare-body scans
(Artec, and the scans the user finds); eyes (the measured results: photo iris, white, pupil, margin, caruncle);
mouth (Poseidon3D teeth shapes, MIO colour); nails (Yakimov); the chest seam fixed in the colour build.

### In parallel, independent of the mesh

- The live view's detail (rec 1): EEVEE's screen-space skin scattering blurs fine detail (Aaron's cheek: 0.448 fine vs
  Cycles 0.766; scattering off 0.609) - the real-time method (sharp specular, a blurred share of the diffuse) measured
  against Cycles, frame rate kept.
- The user's search: bare full-body scans (women, heavier, older, darker skin, athletic men), bare hand and foot scans.

## Adversarial checks on this plan

1. *Isn't the audit another long detour?* Bounded: ~12 regions, references on disk (Aaron, Blender's CC0 set) and one
   in the user's Unreal; one sheet per region. It replaces open-ended symptom-chasing.
2. *Append breaks MakeHuman compatibility?* Only for tools that read hm08 by count; we are the only reader; exports
   carry the final mesh. Recorded in the spec.
3. *Is hm08's face dense enough to deform like MetaHuman (24k head vertices at LOD0, 669 shapes)?* Unknown - Phase 1
   measures expressions on each mesh. If not, Phase 2 adds face loops (nasolabial, mouth, lids) by the same append.
4. *Why not switch to a denser base (MHR, GNM, Blender's head)?* MHR and GNM are closed triangle meshes built for fitting,
   not production anatomy (`2026-10-29-research-05-bases-pass2.md` §2); Blender's head is 3,242 v with no sliders; all of
   them arrive as sliders on our base by wrapping anyway. A switch costs every texture, mask and slider for anatomy we can
   add.
5. *Does the mesh fix invalidate today's proven work?* No - old indices and UVs stay: the face skin method, the eye
   results, the Artec relief bake carry over.
6. *Blinks and expressions sliding the margin into the eyeball?* The existing eye clearance (a shape key per refit) and
   Phase 4's correctives; measured in Phase 2's check.
7. *Licences:* hm08 and MakeHuman targets CC0, MHR and GNM Apache-2.0, Blender's set CC0, scans CC BY - all shippable.
   Aaron and MetaHuman are references only (looked at, never shipped).

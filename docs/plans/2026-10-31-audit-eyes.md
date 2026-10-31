# Audit — the eye white near the lids (job 13), researched (2026-10-31)

Audit row 13 in `2026-10-31-choices-audit.md`: the eye white (sclera) is darkened toward the lids by Cycles' Ambient
Occlusion shader node (6 mm), with the cornea split into its own object. Picked in face-test round 45 without a search.

**Scope.** The task began as jobs 13, 14 (catch light) and 24 (iris points). The coordinator then cut it twice: first
"extract what the earlier research found, search only real gaps", then "DROP job 14 … DROP job 24 … Do ONLY job 13:
how CC5's Eye Occlusion … and Tearline … and MetaHuman's eyeEdge/eyeshell are SHADED, and how they are FITTED to a new
head and kept on moving lids, with open implementations … and their licences". The searches already run for jobs 13,
14 and 24 are all logged in §9, and what job 24's searches returned is kept in §8. Nothing was concluded for 14 or 24.

**Plain words.** *Sclera*: the white of the eye. *Eye occlusion shell*: a thin see-through skin laid over the front of
the eyeball. It darkens the white near the lids, like the soft shadow a real lid casts. *Tearline* (tear meniscus): the
thin wet strip of tear fluid where the lid edge meets the eyeball. It shows as a fine shiny line. *Caruncle*: the small
pink lump of tissue in the inner corner of the eye. *UV mask*: a black-and-white picture painted on a mesh's own flat
map (its UVs), which tells the shader where to darken. *Shrinkwrap*: Blender's modifier that keeps one surface hugging
another. *Path tracer*: a renderer that traces real light paths (Cycles), so real shadows come for free. Real-time
engines (Unreal, CC5's viewport) can't trace light this way, which is why they fake the shadows.

Evidence labels: **page read** (the page itself was opened), **API** (a GitHub or Hugging Face API, or the file read
through it), **measured** (run here on CPU), **snippet** (only a search result's text).

---

## 1 · What our research already had (quoted, with file:line)

| Finding | Where | Evidence there | Re-checked now |
|---|---|---|---|
| Layer stack: eyeball, tearline "under the Eye Occlusion", the occlusion "the topmost mesh layer" for "the shadow cast from the eyelids" | `2026-10-30-research-hair-eyes-teeth.md:334-336`; `../dev/RESEARCH.md:554-560` | page read | yes, page read again (CC5 occlusion page) |
| 80.lv UE4 article: occlusion mesh "provides fake eyelid shadow and occlusion shadow for eyes, this is the key to making the eyes look more natural"; tearline "blends eye and eyelid more natural and it also provides the wet effect"; "check the UV of this mesh" | `hair-eyes-teeth.md:337-340` | snippet | **page read now**: all three quotes confirmed. The article doesn't say how the UVs are used. |
| Reallusion forum: after editing in Blender the shells "move with the head but are otherwise static" | `hair-eyes-teeth.md:340-341` | snippet | **page read now** (forum topic 518661): quote confirmed. The fix posted there: delete the shells, re-add them with "Add Eye Element", re-import the blendshapes through the Face Profile Editor. |
| CC5 occlusion settings pages exist: Blur, Shadow 1, Shadow 2, Vertex Offset | `RESEARCH.md:556-557` ("not read"); `2026-10-29-research-02-cc5.md:500` (TOC titles) | TOC only | **page read now**, all four; their parameters are in §3a |
| CC4 Tear Line settings: Depth Offset, Detail Amount, Detail Scale U/V, Edge Fadeout, Roughness | `RESEARCH.md:561-563` | page read | **page read now** on the CC5 version; values in §3b |
| Shells "will be changed along with the movement of eye sockets when morphing and performing facial animations" | `RESEARCH.md:563-566`; `2026-10-29-research-02-cc5-pass2.md:315-318` | page read | not re-read; the mechanism was found now (§4) |
| MetaHuman meshes `eyeshell`, `eyeEdge`; material slots `EyeShell`, `LacrimalFluid`; forum: eyeshell and edge clip into a custom head's eyeball | `RESEARCH.md:565-569` | snippet | **API now** (Epic's DNA Calibration repo: the mesh list and skin clusters, §3c/§4); forum **page read**: only the question, no answer |
| ICT-FaceKit (MIT): lacrimal fluid 204 v, eye blend 24 v, eye occlusion 152 v per eye; "adopts the style of Unreal Engine's Digital Human Project … plug and play with Unreal Engine's shaders" | `hair-eyes-teeth.md:342-345`; `2026-10-30-research-skin-detail-shading.md:478-481`; `2026-10-29-research-10-character-assets.md:143-144` | API | **API + measured now** (§4): the shells are in every expression shape |
| Layers top-down incl. "**Eye blend mesh** at the corners (ICT-FaceKit), for the caruncle transition"; occlusion "A transparent dark gradient by UV, with blur, two shadows and a vertex offset" | `skin-detail-shading.md:465-473` | page read (CC5) + inference | gradient-by-UV now confirmed by Epic's doc (§3c) |
| Unity *Heretic*: "Custom marker-driven occlusion for eyes and teeth" | `skin-detail-shading.md:476-477` | API (README) | **API now**: the code's method read (§3d) |
| Rec: shells in ICT's layout + refractive cornea + MNEE; attack: MNEE ignores normal maps | `skin-detail-shading.md:554-557` | — | the AO node can't be combined with MNEE: see §2 |
| **Rec 6** (approved): "ICT-FaceKit's (MIT) eye occlusion, tearline and caruncle meshes as templates fitted to our eyes" | `2026-10-30-realism-recs.md:54-55` | — | ICT has **no caruncle mesh**: its corner piece is "Eye blend" (§4) |
| Inference: no eyelid shadow on the eyeball is "exactly what CC5's Eye Occlusion exists to fix" | `hair-eyes-teeth.md:140-142` | inference | stands |
| CC Blender Tools (GPL-3) rebuilds CC's occlusion and tearline in Blender. "Clean-room: do not read its shader code" | `hair-eyes-teeth.md:366`; `skin-detail-shading.md:380, 531` | API | README changelog read now (no code), §3g |

---

## 2 · What the face test does now, against that research

Read in `tools/face_test/test_face_project.py`:

- **The white darkened by an AO node** (lines 795–802): `ShaderNodeAmbientOcclusion`, Distance 0.006, 16 samples,
  feeding MPFB2's `EyeWhiteColor`. Measured in round 45: the white's brightest tenth was 0.258 against the painting's
  0.248 (0.287 without AO).
- **The cornea split into its own object** (lines 848–860), hidden from shadow and diffuse rays, so the AO sees only
  the lids.
- **No shells.** `_eye_shells` (line 151) builds an occlusion shell and a tear band. Its mask comes per vertex from a
  front-camera depth test, and its shader mixes a lit dark Diffuse BSDF with a Glossy one. **It is never called**:
  grep finds only its `def`. TASKS round 19–26 recorded it as "tried and set aside (its shading blotched)".
- **The lash cards cast no shadow** (line 288, `obj.visible_shadow = False`, after MakeHuman's `.mhmat`
  "castShadows False").

**Deviations from the research:**

1. Rec 6 and every research file name an occlusion shell, a tearline and a corner piece. The pipeline has none of
   them, and uses an AO node, which no source names for this job.
2. The AO node is light-blind: it darkens wherever geometry lies within 6 mm, the same at the top, bottom and corners.
   CC5 gives the upper lid, lower lid, inner corner and outer corner separate ranges and strengths (§3a). Sony's patent
   puts the darkest band under the upper lid (§3e).
3. Blender's manual (raw `ao.rst`, page read) says: "For Cycles, this is an expensive shader and can slow down render
   significantly". It also says the node "will not produce a valid result when" the object is a caustic caster or
   receiver while the scene has a shadow-caustic light. So the AO node **can't be combined with MNEE**, the cornea
   method the research recommended (`skin-detail-shading.md:427-431, 491, 555`).
4. The round-45 metric (the brightest tenth) checks how bright the white is, not how it darkens toward the lids.

---

## 3 · How the pros shade the layers (the gap, now researched)

### 3a · CC5 Eye Occlusion — a UV-space mask with per-side ranges (all pages read)

- **Shadow 1**: "Shadow 1 Color" ("the shadow color casting on the eyeballs"), "Shadow 1 Strength" (default **0.312**).
  It also has a range, contrast and "Edge Fadeout Contrast" ("the edge sharpness of the range mask") for each of
  **Top** ("the shadow from the upper eyelid"), **Bottom** ("from the lower eyelid"), **Inner** ("from the inner corner")
  and **Outer**.
  [page](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/15_Digital_Human_Shader/Eyes/Eye-Occlusion-Shadow-1.htm)
- **Shadow 2**: a second colour (example values shown **#54170E**, a dark red-brown, and #0000FF), a strength
  (examples 0.2 / 0.8), "Shadow 2 Top" and "Shadow 2 Top Range" ("Controls the edge sharpness of the range").
  [page](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/15_Digital_Human_Shader/Eyes/Eye-Occlusion-Shadow-2.htm)
- **Blur**: "adjust the blurriness of the eye-occlusion elements for simulating the shadows from the eyelids". It has
  Blur Color and Strength, plus a Range, Contrast and Edge Fadeout for Top, Bottom and Outer, and "Inner Blur Duct Range".
  "Inner Blur Contrast": "determines the position of the dark crevice between the eyeball and the tear duct".
  [page](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/15_Digital_Human_Shader/Eyes/Eye-Occlusion-Blur.htm)
- **Vertex Offset**: "offset the Eye Occlusion mesh in order to snuggly fit the eyeballs". "Depth Offset" ("the depth
  of the entire Eye Occlusion Mesh", default **0.500**), and Top / Bottom / Inner Corner / Outer Corner Offsets
  (−0.2…0.2). [page](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/15_Digital_Human_Shader/Eyes/Eye-Occlusion-Vertex-Offset.htm)
- *Reading:* CC5 doesn't compute the occlusion. Artists set it per side, as range masks over the shell's UVs.

### 3b · CC5 Tear Line (page read)

[CC5 Tear Line settings](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/15_Digital_Human_Shader/Eyes/Digital-Human-Tearline-Tearline.htm):

- Depth Offset ("the depth of the entire Tear Line", default **0.050**)
- Detail Amount, plus Detail U/V Tiling (a tiling normal detail)
- Micro Normal Strength and Scale
- **Edge Fadeout** (examples 1.25 / 0)
- **Roughness** (0.25 / 0.45)
- **Opacity** (0.04 / 0.2)

The CC5 overview page (page read) says the tearline texture is unchanged, but its UVs were redone because CC4's
normal-map tiling "was unevenly distributed". So the tearline is a near-transparent, glossy strip that fades at its
edges. CC's slider units are not stated.

### 3c · Epic (Unreal Digital Humans, MetaHuman)

- **UE 4.27 "Photorealistic Character"** ([page read](https://dev.epicgames.com/documentation/en-us/unreal-engine/photorealistic-character?application_version=4.27)):
  - A translucent helper sheet over the eye approximates the occlusion, with the material `MI_Eye_Occlusion_Bust`.
    Its border "should be made to fit the area of the open eyelid", and its UVs fill the 0–1 space.
  - The eye material itself has **Shadow Hardness** and **Shadow Radius**, plus Sclera inner/outer colour, Brightness,
    Roughness, Veins and Flatten Normal.
  - A wet normal map (`T_Eye_Wet_Normal`) and the "Secondary Env" reflection cubemap.
  - The Eye shading model has an Ambient Occlusion input, described as the soft shadow where the eye meets the lid and
    caruncle. It is soft because light scatters through the eye.
- **MetaHuman's eye-area meshes** (Epic's `MetaHuman-DNA-Calibration`, `examples/dna_viewer_build_rig_with_textures.py`
  and `data/mh4/additional_assemble_script.py`, API read; Epic's own licence, study only):
  - `eyeshell_lod*` (own shader); `eyeEdge_lod*` and **`cartilage_lod*`** (the inner corner) share `eyeEdge_shader`.
  - `saliva_lod*`, and **`eyelashesShadow_lod*`**, a separate mesh whose only job is the lashes' shadow.
  - Each mesh has its own skin cluster (`eyeshell_lod0_mesh_skinCluster` …).
- MetaHuman Creator's sclera controls were already page read (`research-10-character-assets.md:553-556`). Re-found as
  a snippet: Vascularity Coverage is clamped to 0.1–0.4 and Intensity to 0–2, and the tint follows the skin tone unless
  `bUseCustomTint` is set.

### 3d · Unity *The Heretic* (API, `Runtime/EyeRenderer.cs`; Unity Companion License, "for Unity-dependent projects")

- The lid occlusion is an **anisotropic spherical Gaussian** (a soft oval darkening on the eyeball). It is fitted every
  frame to four markers attached to the skin at the lid's left, right, top and bottom.
- Settings: `asgPower` 10, `asgThreshold` 1e-7, `asgModulateAlbedo` **0.65** (the darkening is applied to the colour),
  and an optional extra layer on the iris.
- The four markers follow the skin through Unity's skin-attachment system.
- This is a published maths method (ASG, Xu et al. 2013). We could write it ourselves; Unity's code can't ship.

### 3e · Film and patents

- **Weta, Gollum** ([page read](https://www.theonering.net/torwp/2003/08/06/25471-weta-digital-sfx-details-2/)):
  "simulate … the meniscus near the eyelids, and an extra amount of shadowing from the eyelids". "The eyelid meniscus
  and shadow effects were created by constraining curves to the edges of the eyelids, and then querying information
  about these curves from within the shaders at render time." So film also adds extra lid shadow on top of the
  computed light, and drives it by distance to the lid edge.
- **Sony Pictures, US 9336622** (Sheerin; [page read](https://patents.google.com/patent/US9336622B2/en)): "a darkened
  region … on the top portion of the eye between the center of the pupil and the upper eye lid", "between about 40%
  and 60% of the shading value of the remainder of the eye", strongest at the lid. "This darkness is a combination of
  shadows from the brow, eyelashes, and upper lid." It is applied as a shader correction, not a computed shadow.
- **Sony Pictures, US 9269185** "procedural CG eye meniscus" (Sheerin, Monos;
  [page read](https://patents.google.com/patent/US9269185B2/en)):
  - The ribbon is built from the eye-socket loop of the skin mesh. It is split into 20–40 radial edges, each
    intersected with the eyeball and offset, and the points are lofted inward.
  - It "may move and be bound, and stay bound, to a moving CG object".
  - A shader curves it (usually concave) and makes "a lower section of the meniscus a greater thickness than a top
    section".
- Weta, *Alita*: the meniscus and caruncle "water movement" was simulated in Houdini (snippet, Animation Magazine).
- Valve, US 7388580: the sclera is made to look wet with light reflected from a concave surface (snippet).

### 3f · Real anatomy

The normal lower tear meniscus is about **0.20 ± 0.05 mm** high (Keratograph study; 0.19 ± 0.05 mm by fluorescein;
OCT 0.24 ± 0.07 mm). It is higher away from the pupil's midline (snippet, search 12).

### 3g · In Blender

- **CC Blender Tools** README changelog (API; GPL-3, its code not read under the clean-room rule):
  - "Added cycles specific shaders for hair, tear-line and eye occlusion"
  - "Added displacement modifiers & parameters to Eye Occlusion and Tearline objects"
  - "Added eye occlusion hardness parameter"
  - "Cycles Tearline shader reworked"
  - So a Blender port keeps both shells **even in Cycles** (a path tracer), and holds them off the eyeball with
    modifiers.
- **Blender's Shrinkwrap modifier** (manual raw `shrinkwrap.rst`, page read): "Nearest Surface Point" mode with an
  Offset and "Outside Surface" ("the offset is always applied towards the outside of the target"). This is the
  documented way to keep a layer a set distance outside another surface.

---

## 4 · How the shells are fitted to a head and kept on moving lids

| System | How it fits and follows the lids | Evidence |
|---|---|---|
| CC5 | The shells have **their own blendshapes**: "Their relative blendshapes are Eye_Blink, Eye_Wide, Eye_Squint" (Reallusion staff, 2020-12-14). Vertex Offset fits them to the eyeball. Edited outside CC they "move with the head but are otherwise static" until re-added | page read ([tracker](https://www.reallusion.com/FeedBackTracker/Issue/New-Eye-Elements-Occl-and-Tearline-in-CC-3-32-fail-to-work-in-Unity-2019-4), [forum](https://forum.reallusion.com/PrintTopic518661.aspx)) |
| ICT-FaceKit | The shells are **inside every expression shape**. Measured on `generic_neutral_mesh.obj` vs `eyeBlink_L.obj` / `eyeLookUp_L.obj` (all 26,719 vertices; units taken as cm because the eye centres are 6.19 apart, a human spacing — an inference): see the list below this table | measured (files via raw GitHub, MIT) |
| MetaHuman | Each eye mesh is **skinned** (its own skin cluster) to the face joints, and the DNA drives them. A custom head with MetaHuman topology still gets "eyeshell and edge clip into the eyeball" (no answer posted) | API (DNA Calibration), page read (forum) |
| Unity *Heretic* | Four markers attached to the skin drive the occlusion; there is no shell mesh | API |
| Sony | The meniscus is generated from the socket loop and bound to the moving eye and lid | page read |
| Blender ports | Displacement modifiers (CC Blender Tools); Shrinkwrap with offset (manual) | API, page read |

ICT-FaceKit, measured:

- In a blink, the left occlusion moves up to 9.6 mm (median 2.8 mm) and the lacrimal fluid moves up to 9.6 mm, while
  the eyeball and the eye blend don't move.
- In look-up, the occlusion moves up to 3.6 mm and the eyeball doesn't. ICT turns the eyeball by transform, not by
  shape.
- Against a sphere fitted to ICT's sclera (radius 15.8 mm, larger than a real ~12 mm eye), the occlusion sits a median
  0.5 mm off the eyeball (−0.4…2.6 mm), and the lacrimal fluid a median 0.4 mm.
- The occlusion covers 27 × 11 mm, the whole eye opening.

**What we already have for this** (code read):

- `libs/wrap/gnm_to_hm08.py`: a non-rigid fit, trimesh's Amberg NICP (MIT), "the standard method".
- `extension/juststage/core/mhclo.py` `bind`/`fit`: MakeHuman's MHCLO, which binds each vertex of an asset to the
  nearest triangle of the base. It is how our eyes, teeth and lash cards follow every head shape key.
- *Limit:* MHCLO keeps each vertex's offset fixed in the base's axes. The middle of an occlusion shell sits over the
  eyeball, far from any lid triangle. It should follow the eyeball's surface, not the lid.

---

## 5 · Open implementations and references, labelled

| Name | What it gives for this job | Code licence | Data / weights | Platform | Last update | Evidence |
|---|---|---|---|---|---|---|
| **ICT-FaceKit** (USC-ICT) | Eye occlusion 152 v, lacrimal fluid 204 v, eye blend 24 v per eye, with UVs; the shells inside the expression shapes (2 of its 53 checked); material values only (`M_EyeOcclusion` Kd 0.5, `M_LacrimalFluid` Ks 1.0), **no shader, no texture**; no caruncle mesh | MIT | geometry MIT | any (OBJ) | 2020-12-01 | API, measured |
| Galacean digital-human eye | Sclera texture ("blood vessel color … add bloodshot effects"), sclera mask, limbal ring, parallax. **No lid occlusion or tearline** | MIT | — | WebGL | 2026-08-03 | page read, API |
| O3DE `Eye.materialtype` | Iris depth/radius, limbus size, inner-eye IOR, sclera/iris textures. **No occlusion or tearline** | Apache-2.0 OR MIT (`RESEARCH.md` §6; the GitHub API says NOASSERTION) | — | O3DE | 2026-10-30 | API |
| MPFB2 procedural eye (in use) | Iris and white, procedural; no shells | GPL-3 | node data CC0 | Blender | — | already in research |
| Unity digital-human package | The ASG lid occlusion from 4 skin markers (§3d) | Unity Companion License (Unity-dependent projects only) | — | Unity HDRP | 2025-01-15 | API |
| MetaHuman (DNA Calibration) | Mesh list and skinning (§3c) | Epic's own licence — study only | — | Maya/Unreal | 2025-06-20 | API |
| CC5 Digital Human shaders | Parameters (§3a–b) | proprietary — behaviour only | — | CC5 | — | page read |
| CC Blender Tools | Cycles occlusion/tearline shaders, displacement modifiers | GPL-3 — **code not read (clean-room)** | ships Reallusion textures | Blender | 2026-10-14 | API (README) |
| EyeForge | Imports caruncle and tear line "as separate objects" | GPL, $16.98 | — | Blender 4.0–5.x | — | already in research |
| Tom Newbury, "Realistic Digital Eyes 3.0" | A course: caruncle and meniscus modelling | paid course | — | Maya / Mari / Redshift | — | snippet |
| Sony patents US 9336622, US 9269185 | The darkened band; the procedural meniscus | patents (method described; check before copying the exact method) | — | — | granted (B2); dates not read | page read |

Not found (a gap in these searches, not proof): an open shader for an occlusion or tearline shell; a CC0 sclera
texture with veins (search 14); an open procedural caruncle; any vendor document on how Unreal's path tracer treats
the occlusion shell (search 17).

---

## 6 · The rec

**Build rec 6's shells the CC5 / MetaHuman / ICT way, and drop the AO node.**

1. **Geometry.** Per eye: ICT-FaceKit's (MIT) eye occlusion and lacrimal-fluid meshes, plus its eye-blend mesh for the
   inner corner.
   - Fit them once to our eye with the non-rigid fit we already use (`libs/wrap/gnm_to_hm08.py`'s NICP), scaled from
     ICT's 15.8 mm eyeball to ours.
   - Their rims follow our lids through `core/mhclo.bind`, the way our lashes and parts follow head shape keys.
   - Blender's Shrinkwrap modifier (Nearest Surface Point, Outside Surface, a small offset) holds them on the eyeball.
     This plays the part of CC5's Vertex Offset and CC Blender Tools' displacement modifiers.
2. **Occlusion shading.** A UV mask, as CC5 and Epic do: separate ranges and strengths for the upper lid, lower lid,
   inner corner and outer corner, each with an edge fade, then a blur. In Cycles, use a Transparent BSDF tinted by the
   mask: a pure darkening of what lies behind, with no shadow cast (`visible_shadow` off). Not the lit dark Diffuse
   film of `_eye_shells`.
3. **Tearline shading.** A near-transparent glossy strip along both lid margins (CC5's example values: opacity
   0.04–0.2, roughness 0.25–0.45), faded at its edges, thicker at the lower lid (Sony; the real lower meniscus is
   about 0.2 mm).
4. **Calibration.** Set the strengths against the painting the way the rest of the face test does, but on the white's
   brightness profile from the upper lid down to the iris and out to each corner, not only its brightest tenth.
5. Remove the AO node and the uncalled `_eye_shells`.

**The attack, and what it changed:**

- *Double shadow in a path tracer.* Cycles already traces the lids' real shadow, so a fake film could over-darken.
  But Weta added "an extra amount of shadowing from the eyelids" on top of computed light (2003, rendered "without
  raytracing", so this is weaker evidence for a path tracer), CC Blender Tools keeps both
  shells with Cycles-specific shaders, and Sony's band is 40–60%. **Kept**, with the strengths calibrated against the
  painting starting from low. **Changed:** the metric becomes the brightness profile (item 4).
- *Our last shell blotched* (rounds 19–26). Its mask came per vertex from a front-camera depth test, on a subdivided
  cap of the eyeball, and its dark part was a lit Diffuse BSDF. **Changed:** the mask moves into UV space on ICT's
  clean ring layout (Epic: UVs fill 0–1, fitted to the open lid), and the film is a tinted Transparent BSDF. What
  caused the blotches was never traced. This is my reading of the code, not a measurement.
- *Cost against the AO node.* The AO node needs no fitting and follows the lids by itself. But it is light-blind and
  equal on every side. It gives no wet line, which rec 6 needs anyway. Blender's manual calls it "expensive", and it
  can't be combined with MNEE (§2). No pro pipeline in these searches uses it for this job. **Kept.**
- *A simpler standard?* Unity's ASG from four lid markers is one function with no mesh, but it only darkens (no wet
  line), its code is Unity-only, and it has one user. **Not chosen.** It stays as the fallback if the shell fit fails
  on our lids.
- *MHCLO's limit.* A vertex in the middle of the shell has no lid triangle under it. **Changed:** Shrinkwrap onto the
  eyeball was added (item 1), so the shell's middle rides the eyeball while its rim rides the lids.
- *Rec 6's wording.* ICT ships no "caruncle meshes", only "Eye blend" (24 v). MetaHuman's corner piece is `cartilage`.
  **Changed:** the corner piece is ICT's eye blend. The inner-corner pink already comes from the painting projected
  onto our skin (round 46).
- *Licence and clean-room.* ICT is MIT. CC5's and Epic's parameters are used as documented behaviour; none of their
  code or content is used. Holds.

**Not verified here.** Nothing was rendered (no GPU work in this task). The ICT fit on our lids, and the shell's look
against the painting, are measured when the shells are built.

---

## 7 · Open items found (not in the rec)

1. **Lash shadows.**
   - MetaHuman ships an `eyelashesShadow` mesh, a separate mesh for the lashes' shadow (API).
   - Sony's patent says the upper darkening is "a combination of shadows from the brow, eyelashes, and upper lid".
   - Our lash cards cast no shadow (line 288): MakeHuman's `.mhmat` says so, which is a real-time engine's choice.
   - Cycles can cast a shadow through the cards' alpha. Untested here. A trial on `round.blend` would show it.
2. **Rec 6's text in TASKS / realism-recs** says "caruncle meshes". Whether to correct it to "eye blend" is the
   user's call (an approved text).
3. **The AO node and MNEE can't be used together** (Blender manual). This matters for the cornea rec in
   `skin-detail-shading.md:555`, whatever happens to job 13.

---

## 8 · Job 24 (iris points) — what its searches returned before the cut (no rec)

Kept so the searches aren't lost. Not researched to the end: the coordinator dropped job 24 ("the current tool works
for us").

- **MediaPipe Iris** ([arXiv 2006.11341 HTML](https://arxiv.org/html/2006.11341), page read):
  - Predicts "pupil center, 4 points of outer iris circle, and 16 points of eye contour".
  - Trained on "≈20,000 manually annotated images". Overall error 7.16% of inter-eye distance; no figure for the
    iris alone.
  - Google's blog (page read): ~50k labelled eye images; depth from an assumed 11.7 ± 0.5 mm iris (error 4.3%).
  - No study measuring how far its iris circle sits from the true limbus was found (search 25).
  - A 2026 screening paper adds +5% to a HoughCircles radius for lid occlusion (arXiv 2603.00161, snippet).
- **open-iris** (Worldcoin): code MIT. Its segmentation model (`Worldcoin/iris-semantic-segmentation`, ONNX, MIT and
  Apache licence files) is for **infrared** images ("When provided with an infrared image"; 18,431 IR images). API
  and model card read.
- **CVRL OpenSourceIrisRecognition** (Notre Dame; arXiv 2605.20735): a segmenter plus circle regressor, and DINOv3
  "iris-fm-tools". Research use only ("discuss individual licensing options … for commercial purposes"). Pushed
  2026-06-08. Page read, API.
- **OpenFace 3.0**: non-commercial only (LICENSE read); 68/98 face landmarks, no iris contour.
- **GazeML** (Park et al. 2018): MIT, iris-edge landmarks trained on UnityEyes, pushed 2024-10-26 (API).
- **RITnet**: MIT, trained on infrared OpenEDS, 2021 (API).
- **SAM 2**: Apache-2.0, pushed 2026-05-30 (API). In eye studies the iris needs a box plus point prompt; arXiv
  2603.17715 rates SAM 2 above SAM 3 for eye images (snippet).
- **Face parsers** (CelebAMask-HQ's 19 classes) label the eye as one region, no iris (arXiv 2312.15102, snippet).
- **Training-free**: Daugman's integro-differential circle search, Hough, RANSAC circle fit (method descriptions,
  snippet). No Python implementation was found in one search.
- **Benchmarks**: no maintained iris-segmentation leaderboard was found. NICE.I is historical (E1 error). A 2024 PMC
  study compares 11 algorithms on 5 datasets (snippet).

Job 14 (catch light) had no searches before the cut.

---

## 9 · Searches — every query run in this task

27 WebSearch queries. Why each one was run: queries 1–17 came before the coordinator's "search only gaps" message;
from 18 on, each one fills a named gap. "Already in our research" says whether the main result was already in a
research file.

| # | Job | Query (mode; domains) | Why | What it returned | Already in our research |
|---|---|---|---|---|---|
| 1 | 13 | how to make realistic CG eyes sclera shadow near eyelids occlusion (standard) | plain | Weta Gollum article; Sony US 9336622; Valve US 7388580; CC3/4/5 occlusion pages; WACV 2026 eyes PDF (403 on fetch) | CC pages yes (`RESEARCH.md:554`); Weta, Sony, Valve **no** |
| 2 | 13 | best way to shade eye whites realistic 3D character eye occlusion tearline caruncle (standard) | plain | CC occlusion/tearline pages, CC auto-setup "Eyes and Eye Occlusion", 80.lv, EyeForge, Tom Newbury course, Pixelica pack | CC, 80.lv, EyeForge yes (`hair-eyes-teeth.md:334-371`); Newbury no |
| 3 | 13 | eye occlusion mesh vs ambient occlusion eyes realistic character (standard) | X vs Y | CC pages; Reallusion forum: baking the occlusion into the texture "looks weird when the eyes look around" (snippet); EGSR 2006 AO for animated characters | no |
| 4 | 13 | MetaHuman eye occlusion material eyeshell eyeEdge lacrimal fluid how it works (standard) | named | MetaHuman API slot pages, the eyeshell clipping thread, M_EyeRefraction forum claims | slots and forum yes (`RESEARCH.md:565-569`) |
| 5 | 13 | Unity Heretic digital human eye shader eye occlusion "eyelid" occlusion cones technique (standard) | named | Digital-human package forks, 80.lv Heretic tutorial; "marker-driven occlusion" | README line yes (`skin-detail-shading.md:476`); the method (ASG) no, read via API |
| 6 | 13 | Jimenez next generation character rendering eyes wet layer occlusion sclera Activision Digital Ira (standard) | named | Talk listings; arXiv 1505.05916 cites Jimenez for wetness, refraction, AO | named, not opened (`skin-detail-shading.md:509`) |
| 7 | 13 | film VFX digital human eye rendering meniscus tear film sclera veins Weta Pixar eye shading paper (standard) | plain, film | Weta (oil film meniscus), US 9443343 tear film, RIT-Eyes | no |
| 8 | 13 | Alita Battle Angel eyes Weta iris fibers sclera caruncle meniscus eye model detail (standard) | named, film | Press pieces: meniscus and caruncle water simulated in Houdini (snippet) | no |
| 9 | 13 | MetaHuman Creator eyes sclera vascularity brightness tint cornea options documentation (standard; dev.epicgames.com) | named | Eye Material Tools, sclera API struct (ranges, `bUseCustomTint`) | controls yes (`research-10-character-assets.md:553-556`) |
| 10 | 13 | Unreal Engine eye shading model iris mask eye occlusion tear film documentation digital human (standard; dev.epicgames.com, docs.unrealengine.com) | named | Shading-models page; UE4 Digital Humans and Photorealistic Character pages | Eye model yes (`research-10:387-389`); the occlusion sheet no |
| 11 | 13 | realistic eye Blender Cycles tear line meniscus caruncle eye occlusion shell tutorial (standard) | plain, Blender | Newbury courses (Maya/Mari/Redshift), EyeForge, 80.lv eye tutorial; no free Blender tutorial | EyeForge yes |
| 12 | 13 | tear meniscus height mm normal lower eyelid anatomy measurement (standard) | gap: real size | TMH 0.20 ± 0.05 mm (Keratograph), 0.19 ± 0.05 (fluorescein), OCT 0.24 ± 0.07 | no |
| 13 | 13 | RenderMan Pixar realistic eye shading meniscus sclera eyelid occlusion technique (standard) | named, film | Sony US 9269185 procedural meniscus; CryEngine eye shader (an occlusion mesh "covers the gap between the eye lids", snippet); no Pixar paper | no |
| 14 | 13 | sclera texture veins free CC0 eye white texture blood vessels procedural shader (standard) | gap: sclera texture | CC/iClone sclera texture docs, Galacean, a 2017 vessel-synthesis paper; **no CC0 sclera texture** | Galacean yes |
| 15 | 13 | eye occlusion tearline blender addon github open source (standard; github.com) | open implementations | Only CC Blender Tools (+ Unity URP sibling); unrelated AO bakers | yes (`hair-eyes-teeth.md:366`) |
| 16 | 13 | photorealistic eye rendering path tracing sclera subsurface scattering conjunctiva paper (standard; arxiv.org, dl.acm.org, diglib.eg.org, disneyresearch) | academic | Bérard 2014; skin SSS papers; nothing on the conjunctiva | Bérard yes |
| 17 | 13 | Unreal path tracer MetaHuman eye occlusion mesh eyeshell hidden path tracing eyes look wrong (standard) | gap: shells in a path tracer | Forum threads (no fix); an ArtStation post disabling MH occlusion and baking it into colour (snippet); Reallusion RT thread with black edges | no |
| 18 | 24 | best iris detection model 2025 open source iris center radius from face photo RGB (standard) | gap: none in our files | CVRL OpenSourceIrisRecognition (arXiv 2605.20735), Roboflow iris detectors, YOLOv5 iris paper | no |
| 19 | 24 | alternatives to MediaPipe iris landmarks more accurate iris contour (standard) | alternatives | TF.js face-landmarks (attention mesh), DOOMGAN, Google blog | no |
| 20 | 24 | iris segmentation visible light benchmark UBIRIS NICE.I state of the art leaderboard (standard) | leaderboard | No maintained board; NICE.I (E1), IrisParseNet numbers, 2024 PMC evaluation | no |
| 21 | 24 | face parsing model with iris pupil sclera classes segmentation RGB portrait open weights (standard) | named class | 19-class parsers have no iris; RITnet, IrisParseNet, CondSeg, yakhyo face-parsing | no |
| 22 | 24 | visible light iris sclera segmentation pretrained model RGB eye images (standard; github.com, huggingface.co) | named, weights | ESS (unsupervised sclera), LightIrisNet (withdrawn), RITnet, Shape Constrained Network (WACV 2020), Halmstad GST | no |
| 23 | 24 | Daugman integro-differential operator iris boundary circle fit python implementation (standard) | training-free method | Method descriptions, Hough/RANSAC alternatives; no Python repo | no |
| 24 | 24 | Segment Anything SAM zero-shot iris segmentation evaluation point prompt (standard; arxiv.org, github.com) | named candidate | arXiv 2311.08077, 2410.08926, 2603.17715 | no |
| 25 | 24 | MediaPipe iris landmark accuracy evaluation limbus boundary error compared ground truth (standard) | why ×0.88 | No direct study; Google's depth error 4.3%; arXiv 2603.00161's +5% radius correction | no |
| 26 | 24 | iris segmentation (standard; huggingface.co) | HF candidates | Only papers (PMC, Iris-SAM 2402.06497, reviews); no model pages returned | no |
| 27 | 13 | Reallusion forum eye occlusion tearline edited in Blender "move with the head" static not following eyelids (standard) | verify a snippet line | Forum topic 518661, the feedback tracker (shell blendshapes), forum 545320 | the quote yes (`hair-eyes-teeth.md:340`), now page read |

**Pages read** (WebFetch):

- Weta Gollum article
- Google Patents US 9336622 and US 9269185 (the USPTO PDF was image-only)
- CC5: Eye Occlusion overview, Shadow 1, Shadow 2, Blur, Vertex Offset; Tear Line overview and settings
- 80.lv "Efficient character rendering in UE4"
- UE 4.27 Photorealistic Character
- Galacean eye docs
- Reallusion forum 518661 and feedback tracker
- Unreal forum threads 2764072 and 2717655
- arXiv 2006.11341 (abstract + HTML), Google's MediaPipe Iris blog
- CVRL README
- arXiv 2312.15102, 2510.06170, 1910.05283 (abstracts)

Failed: the WACV 2026 eyes PDF (403), Blender's docs site (403; the raw manual from projects.blender.org used
instead), MetaHuman eye-material-tools (empty page), the CryEngine eye shader page (navigation only).

**API / raw files** (no search):

- `gh api`: USC-ICT/ICT-FaceKit (licence, tree, README, `.mtl`); Unity-Technologies/com.unity.demoteam.digital-human
  (licence, README, `EyeRenderer.cs`); EpicGames/MetaHuman-DNA-Calibration (docs, two scripts, LICENSE);
  soupday/cc_blender_tools (README only); o3de/o3de (`Eye.materialtype`); galacean/engine-toolkit; worldcoin/open-iris;
  swook/GazeML; CMU-MultiComp-Lab/OpenFace-3.0 (LICENSE, README); TadasBaltrusaitis/OpenFace;
  AayushKrChaudhary/RITnet; facebookresearch/sam2; CVRL/OpenSourceIrisRecognition.
- Hugging Face API: Worldcoin/iris-semantic-segmentation.
- Raw Blender manual (`ao.rst`, `shrinkwrap.rst`).
- ICT OBJs measured: `generic_neutral_mesh`, `eyeBlink_L`, `eyeLookUp_L`. The files and scripts are in the session
  scratchpad, not the repo.

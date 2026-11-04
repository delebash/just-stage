# Review of the realism brief — Fable, adversarial (2026-11-04)

> The user: "fable review opus brief docs/plans/2026-11-04-realism-review-brief.md review adverserily and produce
> your review". Reviewed: the brief at 872febb, checked against the code, the spec, the research files and the
> sources' own pages. Marks: [code file:line] read; [spec] `docs/standards/character-data-model.md`; [page] a page
> read today; [research file:line]; [not re-read] a claim I could not re-check today (Blender's manual 403s to
> WebFetch and the browser extension disconnected). Findings are ranked by what they cost the bar if left as is;
> each ends with its attack and what the attack changed.

## Verdict

The brief's core is sound and better than most plans of its kind: the measured limits (the tile density, the AI
repaint rounds, the hair diagnosis), the layer split with pores from one scan, the licences now quoted at source, and
the EEVEE light-node facts (verified in the brief itself, 0.2027 vs 0.2028). It should not be built in this order,
and five things are missing that decide whether the bar is reached: a gate that can diagnose, a live-view budget,
delighting as a required step, a likeness rule, and a body tile size that matches the spec. Two recs rest on
assumptions that fail when checked (3's chromophore inversion on unpolarised diffuse; 7's rig-free wrap). Nothing
in the brief needs throwing away.

## Findings, ranked

### F1 · The gate as designed cannot diagnose anything (§7, the order's first step)
- **The brief:** "the same character in (1) our live view, (2) our film render, (3) Unreal 5.8 with MetaHuman's
  shaders ... beside the user's CC5 screenshots".
- **Checked:** Unreal 5.8 is installed (`F:\Epic\UE_5.8`). AGENTS.md's own rule: "a gap is diagnosed by changing one
  factor at a time". The gate changes three at once: a MetaHuman preset is a different person (shape), different maps
  (content) and a different stage (light); CC5 screenshots add a fourth.
- **Problem:** whichever looks best, nothing says why - shading, maps or light - so the result can't steer a rec.
- **Rec:** three gates, one factor each. (a) *Shading:* our mesh and our maps, imported into Unreal (Epic's "Send to
  Unreal", MIT - the standard route, already in the research) on a material using MetaHuman's `M_skin_unified` /
  `SSP_skin_unified`, under one HDRI (engine-neutral) - beside EEVEE and Cycles with the same maps and HDRI. This
  answers "is EEVEE's shading class enough". (b) *Content:* MetaHuman's maps and ours rendered in Cycles on the same
  light - this answers "are our maps enough" (renders only; nothing of theirs copied - clean-room holds). (c) *The
  user's eye* on the full stages, last.
- **Attack:** (a) needs our character in Unreal, a day; → it is the planned Unreal plugin's first step anyway, not
  extra. (b) touches MetaHuman content locally; → comparison renders of a licensed install are use, not derivation.
  **Changed:** the order of the gates - (a) first, since it decides between EEVEE and the fallbacks.

### F2 · No live-view budget anywhere - the bar can be "won" at 2 fps
- **The brief:** recs 1 (per-light Marschner on every strand), 16 (64 samples, full-resolution tracing, max
  roughness to 1.0), 11 (200K+ coily strands), 17 (several tiling layers at render time) each cost frame time and
  VRAM; no rec has a cost in its gate; no fps or ms target exists in the brief.
- **Checked:** the spec sets the only budget there is - the 8 GB rule and "the gate measures VRAM at 2K, 4K and 8K"
  [spec:217-221]; `2026-11-04-realism.md:164` already admits "200K+ coiled strands are too heavy for the live view".
- **Rec:** a budget before the first build: a full character (skin, eyes, scalp hair, brows, lashes) in Material
  Preview at 1080p on this card, steady at or above 24 fps, with the character's textures at or under 2 GB of VRAM;
  every rec's gate reports its ms and MB beside its look; a rec over budget gets an LOD (hair cards, 2K tiles), not
  a pass.
- **Attack:** a number picked now may be wrong; → it is measured on today's character first and set from that
  (the card is shared with CC5 and two peer sessions, so headroom matters). **Changed:** the budget is set by
  measurement, not chosen.

### F3 · Rec 3's chromophore inversion runs on diffuse that has the light baked in
- **The brief:** "each layer inverted per texel to melanin and blood by our own skin model (Donner et al. 2008;
  Aliaga, Hery & Xia 2022), shifted to the target".
- **Checked:** HSRD-100's card states 112 cameras, "Consistent lighting and capture conditions", 16K PNG - and
  nothing about polarisation or any channel beyond the diffuse [page, today]; the Sketchfab scans are phone and rig
  photogrammetry with "baked light" (the brief's own words). Donner's and Aliaga's inversions assume reflectance
  measured under controlled light; on unpolarised diffuse the specular and the shading invert to pigment. The brief
  half-admits it ("light left in a scan reads as pigment") and lists delighting as "untested".
- **Rec:** pick the base by tone, sex and age from the 21 (HSRD covers the tones - real dark skin with its own sheen
  and pore look, which no recolouring gives); then transfer the *broad* layer's colour statistics to the target
  tone from the skin model (mean and spread per channel in a perceptual space - Reinhard et al. 2001, the standard
  colour transfer, a few lines), keeping mid and fine as ratios. Chromophore inversion becomes a side experiment
  with its own gate (round-trip error on NIST's measured skins before any scan sees it).
- **Attack:** colour transfer cannot change sheen or pore look across tones; → that is exactly what picking the
  base by tone does, and specular is rec 16's / 18's job, not the colour map's. **Changed:** nothing in the chain;
  the inversion leaves the critical path.

### F4 · Delighting is a required step, not a candidate
- **The brief:** yoso-delight-v0-4 "run on the scans before the inversion - untested" (rec 3's attack).
- **Checked:** no base on hand is polarised (F3); Headshot 3 and MetaHuman both delight before projection
  [research RESEARCH.md:2166-2171]; the user's "the adams apple is indented" was a painted shadow read as a dent
  [TASKS 386-387] - the same failure, from an AI view instead of a scan.
- **Rec:** its own rec, before rec 2's bases are used: delight the *broad and mid bands only* (the fine band keeps
  the original - delighting models smear pores), candidates yoso-delight-v0-4 (Apache-2.0), Marigold IID appearance
  (OpenRAIL++, a label), OpenDelight (GPL-3 code, face-specific); gate: the top-to-bottom luminance gradient and the
  left-right asymmetry of each base before and after, and a flat-light render beside the scan's own photo.
- **Attack:** one more model on a shared card; → it runs once per base on the processor if need be (the bands are
  4K, the models accept 1-2K and the result is upsampled onto the broad band only). **Changed:** the band split
  (delight low bands only) came out of the attack.

### F5 · No likeness rule: a shipped base can be one recognisable scanned person
- **The brief:** rec 2 puts "ten more people in the scan-skin mix"; rec 7 wraps whole bodies; Ten24's and the CC BY
  scans are real people.
- **Checked:** `tools/face_test/skin_base.py:4,13,160-162` - "not a copy of one scanned person": pores from ONE
  scan, blotchiness from 2-3, the tone its own; no likeness measurement exists anywhere (no recognition model in
  `tools/` or the extension). CC BY, "use as you wish" and the stock licences grant copyright, not personality
  rights - Pexels and Pixabay say so themselves ("especially Content which features a recognisable person"; "you
  must consider whether you require the consent of a third party") [licences file]. HSRD states "informed consent for
  data collection" - for the dataset, not for appearing as a character in an app.
- **Rec:** write the rule into the spec (a shipped character is never one scan's face: shape from GNM's space or
  the generator, broad and mid colour from two or more scans, fine from one; whole-face projection of a single scan
  only for a user's own import), and a build test: an open face-recognition model (facenet-pytorch, MIT; InsightFace's
  models are non-commercial - a label) measures each library character's render against every source scan's photo;
  it must be farther than two unrelated people are. Bodies carry no likeness; rec 7 is unaffected.
- **Attack:** a test that needs a model and a photo per scan; → CPU, seconds, library only; the photos are in the
  scans' own archives. **Changed:** the rule's exception for a user's own import (their scan, their call).

### F6 · Rec 17 fixes the body at 1K tiles; the spec says 2K default, 4K on request, 8K masters
- **The brief:** "(a) all skins are already baked into one layout at one density (head tile 4096 ...; body tiles
  1024), so a 16K source cannot make one character sharper".
- **Checked:** `tools/build_skins.py:45` `SIZE, BODY_SIZE = 4096, 1024`; the spec's resolution budget: "the working
  resolution is 2K per tile by default (≈ 0.5 GB for the body) and 4K on request; 8K is used by Cycles and by final
  bakes" [spec:217-221]. A 1K torso tile is ~1.6 texels/mm: moles, veins, elbow and knee darkening, tan lines - the
  mid band rec 17's floor is meant to measure - blur away below the neck.
- **Rec:** body tiles to 2K now (the spec's default), 4K on request, 8K masters baked from the 16K scans; VRAM
  measured at each (the spec's own gate). Rec 17(a)'s sentence corrected: the density is the spec's, not today's.
- **Attack:** VRAM on a shared 8 GB card; → 2K is 0.5 GB for the body by the spec's own arithmetic. **Changed:**
  nothing; the spec already decided this.

### F7 · Rec 7's rig-free wrap is the non-standard route; the standard is a body-model fit, already running here
- **The brief:** "correspondences from body keypoints on renders (Sapiens2, cached), procrustes + NICP"; §9.4 asks
  for "the best way to wrap posed full-body scans onto our A-pose body without a rig".
- **Checked:** every registered scan dataset is built by fitting a parametric body to the scan; the research has the
  open one: MHR through SAM 3D Body, "SAM License (custom; royalty-free incl. derivatives)" [research-05-bases:85,
  187]; and web-9e's just-mocap runs SAM 3D Body through ComfyUI on this machine (its card request of 2026-11-03).
  NICP across different arm and hand poses is where it fails (the brief's own attack).
- **Rec:** fit MHR to each scan (SAM 3D Body from the scan's render, refined to the mesh), one MHR-to-hm08
  correspondence made once (both in A-pose), and every body texture transferred through it - the same path a user's
  imported scan would take. Keypoints + NICP stays for the head, where it is measured and works.
- **Attack:** SAM 3D Body needs the card (~5 GB) and a Windows run unverified in this repo; → it is already run on
  this machine by the peer, through the same ComfyUI, by message. **Changed:** the fitter is the peer's existing
  ComfyUI graph, not a new install.

### F8 · The IMPORT route is a product feature, not §9's question 9
- **The brief:** the redo found the best sources for older faces, coily hair and sclera are a user's own purchase
  (deep3dstudio 16K polarised heads $12.99, KhitrovArt / PixelHair grooms, Bauer's sclera, Texturing.XYZ) and asks
  whether an importer is "worth building early".
- **Checked:** CC5's realism ecosystem is exactly this - SkinGen and Headshot work on content the user brings or buys
  (RESEARCH.md:205-207); rec 2's scan route (`tools/face_test/scan_*.py`) is the importer in all but its command.
- **Rec:** rec 2 gains its command form - "Import a scan" (OBJ / FBX + maps, 4K-16K) through wrap, delight (F4),
  bake - and rec 11 "Import a groom" (Alembic is Blender's own import). A user who buys a deep3dstudio 70-year-old
  gets the same quality as the library; the app ships nothing of it.
- **Attack:** scope; → no new pipeline, the existing tool exposed as the command the standards spec already lists
  for the API. **Changed:** nothing.

### F9 · Rec 1 builds on a stand-in; a five-minute check first, and a bound
- **The brief:** a hand-written Marschner / Karis node group on Light Accumulation, first in the build order,
  "NOT STANDARD (replaced by Blender's closure if it lands)".
- **Checked:** `modules/hair/groom.py:58` quotes the manual's limitations page: "Principled Hair BSDF — Not
  supported" [code comment; not re-read today]; the light term verified (0.2027 vs 0.2028); the colour fitted
  under the stage light; the image-light gap 1.4-2.3x is the world's indirect share. Unreal's strand hair also needs
  what EEVEE lacks (deep opacity maps, voxelised transmittance); Karis' multiple-scattering stand-in is the published
  answer for engines without them, and it is in the rec.
- **Rec:** keep rec 1, but (i) one render first with Principled Hair on the All output in EEVEE 5.3 to see what it
  gives today (the manual claim is from an earlier reading), (ii) a bound - two days and the 10% gate under both
  lights - after which hair cards (the MetaHuman / CC5 real-time default beyond LOD0) take over for the live view,
  strands staying for close-ups and the film. Move it after skin and eyes (F11): the colour under the stage light is
  already fitted; the open gap is image light only.
- **Attack:** the user named hair first ("the live view darker inside the hair"); → the remaining gap is one light
  type, while skin and eyes are wrong in every view. **Changed:** the order.

### F10 · Rec 16 should count closures before adding lobes
- **The brief:** "the specular as two lobes (Unreal's 0.75x / 1.3x roughness, mixed 0.85) within EEVEE's three
  closure bins (SSS + two reflection lobes stays noise-free; a fourth closure goes stochastic)".
- **Checked:** the face material already carries SSS + GGX + a coat lobe (0.12, roughness 0.44 - a second specular
  lobe in all but name) + sheen 0.1 [`maps.py:29,169-178`] - four closures, if the research's bin reading of
  `eevee_nodetree_lib.bsl.hh` is right (its own "not verified": "whether Principled plus a Glossy takes the
  two-reflection-bin path"). If so, the face is stochastic at 16 samples today - part of the "plastic" noise.
- **Rec:** rec 16 starts by measuring noise vs closure count (sheen off, coat off, each alone); sheen on skin at 0.1
  is a peach-fuzz stand-in that rec 10's real fuzz replaces - likely a free win. `trace_max_roughness` 0.5 vs skin
  0.59 stands as the brief has it (the setting's semantics [not re-read today]: surfaces rougher than it fall to
  Fast GI).
- **Attack:** the bin reading may be wrong; → measuring costs an hour and settles it. **Changed:** "measure first"
  replaces "add two lobes".

### F11 · The order
- **The brief:** gate → 16 → 1 → 18 → 2+3 → 17+7 → 4 → 6, 5 → 12 → 8-10 → 13-15 → probe → 11.
- **Checked against the user's own words:** "yours looks plastic, the eyes dont look real" (skin, eyes), "the live
  view darker inside the hair" (hair, image light only), "we need to do realistic variety" (bases); every character
  today has plain body skin; the bodies are on hand.
- **Rec:** the gate (F1a) runs as soon as the card is free, in parallel with the build, not before it. Build: 16
  (incl. F10's count; half a day) → 18 + F4 (relief source and delighting; they decide 17) → 17 + 7 + F6 (one quality,
  bodies at 2K, through F7's fit) → 3 as F3 (base by tone, transfer) → 2 + F8 (bases and the import command) → 12
  (eyes) → 1 (hair, bounded, F9) → 4 → 6, 5 → 8-10 → 13-15 → probe → 11.
- **Attack:** 18 before any base work delays variety by days; → 18 is a one-scene test on data on hand (Ten24's six
  measured normal levels, HSRD crops), and 17 can't choose its source without it. **Changed:** 12 moved up, 1 down.

### F12 · Smaller corrections
- **Rec 18:** single-image relief from a stock photo (StableNormal / Marigold) at pore scale is a guess - the
  photo route for relief is photometric stereo, which stock photos can't give; keep it in the test as the cheap
  contender, expect the measured sources to win (Ten24's `Level_01-06_Normal` at 16K are measured relief; HSRD's 5M
  polygons bake to normals). "Per-pore shine" already half exists - cavity drives Specular IOR Level
  [`maps.py:147-150`]; the test should add cavity-to-roughness, not a new mechanism.
- **Rec 17(c):** at 6 texels/mm a pore (0.1-0.3 mm) is under one texel - the baked tile never holds pores; the
  floor measures the mid band (wrinkles, blotches), which is right; say so, and state the fine layers' own density
  (the LPS tile: ~5.6 cm per tile) as the pore floor.
- **Rec 13:** Poseidon3D's record is titled "Challenging Teeth Segmentation Cases" [page, today] - a segmentation
  benchmark, so its arches lean toward hard cases (crowding, partial dentition); use them as the extremes and GNM's
  80 teeth directions as the normal space; the scans are shape only (no colour), as the brief says.
- **Rec 11's label:** Blender's "Hair Styles" demo says "CC BY-SA license" with no version [research other-sites:27].
  BY-SA 4.0 is one-way compatible with GPLv3 (Creative Commons, declared 2015-10-08 [page, today]) - adaptations may
  ship inside the GPL extension; BY-SA 3.0 is not - they would ship as separate BY-SA assets. Find the version on
  Blender's demo-files page before the grooms enter the library.
- **Children:** the brief defers to "the generator and MakeHuman's age shape". MakeHuman's age targets reach
  children (CC0, on hand); whether GNM's scan-based identity space holds children is not stated anywhere in the
  research (grep: nothing) - say it is a hole in the bar until a child head source exists (the redo found only 3D.sk's
  clothed photo references, IMPORT / REFERENCE), and gate child faces for uncanniness on their own.
- **Shape is outside the brief and inside the user's complaint:** "the lashes and the corner of the mouth look
  wrong" (2026-11-03) - lid shapes, the lip contact line, mouth corners are shape and rig, not texture; the brief
  names lid shapes in rec 12 only. The face rig (OpenRigLogic, built) is the vehicle; it should be named as the
  rec that answers that complaint, so it is not read as "fixed by skin".

## Answers to §9

1. **Hair (rec 1):** keep it, bounded (F9); cards are the real-time standard beyond LOD0 and the fallback, not the
   first move - the strand route is half built and the gap is measured. Multiple scattering without deep opacity
   maps: Karis' wrapped-Lambert term tinted by the base colour, plus an explicit world term - what the brief has.
2. **Variety (recs 2-4):** scan base + AI colour is right at 21 bases. A statistical texture space (MetaHuman's way)
   pays off from ~50 registered scans; it is a PCA over the broad and mid bands of bases already in our layout - an
   afternoon once the count is there, so plan it, don't start it. 21 covers "any tone"; it does not cover 70+ or
   children (F12).
3. **Chromophore inversion on photogrammetry albedo:** no (F3).
4. **The body wrap:** a body-model fit, MHR via SAM 3D Body (F7).
5. **Missing:** F1, F2, F4, F5, F6, F8; shape (F12 last point).
6. **Order:** F11.
7. **Recs 13, 15:** shape targets from scans beat a statistical model at these counts (400 arches, 58 ears) - keep;
   for teeth, GNM's directions as the smooth space and the scans as targets at the extremes (F12).
8. **Pores by ethnicity and sex:** dermatology reports pore size and density varying with sex and age; by ethnicity
   the published evidence is mixed - not researched here, and it should be before rec 17's axes are fixed (a
   research item, not a rec). The band-energy floor is right for the mid band only (F12).
9. **IMPORT:** yes, as a command of rec 2 and rec 11, not a separate build (F8).

## What stands as written

Recs 5, 6, 8, 9, 10, 14, 15; rec 12 (eyes: the iris library, parallax, the caustic, the catch light); rec 13 with
F12's caveat; rec 16's settings with F10 first; the licence routes; the "film render is the oracle" rule (necessary -
it checks the engine - not sufficient: F1b checks the content); the recorded AI-repaint limits, which this review
confirms from TASKS and did not re-run.

## Not verified by me today

Blender's manual pages (limitations, raytracing) - 403 to WebFetch and the browser extension disconnected, so the
"Principled Hair BSDF not supported" and `trace_max_roughness` semantics stand on the earlier readings; EEVEE's
closure packing of Principled (F10 says measure); the BY-SA version of the Hair Styles demo; whether GNM's identity
space holds children; pore statistics by ethnicity.

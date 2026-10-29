# Research 02, pass 2 — Character Creator 5 (CC5): the gaps round one left open

Researched 2026-10-29 by a second-pass research agent (section S1 of
[`2026-10-29-research-second-pass.md`](2026-10-29-research-second-pass.md)). Round one's notes:
[`2026-10-29-research-02-cc5.md`](2026-10-29-research-02-cc5.md). Clean-room: public pages and docs
only; nothing copied. Code repositories were read for names and facts only.

Labels on each fact:
- **page read**: the page itself was fetched and read. Reallusion forum topics were read through
  Discourse's public JSON (`/t/<id>.json`, `/posts.json`), which counts as page read.
- **forum excerpt**: only the excerpt returned by the forum's own search API was read.
- **search snippet only**: seen only in a web-search result summary.
- **file read (facts only)**: a public source file was fetched to read names or numbers.

The CC5 online manual's table of contents (940 topic URLs) was parsed again from
`https://manual.reallusion.com/Character-Creator-5/Data/Tocs/5_Chunk0..3.js`. About 240 topic pages
were fetched as text; the ones cited below were read. Manual pages carry no dates of their own; the
help system was built 2026-10-29 (round one). Short name used below: **M:** =
`https://manual.reallusion.com/Character-Creator-5/Content/ENU/`.

Blocked or refused (not worked around): reddit.com (both search and fetch refused: "not accessible to
our user agent"), polycount.com (HTTP 403), help.z-emotion.com article (403), the ArtStation post
round one hit (403 then; not retried). Reallusion's store pages load prices from a script, so the
fetched HTML holds no prices. About 55 WebSearch calls were used.

---

## Top findings

1. **The viewport runs on DirectX 11.** Reallusion added a second engine, **RTX Render**, a path
   tracer on NVIDIA RTX Path Tracing that needs DirectX 12 (DXR 1.1 minimum, 1.2 recommended) and an
   NVIDIA RTX 3060 8 GB or better. It has been an open beta for iClone and CC5 since 2026-07-13
   (Beta3_0917 on 2026-09-23). It is free, NVIDIA only, and doesn't yet support CC editing tools —
   [staff post, RTX Render Open Beta (1)](https://discussions.reallusion.com/t/17902) (2026-07-13, page read);
   [Beta3 post](https://discussions.reallusion.com/t/18527) (2026-09-23, page read).
2. **Iray does not work in CC5.** Staff said so before launch: "Headshot 1 and the Iray Plug-in are
   NOT supported in CC5". The manual's Plugins menu, which still lists "Iray Render", is out of date —
   [staff, Pete_RL](https://discussions.reallusion.com/t/13783) (2025-04-08, page read).
3. **5.12 exists but has no release-note post.** Builds 5.12.1925.1 (RTX beta) and 5.12.1928.1 are
   reported in August 2026, the Feedback Tracker has a "5.12" version field, and the manual has a
   `5.12/` folder. Other builds found: 5.07.1705.1, 5.11.1823.1 and 5.13.2031.1. The 5.2 build number
   was not found (§9).
4. **The mesh counts now fit together.** The published spec table gives the CC3+ base at SubD 0 as
   **17,683** polygons for all elements, and **14,046** for the full body (head 4,758 + body 9,288). The
   CC5 HD base is **70,732** at SubD 1 and **282,928** at SubD 2, exactly ×4 per level. The "60K" and
   "240k+" figures are for a dressed character with hair. Round one read the Level Table's columns
   wrongly; corrected in §3. Vertex counts are published nowhere —
   [CC base-model page](https://www.reallusion.com/character-creator/cc-avatar.html) (undated, page read).
5. **Reallusion gives three bone counts for the CC3+ rig: 100, 101 and 108.** A list of 101
   `CC_Base_` names was put together from Reallusion's own GPL Blender add-on, and the manual's LOD
   removal steps reduce it to exactly 54 and 22. **CC5 adds "ten additional bones … to the spine and
   head"** to match UE5, but their names aren't published (§4).
6. **Facial bones (CC3+): 10.** They are `CC_Base_FacialBone`, `JawRoot`, `UpperJaw`, `Teeth01/02`,
   `Tongue01–03` and `L_Eye`/`R_Eye`. The tongue has three bones, per the manual (§4).
7. **The UDIM layout has six tiles along U:** 1001 head, 1002 body, 1003 arm, 1004 leg, 1005 nails,
   1006 eyelash. All six sit in one texture set named `Std_Skin_Head`. The eyes, teeth and tongue keep
   their own materials in tile 1001. CC5 HD uses the same layout (§5).
8. **The CC5 Pro annual plan costs $33.25 a month, billed yearly (about $399 a year).** It bundles CC5
   Deluxe, Headshot and the SkinGen Premium 4-in-1 —
   [Creative Bloq review](https://www.creativebloq.com/3d/character-creator-5-review-unreal-engine-support-and-auto-rigging-make-it-a-joy-to-use) (2026-05-27, page read).
   Other prices found: ZBrush Face Tools $299 Indie / $1,490 Studio (2023), SkinGen Premium $99 list
   (2020) and PRIME $99 a year. Reallusion points are 100 to the dollar. Still not found: the Iray,
   FashionGen and current SkinGen prices (§6).
9. **Scripting stays on the iClone 8 plugin model with PySide2 (so Qt 5).** Staff's CC5 samples
   declare `"ap": "iClone", "ap_version": "8.0"`, and Reallusion's own in-app plugin imports `PySide2`
   and `shiboken2`. The Python version is a conflict: 3.8 (IC8 docs, 2023) against 3.10 (a third
   party, 2026). CC5 ships its own interpreter, `CharacterCreatorpy`, in `Bin64` (§7).
10. **The MetaTailor plugin works with CC5.** It was missing at launch; staff said on 2025-09-15
    "Yes, it will be released this week". Users dressed CC5 characters through it in 2026. Users
    still report it needs MetaTailor Pro (§7).
11. **The native formats are closed and carry DRM.** The `.fbxkey` is a "Decrypt Key File" that
    authenticates assets. It holds DRM base-content information, the scale of each bone, the body
    skin weight of each vertex, and the clothing type. The content EULA calls ccAvatar, ccProject,
    ccSlider, ccHair, ccCloth, ccShoes and ccGloves proprietary "CC Components". No public structure
    for any of them was found (§8).
12. **Licence lines** (text served; §11):
    - Software EULA, 2026-05-25: outputs may be used commercially. The CC Base Model clause bars use
      "in any character generation system", for AI training, and in a "character-generating business".
    - Content EULA, 2025-08-01: Standard and Enterprise tiers, plus iContent at 30% and Extended.
    - AI Service EULA, 2026-10-29: the Free tier is for testing only; Starter, Standard and Pro allow
      commercial use.
13. **Outside opinion is thin and mostly positive.** The independent review found is Creative Bloq's,
    4.5/5 in every category. It praises the HD face rig, ActorMIXER and the swap with MetaHumans in
    Unreal. Its complaints: the app "feels very much like a set of plugins collected together", has
    little backward compatibility, and assumes an asset budget. Reddit was blocked and Polycount
    refused; CGSociety closed in January 2024 (§1).
14. **No link between Z-Weave and CC was found.** Z-Weave imports custom avatars as OBJ, FBX, GLB,
    glTF, USD or Alembic (search snippet), so an exported CC character could be loaded as a generic
    avatar (inference; §10).
15. **The manual pages behind round one's topic-title rows were opened** (§2). They add the 5.2 cloth
    categories and their mapping from the old layer numbers, the two collision types, how auto-hide
    works, the six SkinGen material regions and seven skin layers, the shader texture lists, the
    `.fbxkey` and JSON sidecar contents, the FBX export options, an undo limit of 180, and more. One
    count conflicts: Extended Plus is given 26 non-linear sliders on one page and 50 on another.

---

## 1 · Praise and complaints from outside Reallusion's own forum

### Reached
- **Creative Bloq**, review by Paul Hatton (Future), published 2026-05-27, page read —
  [review](https://www.creativebloq.com/3d/character-creator-5-review-unreal-engine-support-and-auto-rigging-make-it-a-joy-to-use).
  - Scores: 4.5/5 for value, getting started, features, user experience and support. Verdict: "an
    affordable package for premium and professional character creation".
  - Praise:
    - The HD facial rig (262 blendshapes + 128 correctives): "I couldn't believe how easy it was …
      to create squint wrinkles and furrowing brows".
    - ActorMIXER is "simple to use and generates excellent results", though it lacks "a little bit
      more granular control".
    - CC5 characters swap with MetaHuman counterparts in Unreal Sequencer without retargeting.
    - The Hub shows which plugins work with CC5 or iClone 8.
    - Support tickets were answered quickly.
  - Complaints:
    - The UI "feels very much like a set of plugins collected together into one application rather
      than a refined set of tools"; "novices will struggle"; "many legacy tools … get in the way".
    - "There doesn't appear to be much backward compatibility"; with older meshes the experience
      "can actually feel quite limited and restrictive".
  - Don't buy it if you make "non-humanoid monsters or multi-limbed creatures", want "extensive
    animation tools built in", or "don't have any extra budget to buy Reallusion's assets".
  - The reviewer "had access to a full licence" for testing; who supplied it isn't stated.
- **GameFromScratch**, 2025-09-08, page read —
  [article](https://gamefromscratch.com/reallusion-character-creator-5/). A feature announcement
  that calls CC5 "powerful character creation software", like a "super powered video game character
  creator". Its one complaint: the trial is "only available on the Windows platform".
- **CGDive review** (tool listing, undated, tagged "paid"), page read —
  [CGDive](https://cgdivetest.super.site/tools/reallusion-character-creator).
  - Praise: CC5 "can save a lot of time and effort", ActorMIXER, and clothes that adapt to body
    shape.
  - Limits: humanoids only; the full ecosystem is paid modules and packs, so costs add up; Blender
    remains better for slow, hand-sculpted work.
- **DevGames3085**, YouTube "CC5 vs MetaHuman", listed 9/4/2025 (day and month unclear). Read through
  a third-party summary, page read — [summary](https://readray.ai/notes/tr/unreal-engine-5-20260813/cc5-vs-metahuman-review).
  - "Basically CC4 on steroids"; "you own your assets and aren't locked into Unreal's ecosystem".
  - "Some of the best features come with extra bundles".
  - MetaHuman is "free but tied to Unreal licensing".
- **Argil** (a competing AI-video company), 2025, search snippet only —
  [blog](https://argil.ai/blog/how-much-does-reallusions-character-creator-subscription-cost-and-is-it-worth-it-in-2025).
  It flags a complex UI, multi-step workflows, and export limited by price tier.
- **Epic's Unreal forum** (user reports, page read):
  - Importing a CC5 character into UE 5.7.4 with Auto Setup crashes "7-8 out of 10 times" —
    [thread](https://forums.unrealengine.com/t/2734691) (2026-07-09).
  - A four-fingered CC5 template shows a lens-flare artefact in UE 5.7 —
    [thread](https://forums.unrealengine.com/t/2735248) (2026-07-12).
  - A community tutorial says CC5 fixed earlier retargeting problems "by adding more bones and
    refining the default rest pose" — [thread](https://forums.unrealengine.com/t/2678878) (2025-11-26).
- **80.lv**: no review; only news and tutorial pieces. Example: "From Sculpt to Infinite Variations:
  Mastering CC5's HD Character Workflow and ActorMIXER" by Óscar Fernández, 2025-11-11 —
  [80.lv](https://80.lv/articles/from-sculpt-to-infinite-variations-mastering-cc5-s-hd-character-workflow-and-actormixer) (search snippet only).

### The Virtual Production Insider review (hosted by Reallusion)
- David Stapp, Virtual Production Insider; Reallusion's magazine, 2025-11-20, page read —
  [write-up](https://magazine.reallusion.com/2025/11/20/influencer-highlight-character-creator-5-review-by-virtual-production-insider/).
  Disclosed: Reallusion supplied the software.
  - Praise: CC5 is "pretty amazing" and "the winner" for body and skin tweaks; it "wins on the sheer
    amount of assets"; a CC5 character goes into a MetaHuman Blueprint with "very little effort".
  - Caveats: many assets cost extra; CC5 "may not be right for" occasional users; not a "Metahuman
    killer"; the export button can be hidden unless Windows scaling is 100%; the MetaHuman swap has
    many manual steps.
  - On CC4: its quality "wasn't competitive" with MetaHumans, and its Unreal transfer "wasn't great".

### On Reallusion's own forum (for balance; outside sources were thin)
- In "CC5 vs Metahumans", users argue that MetaHumans are free and that Reallusion's licence forbids
  using CC in in-game character builders —
  [thread](https://discussions.reallusion.com/t/cc5-vs-metahumans/14296) (2025-06-05/06, page read).
- Subscriptions drew objections ("Pay forever software …"), and a user wished the EULA's limits on
  using output were more reasonable —
  [thread](https://discussions.reallusion.com/t/16307) (2026-02/03, page read).
- A user said Reallusion stated that hobbyists are no longer its target. Staff (jason_RL) answered
  that "individual 3D creators remain at the heart" and that subscriptions were made "with indie
  creators in mind" — [thread](https://discussions.reallusion.com/t/17227) (2026-05-13/14, page read).

### Blocked or absent
- Reddit (r/Reallusion and others): refused to both search and fetch, so not reached.
- Polycount: one comment page found (`polycount.com/discussion/comment/2469614`), which returned HTTP
  403.
- CGSociety: announced it would shut down on 2024-01-08, so there's no CC5 coverage —
  [CGPress](https://cgpress.org/archives/cgsociety-to-shut-down-in-january-2024.html) (2023-12, search snippet only).
- YouTube: videos are only reachable through Reallusion's write-ups or third-party summaries.

Assessment:
- The one independent review adds three complaints round one didn't have: the app feels like a set
  of plugins, backward compatibility is weak, and the HD features are limited to the newest meshes.
  It agrees with round one's praise.
- Without Reddit, the sample stays small and tilted towards vendor-hosted voices.

---

## 2 · Manual pages behind round one's topic-title rows

Each bullet is one manual page (M: prefix as above), page read. These upgrade round one's "TOC title"
rows to page-read facts.

### Base bodies and conversion
- CC3 Base+ came in CC 3.3. Its spec table lists bone counts CC1 139, CC3 100, CC3+ 100, Game Base 72,
  and texture counts 5 / 6 / 6 / 1-2-6 —
  [M: CC3 Base+ Characters](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/05-Character/CC3-Plus-Characters.htm).
  Polygon counts are in §3.
- When converting CC1 or CC3 to CC3+, you pick texture sizes from a target table. At High (4K):
  head, body, arm and leg diffuse 4096; eyelash 128; nails 2048; tongue 1024. Every choice
  "inevitably degrades the textures" —
  [M: Converting CC1, CC3 to CC3 Base+](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/05-Character/Converting-CC3-to-CC3-Plus.htm).
- Load Neutral Base resets CC1, CC3, CC3+ or CC5 HD. You choose Replace All, Replace Character (Keep
  Outfit) or Replace Outfit Only. Baked morphs can't be undone any other way —
  [M: Loading Neutral Base](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/05-Character/Loading-Neutral-Base-Characters-of-Different-Generations.htm).
- There are three character categories:
  - Standard: Reallusion bones, morphs and swappable parts.
  - Humanoid: characterised to Reallusion bones; can't swap body parts or clothes.
  - Creature: its own skeleton, no facial controls, nothing swappable.
  - Source: [M: Characters in Character Creator](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/05-Character/Characters-in-Character-Creator.htm).
- The embedded CC5 standard characters are "sub-divided to level 2 already". Subdivide adds a level
  (up to 2); Delete Highest SubD removes one. Viewport and render levels are set separately —
  [M: Increasing and Switching Subdivision Levels](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/05-HD-Character/Increasing-Mesh-Level.htm).
- Upgrading CC3+ to HD: raise the mesh level, add HD morphs, eyes and lashes, upgrade materials
  (redness, displacement, baked normals and wrinkles), then apply the HD facial profile —
  [M: Upgrading CC3+ to CC5](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/05-HD-Character/Upgrading-CC3Plus-Characters.htm).
- Each SubD level has its own normal map. One map can be linked across levels (for example, baked
  from SubD 2) — [M: Normal Maps and Subdivision Levels](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/05-HD-Character/Normal-Maps-and-Subdiviaion-Levels.htm).

### Morphs
- In the Morph Slider Editor, a custom slider's value range is −100 to 100. The source is a rigged
  character (current, or an iAvatar file); the target is OBJ or GoZ. "Auto apply" sets the new
  slider to 100 — [M: Morph Slider Editor UI](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/06_Customizing_Morphing_Sliders/User_Interface.htm);
  [M: Preparing Source Morph](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/06_Customizing_Morphing_Sliders/Preparing_Source_Morph.htm).
- "Create Head & Body Morph Sliders" turns the current shape into sliders under Head, Body or both —
  [M: Creating Head and Body Morphing Sliders](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/06_Customizing_Morphing_Sliders/Creating-Head-and-Body-Morphing-Sliders.htm).
- Bake keeps the shape and resets the active sliders to 0. Reset is then disabled —
  [M: Baking Morphing Results](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/06_Body/Baking_Morphing_Results.htm).
- HD morph sliders sit in "HD Body" and "HD Head" under Actor. They work at every SubD level and
  can be mixed with the legacy sliders —
  [M: Full Body Alterations with HD Morph Sliders](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/05-HD-Character/Full-Body-Alteration-with-Morph-Sliders.htm).
- Displacement is an EXR height map in the head, body, arm and leg channels. It "requires actual
  changes in geometry", so SubD 2 is recommended to see it; it's meant for Maya and Blender renders —
  [M: Displacement Map for HD Characters](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/05-HD-Character/Displacement-Map-for-HD-Characters.htm).

### Head and face
- Extended Plus vs HD: 68 vs 128 corrective rule sliders (mouth only vs mouth and eyes), 26 vs 52
  non-linear sliders, 254 vs 390 sliders in total. HD is "fully compatible with Unreal Engine's
  MetaHuman system" —
  [M: Why Extended Plus and HD Facial Profiles](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/05-HD-Character/Why-ExPlus-HD-Facial-Profiles.htm).
  - Conflict: another page says Extended Plus "introduces 50 non-linear sliders" —
    [M: Extended Plus Facial Profile](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/05-HD-Character/Extended-Plus-Facial-Profile.htm).
    Round one's ARKit mapping page gave 48.
  - Assessment: 160 + 68 + 26 = 254, so 26 matches the total.
- A corrective rule slider is named after the two sliders whose combination breaks the face,
  joined by an underscore (e.g. `CornerPullR_SharpCornerPullR`). Moving any of the three keeps them
  in sync — [M: Using Corrective Rule Sliders](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/05-HD-Character/Using-Corrective-Rule-Sliders.htm).
- To check a face, play the Extended_Step and Extended_Linear calibration animations. Fix bone
  misalignment with Adjust Bones or Proportion, and transition flaws with corrective morphs —
  [M: Refining Expressions](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/05-HD-Character/Refining-Expressions-by-Bones-or-Corrective-Morphs.htm).
- Expression sets:
  - CC3 Traditional: 60 sliders (iClone 5–7).
  - CC4 Extended ("Hybrid / Film Set"): the most sliders, matching MetaHuman "as possible" for Live
    Link.
  - CC4 Standard ("ARKit / Expression Plus Set"): 52 ARKit + 11 tongue sliders.
  - Viseme sets: 8+7 Phoneme Pair or 1:1 Direct.
  - Source: [M: Expression Set and Viseme Set](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/06-Facial-Profile-Editor/Expression-and-Viseme-Sets.htm).
- The 15 visemes are AE, Ah, B_M_P, Ch_J, EE, Er, F_V, Ih, K_G_H_NG, Oh, R, S_Z, T_L_D_N, Th, W_OO.
  8+7 builds them from 8 lip shapes and 7 tongue moves —
  [M: 8+7 and 1:1](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/06-Facial-Profile-Editor/8_7_and_1_1.htm).
- Facial rigs can be bone-based, morph-based or hybrid. A morph-based face keeps only the two eye
  bones — [M: Types of Facial Expressions](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/06-Facial-Profile-Editor/Types-of-Facial-Expressions.htm).
- Batch import of edited expressions (FBX "Mesh and Expression Sequence", one key per slider at its
  maximum). "The vertex number should never be changed", and Blender exports need Add Leaf Bones off —
  [M: Adjusting Expressions with FBX](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/06-Facial-Profile-Editor/Adjusting-Expressions-for-Standard-Characters_FBX.htm).
- Expression wrinkles come in three sets, each with diffuse, normal and roughness maps for its own
  face regions:
  - Set 1: forehead, blink, eye bags, lip lines, mental creases, neck.
  - Set 2: frown, bunny lines, nasolabial, marionette and jowls, neck.
  - Set 3: crow's feet, nasolabial lines, dimples.
  - Source: [M: Regions and Wrinkle Sets](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/06-Wrinkle/Relationships-Between-Regions-and-Wrinkle-Sets.htm).
  - Mesh wrinkles use the paid "Smile_Line" sliders —
    [M: Concepts of Expression Wrinkles](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/06-Wrinkle/Concepts-of-Expression-Wrinkles-System.htm).

### Skin and materials
- SkinGen divides each CC3+ character into 6 material regions —
  [M: Character Materials Regions](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/15-SkinGen/Basic-Concepts/Regions-of-Character-Materials.htm).
  The names are in images; the TOC titles give Head, Body, Arm, Leg, Nails and Eyelash.
- Skin has 7 layers: Skin Base (not removable), Normal Effects, Skin Details, Blemish, Acquired,
  Body Hair, Nail — [M: Skin and Makeup Layers](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/15-SkinGen/Basic-Concepts/Skin-and-Makeup-Layers-Concepts.htm).
- SkinGen requirements:
  - Minimum: GTX 600 / HD 7000 and 2 GB VRAM.
  - For 4K editing: 32 GB RAM, 6 GB VRAM and a 500 GB DDS cache.
  - Edit at 512 and switch up afterwards.
  - Source: [M: SkinGen Performance](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/15-SkinGen/Basic-Concepts/Performance-Enhancements.htm).
- Digital Human shaders by part:
  - Head: head only.
  - Skin: body, arms, legs and nails.
  - Hair: hair, not the scalp.
  - Eye: cornea only.
  - Teeth Gums; Tongue.
  - Source: [M: Shaders in DHS](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/15_Digital_Human_Shader/Shaders_in_Digital_Human_Shader.htm).
- The Skin shader uses 5 textures: Transmission, SSS, Micro Normal Mask, Micro Normal, RGBA Area Mask
  (four roughness zones) — [M: Skin Textures](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/15_Digital_Human_Shader/Skin/Texture.htm).
- The Head shader uses 11 textures: Base Color Blend, Normal Blend, Transmission, SSS, Micro Normal
  Mask, Micro Normal, Specular Mask, MN Mask & AO, NMUIL Mask, Ear Neck Mask, CFULC Mask —
  [M: Head Textures](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/15_Digital_Human_Shader/Head/Texture.htm).
- The PBR shader type has up to 9 map channels per material —
  [M: Types of Maps – PBR](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/15-Multiple-Channel-Texture-Mapping/Types_of_maps_PBR.htm).
- Material files: `.iMtl` holds one material; `.iMtlPlus` packs several into one file —
  [M: Material Tools](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/04-Introducing-the-User-Interface/Modify-Material-Tools.htm);
  [M: Material Plus](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/15_Material_Plus/Material_Plus.htm).
- New in the 5.12 folder:
  - Merge Materials (UV) bakes any materials into one; it converts a Standard character to Humanoid
    and removes its LODs.
  - Unify Materials by Name.
  - Link Identical Texture Maps (example: 1.3 → 1.1 GB VRAM, 339 → 292 MB project).
  - Source: [M: Merging Materials](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.12/15-Multiple-Channel-Texture-Mapping/Merging-Materials.htm);
    [M: Linking Identical Textures](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.12/15-Multiple-Channel-Texture-Mapping/Linking-Identical-Textures-in-Project.htm).
- The Substance Painter round trip uses OBJ with Painter's UV Tile workflow, OpenGL normals, and a
  Reallusion export preset (`Character_Creator.spexp`). Material names must be unique and without
  spaces — [M: Exporting Substance Source](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/15_Substance_Painter/Exporting-Substance-Source.htm);
  [M: Import OBJ in Substance Painter](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/15_Substance_Painter/Import-OBJ-in-Substance-Painter.htm).

### Eyes, lashes, teeth
- Eye Occlusion simulates eyelid shadow; Tearline fakes the wet line. Both follow eye-socket morphs
  and animation. Characters converted from CC1, CC3 or Transformer don't get them by default; add
  them with Add Eye Element —
  [M: New Eye Elements](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/15_Digital_Human_Shader/Eyes/New-Eye-Elements.htm).
- HD lashes stack on top of the legacy lashes (which are then hidden) and use the Digital Human hair
  shader. Morph sliders act on the legacy lashes, which drive the HD ones —
  [M: New Eyelash System](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/08-HD-Eyelashes/New-Eyelash-System.htm).
- The lower teeth move with the teeth bone; bones must be re-placed if the teeth meshes move —
  [M: Optimal Teeth Bone Position](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/06_Body/Best_Position_for_Teeth_Bones_and_Meshes.htm).

### Hair
- Hair content is HairStyle → HairGroup (hair, brows, beard) → HairElement —
  [M: Smart Hair Content Structure](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/08-Hair/Smart-Hair-Content-Structure.htm).
- Hair physics is the soft-cloth system (Modify › Physics › Hair) —
  [M: Physics Settings for Smart Hair](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/08-Hair/Physics-Settings-for-Smart-Hair.htm).
- Conform regions: beard (full, moustache, goatee, sideburns, soul patch); eyebrows (middle, upper,
  lower) — [M: Facial Hair Conform Region](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/08-Hair/Conforming-Regions-for-Smart-Hair.htm).
- Custom hair is an OBJ or FBX accessory turned into hair with "Create Hair, Brows, Beard, Lashes".
  Hair from AI Mesh Generator attaches to the head automatically —
  [M: Creating Custom Smart Hair](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/08-Creating-Custom-Assets/Creating-Custom-Smart-Hair.htm).
- 5.2 hair binding presets choose which bones get weights:
  - Long: Spine01, Spine02, NeckTwist01, NeckTwist02, Head, L/R_Clavicle.
  - Medium and Short drop the lower bones in turn.
  - Soft-cloth physics overrides skin weights.
  - Source: [M: Hair Binding Presets](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.2/08-Creating-Custom-Assets/Hair-Binding-Presets.htm).

### Clothes
- 5.2 cloth categories, innermost to outermost: Gloves, Shoes, Underwear, Lower, Upper, Coat, Others —
  [M: Layering Clothing (5.2)](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.2/08-Cloth/Layering_Clothing.htm).
- How the old layer numbers map onto the eight categories —
  [M: Clothing Layer Category Mapping](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.2/08-Cloth/Clothing-Layer-Category-Mapping-for-CC5.1-Earlier-Users.htm):
  - Others / Accessories ← Cloth 3, 6, 16, 17, 19, 20
  - Coats ← 13, 15, 18
  - Upper ← 4, 7, 10
  - Lower ← 5, 8, 9, 11, 12, 14
  - Skin-tight Top ← 1
  - Skin-tight Bottom ← 2
  - Shoes ← Shoes 1, 2
  - Gloves ← Gloves 1, 2
- Collision types:
  - **Push-out** (CC4 legacy) keeps the inner garment and expands the outer one.
  - **Tuck-in (Preserve Outer)** keeps the outer garment and shrinks the inner one.
  - Shrink Wrap settings: Weight, Range, Tuck-in Blend Range.
  - Source: [M: Switching Collision Types](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.2/08-Cloth/Switching-Collision-Types.htm);
    [M: Shrink Wrap Settings](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.2/08-Cloth/Shrink-Wrap-Settings.htm).
- How Auto Hide Mesh works:
  - Wrist, head, neck, lower neck and shoulder areas always stay visible.
  - Each vertex's bind bone is evaluated, and a ray from that bone to the vertex hides the geometry
    between it and the outermost mesh.
  - Source: [M: Automatically Hiding Inner Meshes](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/08_Cloth/Automatically_Hiding_Inner_Meshes.htm).
- 5.2 Transfer Skin Weight presets: Default, Cloth, Dress, Vest, Hood, Gloves, Cloak, Shoes, Socks,
  and more — [M: Transfer Skin Weight Templates](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.2/08-Cloth/Transfer-Skin-Weight-Templates.htm).
- To test weights while painting, rotate a bone (E) or play calibration motions —
  [M: Calibrating Skin Weights](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/08-Creating-Custom-Assets/Calibrating_Skin_Weights.htm).
- Clothes made for CC1 or CC3 on a CC3+ body raise a weight-transfer choice, because CC3+ weights
  "deviate significantly" — [M: Mix-Dressing](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/08_Cloth/Dressing_Characters_of_Different_Generations.htm).
- Soft-cloth physics parameters:
  - Solver Frequency: e.g. 60 behaves like silk, 1200 like rubber.
  - Collision Margin.
  - Soft-vs-rigid collision and self-collision toggles.
  - Source: [M: Solver Frequency](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/20-Physics/Solver_Frequency.htm);
    [M: Collision Margin](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/20-Physics/Collision_for_Soft_Cloth.htm).

### Rigging and import
- Characterisation must map at least 15 bones and set a T-pose. HIK profile presets (`.3dxprofile`)
  automate it — [M: Auto T-Pose and Bone-Mapping](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/09-Import-Humanoid/Auto-Bone-Mapping-Method.htm).
- Bone types in the Bone List (F3):
  - HIK, Facial, Used (= Extend; can take springs and keys), Spring, Unused (invisible in iClone).
  - Facial bones must branch from the Head bone.
  - Source: [M: Bone List](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/04-Introducing-the-User-Interface/Bone-List.htm).
- The body skeleton, facial bones and eye bones can't be converted for springs; only accessory, hair
  and cloth bones or extensions such as tails can —
  [M: Adding Spring Effects to Characters](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/21-Spring/Adding-Spring-Effects-to-Characters.htm).
- A Humanoid's motions are applied to a hidden "virtual RL bone structure" that drives the custom
  skeleton — [M: Importing for Creating Humanoid Character](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/09-Import-Humanoid/About-Convert-to-Non-Stnadard-Character-Mode.htm).
- A Creature is animated only by key-frames or its own embedded motions, with no puppet or mocap —
  [M: Creating Creature Characters](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/09-Import-Creature/Importing-Model-to-Create-Non-Human-Character.htm).
- AccuRIG takes A- or T-pose scans and sculpts, single- or multi-mesh, with partial rigs. Custom
  skeletons convert to the Reallusion skeleton, keeping facial bones or not —
  [M: Creating Humanoid Characters with AccuRIG](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/09-AccuRIG/Creating-with-AccuRIG.htm).
- The CC3+ bind pose is an A-pose; CC1 and CC3 bind in a T-pose —
  [M: Bind-Pose for Exporting](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/17-Export/Bind-Pose-for-Exporting-Characters.htm).

### Mesh tools
- "Character Creator does not provide modeling features"; GoZ is the route —
  [M: Targets for GoZ](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/09_GoZ/Targets_for_GoZ.htm).
- Sculpt mode in Edit Mesh has three brushes (push, pull, smooth) —
  [M: Sculpting Meshes with Brushes](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/08-Creating-Custom-Assets/Sculpting_Meshes_with_Brushes.htm).
- Delta Mush has Strength, Iterations, Range (selection or all) and a reference mesh (default: the
  neutral character) — [M: Delta Mush](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/09-Editing-Meshes/Smoothing-Mesh-Faces-with-Delta-Mush.htm).
- Replace Mesh needs the same vertex count; OBJ round trips need "Keep Vert Order" —
  [M: Replacing Mesh](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/09-Pipeline/Replacing-Mesh.htm);
  [M: Main Menu – Mesh](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/03-Main-Menu/Menu-Mesh.htm).
- InstaLOD only works on worn items (hair, clothes, shoes, accessories), not skin, eyeballs or teeth.
  It triangulates and rebuilds UVs —
  [M: InstaLOD Mesh Optimization](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/09_InstaLOD/InstaLOD_Mesh_Optimization.htm).
- 5.2 AI Polygon Reduction (Mesh › Polygon Reduction):
  - By percentage (0.01–100%) or by face count (100–1,000,000), output as quads.
  - Example: 481,170 → 56,582 tris at a 25,000-face target.
  - Can re-bake textures for AI-generated props.
  - Source: [M: Using AI Polygon Reduction](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.2/09-AI-Polygon-Reduction/Using-AI-Polygon-Reduction.htm).
  - Whether it runs locally or in the cloud isn't stated.

### Pipeline
- FBX export settings:
  - Target Tool Preset.
  - FBX Options (mesh, motion, both, or "Mesh and Expression Sequence").
  - An HD Character SubD level, which needs InstaLOD off.
  - Source: [M: Exporting FBX Files](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/17-Export/Export-FBX.htm).
- Advanced General options: Axis, Auto Skin Rigid Mesh, Rename Morph Invalid Name, Rename Duplicate
  Bone Name, Reset Self Illumination, Bone Name lower-case —
  [M: FBX Advanced – General](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/17-Export/FBX-Advanced-Settings-General.htm).
- Texture options:
  - Merge Opacity to Diffuse, Unity Texture, Use Glossiness, Invert Opacity, UDIM, vertex colour.
  - Texture Presets: Unity (HDRP, MetallicAlpha, AO) and Unreal (ORM, Specular, AO).
  - Source: [M: FBX Advanced – Texture and UV](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/17-Export/FBX-Advanced-Settings-Texture-UV.htm);
    [M: Texture Preset](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/17-Export/FBX-Advanced-Settings-Texture-Preset.htm).
- Since CC 3.1, an FBX export is one FBX plus a JSON file that "records all the settings that can not
  be packed into FBX", LODs included —
  [M: Exporting Character with LOD from Different Versions](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/17-Export/Exported_Files_from_Different_Versions.htm).
- Subdivided export works for FBX, OBJ and USD. For OBJ it's limited to "Character with Current Pose"
  and "Selected Item" — [M: Using Subdivided Mesh](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/17-Export/Using-Subdivided-Mesh.htm).
- Unreal export: the UE5 (Skeleton) preset picks the Epic UE5 skeleton and an A-pose bind. SubD 1 is
  recommended. The manual's example uses UE 5.6.0 with Auto Setup 1.40 —
  [M: Exporting Characters to Unreal Engine](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/17-Metahuman-Interoperability/Exporting-Characters-to-UE.htm).
- Reallusion's FAQ test ("Embedded Ariana"):
  - FBX export at SubD 2 / 8K: 6.5 min.
  - UE import: SubD 0 5+ min, SubD 1 8+ min; SubD 2 "crashed after ~11 min" (out of memory).
  - CC5 HD characters carry "nearly 400 morph sliders".
  - Source: [KB: Minimum vs Recommended Specs](https://kb.reallusion.com/Print53239.aspx) (undated, page read).
- GoZ Plus needs CC 4.42 or later. Its support for diffuse, normal and SubD transfer excludes Game
  Base, CC3 Base, legacy G3/G4/G6, and the CC3+ eye occlusion and tearline —
  [M: Upgrading to GoZ Plus](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/09-GoZ-Plus/Upgrading-To-GoZ-Plus.htm);
  [M: CC object compatibility with ZBrush](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/09-GoZ-Plus/CC-Object-Compatibility-With-ZBrush.htm).
- Transformer versions: CC5 is needed for Daz G9 and HD Daz characters, which convert to the CC3+
  base. Poser and older Daz figures work only in CC4. Daz core meshes must keep their topology —
  [M: Compatible Characters](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/09_Transformer/Compatible-DAZ-Characters.htm).
- Export Head writes an FBX head for creating a MetaHuman —
  [M: Exporting Head Mesh for Creating MetaHuman](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/17-Export/Exporting-Head-Mesh-for-Creating-MetaHuman.htm).
- BVH export converts iMotion, iMotionPlus, rlMotion and rlPose —
  [M: Exporting Motions to BVH](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/17-Export/Exporting-Motions-to-BVH.htm).

### UI and settings
- "Qt UI is designed to let you drag, dock and combine" panels: stack or top-down docking, saved
  workspace layouts — [M: Docking Toolbars and Panels](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/04-Introducing-the-User-Interface/Docking_Areas.htm).
- Undo is configurable, up to **180** steps —
  [M: System Section](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/04-Introducing-the-User-Interface/System_Section.htm).
- The world axis shows R = X, G = Y, B = Z; the up axis isn't stated —
  [M: Display Section](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/04-Introducing-the-User-Interface/Display_Information_Section.htm).
- Performance settings: DLSS (Balanced, Quality, Performance, Ultra Performance), progressive texture
  loading, and DDS-cache compression —
  [M: Performance Section](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/04-Introducing-the-User-Interface/Performance-Section.htm).
- Interactive tooltips link to the manual and play tutorial videos —
  [M: Interface Section](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/04-Introducing-the-User-Interface/Interface-Section.htm).

Assessment:
- The manual shows a tool with deep presets on the user side but rules buried in file structure:
  fixed vertex order, key files, proprietary content types.
- Things JustStage can learn from:
  - The cloth categories with an explicit inner-to-outer order.
  - The two collision modes.
  - The corrective rules named after the slider pair they fix.

---

## 3 · Base-mesh counts per subdivision level and per mesh

### Published counts
- The base-model page's "Comparison of CC Base Generations" table, read from the page's HTML —
  [CC base-model page](https://www.reallusion.com/character-creator/cc-avatar.html) (undated, page read):

  | Row | CC3+ | CC5 HD SubD 1 | CC5 HD SubD 2 | Game Base |
  |---|---|---|---|---|
  | Bone count | 100 | 100 | — | 72 |
  | Total polycount (all elements) | 17,683 | 70,732 | 282,928 | 8,723 |
  | Full body polycount | 14,046 | 56,184 | 224,736 | 5,610 |
  | Head only | 4,758 | 38,324 | 76,128 | 1,466 |
  | Body only | 9,288 | 17,860 | 148,608 | 3,944 |
  | Texture count | 6 | 6 | — | 1 / 2 / 6 |
  | Expression set | Extended, 160 blendshapes | HD, 262 + 128 correctives | — | — |

- "All elements" means full body, eyeball, teeth, tongue, tear line and eye occlusion. "Full body" is
  head and body. "Head" includes the eyelashes and tear ducts. The CC3+ figures repeat exactly —
  [M: CC3 Base+ Characters](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/05-Character/CC3-Plus-Characters.htm) (page read).
  - Small difference: the manual gives Game Base head as 1,455; the base-model page gives 1,466.
- "Optimized quad for subdivision sculpting (13,580 face)"; the scope isn't stated —
  [M: Topology](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/05-Character/Topology-Mesh-Enhancements.htm) (page read).
- The Level Table, read from its HTML with column spans —
  [M: Character Level Table](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/09-Character-Level/Character-Level-Table-and-Distance.htm) (page read):

  | | Level 1 | Level 2 | Level 3 | Level 4 | Level 5 |
  |---|---|---|---|---|---|
  | Type | CC Standard | CC Standard | actorBUILD | LOD 1 | LOD 2 |
  | Bones | 101 | 101 | 101 | 54 | 22 |
  | Mesh (K) | 80 | 60 | 20 | 7 | 0.8 |
  | Camera distance | 0 m | 2.8 m | 10 m | 20.8 m | 42 m |

  - **Correction to round one**, which read actorBUILD as 60K, LOD1 as 20K and LOD2 as 7K.
  - The convert page says the same as the table: CC3+ 60K at 2.8 m / 101 bones, actorBUILD 20K at
    10 m / 101 bones, LOD1 7K / 54 bones, LOD2 0.8K / 22 bones —
    [M: Converting Character Levels](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/09-Character-Scalability/Converting-Character-Levels.htm) (page read).
- The LOD page's columns are: Subdivision Export **240k up**, CC Avatar (CC3+) **60k up**, actorBUILD
  20k, LOD1 7k, LOD2 0.8k. Its note: "Including cloth and hair" —
  [LOD page](https://www.reallusion.com/character-creator/lod-characters.html) (undated, page read).
- A user saw 62,763 triangles for a CC5 character at SubD 0 (outfit not stated), the same count in
  UE — [forum](https://discussions.reallusion.com/t/texture-streaming-pool-over-budget-ue-5-6-1-autosetup-2-0-cc5-characters/16262) (2026-01-01, page read).

### Reconciliation
Assessment:
- **13,580** (scope not stated) is about 466 faces below the 14,046 full body. That fits a body skin
  without the eyelashes, but no source says so.
- **17K** quads (character spec page, round one) is the 17,683 total, rounded.
- **70K** (the product page) is the CC5 HD total at SubD 1 (70,732).
- **60K / 60k up** is a dressed CC3+ character with hair, at SubD 0.
- **80K** (Level 1, 0 m) has no stated scope. It sits above the dressed 60K at 2.8 m and may be a
  close-up configuration.
- **240k+** is a subdivided export of a dressed character (about 60K × 4).
- Every total grows exactly ×4 per SubD level (17,683 → 70,732 → 282,928; 14,046 → 56,184 → 224,736),
  which is what Catmull-Clark gives on an all-quad mesh. So "polycount" here counts quad faces.
- The SubD 1 head/body split (38,324 / 17,860) does not equal 4 × 4,758 / 4 × 9,288 (19,032 /
  37,152), although both pairs add up to 56,184. The SubD 2 split does match ×16. The SubD 1 split on
  the page is probably an error.

### Per-mesh counts and vertices
- **Not published.** No page read gives separate counts for the eyes, teeth, tongue, lashes,
  occlusion or tearline, or any vertex count.
  - Tried: the manual (about 240 pages), the base-model, LOD and product pages, the KB articles, the
    issues thread, Reallusion's Blender add-on and in-app plugin code (no hard-coded counts), the
    cc5-mcp-server repo, and web searches including arXiv.
  - Only figure derivable: by subtraction, eyes + teeth + tongue + tearline + occlusion = 17,683 −
    14,046 = 3,637 polygons at SubD 0.
- Mesh object names seen in Reallusion's own code: `CC_Base_Body`, `CC_Base_Eye`, `CC_Base_Teeth`
  (upper/lower), `CC_Base_Tongue`, `CC_Base_EyeOcclusion`, and a tearline mesh (L/R) —
  [CCiC Blender Pipeline Plugin](https://github.com/reallusion/CCiC-Blender-Pipeline-Plugin) and
  [cc_blender_tools](https://github.com/reallusion/cc_blender_tools) (GPL-3.0, pushed 2026-09-11,
  file read (facts only)); `CC_Base_EyeOcclusion` also appears in a user post in the
  [issues thread](https://discussions.reallusion.com/t/15102) (2025-11-04, page read).

---

## 4 · Bone list and count per part; facial bones

### Counts Reallusion publishes (they conflict)
- **101**: "Standard (101 bones)" —
  [M: Level Table](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/09-Character-Level/Character-Level-Table-and-Distance.htm) (page read);
  [LOD page](https://www.reallusion.com/character-creator/lod-characters.html) (page read).
- **100**: the CC3+ and CC5 HD bone count —
  [base-model page](https://www.reallusion.com/character-creator/cc-avatar.html);
  [M: CC3 Base+ Characters](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/05-Character/CC3-Plus-Characters.htm) (page read).
- **108**: "The CC3+ character rig consists of 108 bones, which is more than the 68 bones of the UE4
  Mannequin" — [MetaHuman Interoperability manual: Skeleton Structures](https://manual.reallusion.com/Metahuman-Interoperability/Content/MetaHuman-Interoperability/17-Metahuman-Interoperability/Skeleton-between-CC-and-UE-Characters.htm) (undated, page read).
  The same text is in the [Live Link manual 1.36](https://manual.reallusion.com/Live_Link_Plugin/ENU/Live_Link_Plugin/1.36/Skeleton-between-HD-and-UE-Characters.htm) (page read).
- **CC5 adds bones**: "Ten additional bones have been added to the spine and head, aligning CC bones
  with UE 5's key structures". The UE5 skeletons have "two additional spine bones (a total of five)"
  and "additional finger bones at the palm" — same two pages (page read).
  - This conflicts with the base-model page, which gives CC5 HD 100 bones, the same as CC3+.
- Unreal's skeletons, per the same pages: MetaHuman 342 bones, UE5 Mannequin 89, UEFN 88, UE4
  Mannequin 68.

### Removal groups (published)
- Level 2 (54 bones) removes toe, facial, share, twist and breast bones, plus "Neck Twist 2". Level 3
  (22 bones) also removes the toe-base and finger bones —
  [M: Level Table](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/09-Character-Level/Character-Level-Table-and-Distance.htm) (page read).
- The tongue has three bones, which can be reduced on conversion. Facial options keep 8 eye-look
  sliders, 7 jaw sliders and 10 head sliders —
  [M: Custom LOD Settings UI](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/09-Character-Level/UI-for-Custom-LOD-Settings.htm) (page read).
- Up to 22 twist/share bones and up to 30 finger bones can be removed —
  [LOD page](https://www.reallusion.com/character-creator/lod-characters.html) (round one, page read).

### The CC3+ bone names, reconstructed
- Names collected from Reallusion's own GPL-3.0 Blender add-on (string constants, read for names only)
  — [cc_blender_tools](https://github.com/reallusion/cc_blender_tools) (`rigify_mapping_data.py`,
  `bones.py` and others; pushed 2026-09-11; file read (facts only)):
  - Centre (19): `BoneRoot`, `Hip`, `Pelvis`, `Waist`, `Spine01`, `Spine02`, `NeckTwist01`,
    `NeckTwist02`, `Head`, `FacialBone`, `JawRoot`, `UpperJaw`, `Teeth01`, `Teeth02`, `Tongue01`,
    `Tongue02`, `Tongue03`, `L_Eye`, `R_Eye`.
  - Per side, with `L_` / `R_` (41 each, 82 in all):
    - Arm: `Clavicle`, `Upperarm`, `UpperarmTwist01/02`, `ElbowShareBone`, `Forearm`,
      `ForearmTwist01/02`, `Hand`.
    - Fingers: `Thumb1–3`, `Index1–3`, `Mid1–3`, `Ring1–3`, `Pinky1–3`.
    - Torso: `Breast`, `RibsTwist`.
    - Leg: `Thigh`, `ThighTwist01/02`, `KneeShareBone`, `Calf`, `CalfTwist01/02`, `Foot`,
      `ToeBase`, `ToeBaseShareBone`.
    - Toes: `BigToe1`, `IndexToe1`, `MidToe1`, `RingToe1`, `PinkyToe1`.
  - Every name carries the `CC_Base_` prefix in CC exports. The root also appears as `RL_BoneRoot`.
    iClone exports drop the `CC_Base_` prefix (a comment in the add-on).
- Assessment:
  - 19 + 82 = **101**, the Level Table figure.
  - Removing toes (10), facial bones (10), share bones (6), twist bones (16 limb twists + 2
    RibsTwist), breasts (2) and NeckTwist02 (1) leaves exactly **54**.
  - Then removing the toe bases (2) and fingers (30) leaves exactly **22**.
  - 11 twist/share bones per side gives the LOD page's "up to 22"; 15 finger bones per side gives
    "up to 30".
  - This is a reconstruction, not a published list. The "100" figure may leave out the root; the
    "108" isn't explained by any source.

### Facial bones
- CC3+ facial bones (10): `CC_Base_FacialBone` (parent), `JawRoot`, `UpperJaw`, `Teeth01`, `Teeth02`,
  `Tongue01–03`, `L_Eye`, `R_Eye` — names in both Reallusion codebases (file read (facts only));
  three tongue bones per [M: Custom LOD Settings UI](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/09-Character-Level/UI-for-Custom-LOD-Settings.htm).
- CC faces are largely morph-driven. A purely morph-based face needs only the two eye bones —
  [M: Types of Facial Expressions](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/06-Facial-Profile-Editor/Types-of-Facial-Expressions.htm) (page read).
- The names of CC5's ten added spine and head bones were not found. The "Spine05" users mention is
  the UE5 skeleton's bone after export —
  [issues thread #6](https://discussions.reallusion.com/t/15102) (2025-08-28, page read).

---

## 5 · UDIM tile → material mapping (CC3+ and CC5 HD)

- The OBJ texture export for Substance Painter puts "all of the UDIM material textures including the
  head, body, arms, legs, nails, and eyelashes" in the `Std_Skin_Head` folder. Other textures export
  per material — [M: Source File](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/15_Substance_Painter/Source-File.htm) (page read).
- In Painter, "multiple UV sets present under Std_Skin_Head" show that UDIM was imported; you
  "identify the UDIM number by using the UV viewport" —
  [M: Import OBJ in Substance Painter](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/15_Substance_Painter/Import-OBJ-in-Substance-Painter.htm) (page read).
- Reallusion's Blender add-on rebuilds materials from UV U-ranges: 0–1 head (with the eyes, tongue
  and teeth told apart by vertex group), 1–2 body, 2–3 arms, 3–4 legs, 4–5 nails, above 5 eyelash —
  [cc_blender_tools `materials.py` `reconstruct_obj_materials`](https://github.com/reallusion/cc_blender_tools)
  (pushed 2026-09-11, file read (facts only); the function's call is commented out in `importer.py`).
  - Material names: `Std_Skin_Head`, `Std_Skin_Body`, `Std_Skin_Arm`, `Std_Skin_Leg`, `Std_Nails`,
    `Std_Eyelash`, `Std_Upper_Teeth`, `Std_Lower_Teeth`, `Std_Tongue`, `Std_Eye_R/L`,
    `Std_Cornea_R/L`, plus `Std_Eye_Occlusion_R/L` and `Std_Tearline_R/L` (same repo).
- The base-model page ticks "UDIM (added in v3.2)" for both CC3+ and CC5 HD, with 4K maps for the
  head, torso, arms and legs — [base-model page](https://www.reallusion.com/character-creator/cc-avatar.html) (page read).
  - Small conflict: the manual says "New in V3.3" —
    [M: CC3 Base+ Characters](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/05-Character/CC3-Plus-Characters.htm).
- Assessment:
  - Standard UDIM numbering (1001 + U offset) gives 1001 Std_Skin_Head, 1002 Std_Skin_Body,
    1003 Std_Skin_Arm, 1004 Std_Skin_Leg, 1005 Std_Nails, 1006 Std_Eyelash.
  - The eyes, teeth and tongue stay in 0–1 on their own materials.
  - No Reallusion page prints the tile numbers; this is code plus manual.
  - CC5 HD keeps the same layout.

---

## 6 · Prices

| Item | Price found | Source (date, label) |
|---|---|---|
| CC5 perpetual | $299 | [CG Channel](https://www.cgchannel.com/2026/01/reallusion-switches-up-iclone-and-character-creator-licensing/) (2026-01-12, page read) |
| CC5 + Headshot 3 Creator, perpetual | $498 / £369 | [Creative Bloq](https://www.creativebloq.com/3d/character-creator-5-review-unreal-engine-support-and-auto-rigging-make-it-a-joy-to-use) (2026-05-27, page read) |
| CC4 → CC5 upgrade | $229 at launch | [staff, Pete_RL](https://discussions.reallusion.com/t/13778) (2025-04-08, forum excerpt) |
| Character Creator 365 | $8.25/mo billed annually (= $99/yr); $29 monthly | Creative Bloq (page read); [staff, jason_RL](https://discussions.reallusion.com/t/17227) (2026-05-14, page read, "annual plans (30% off)"); CG Channel (page read) |
| **Character Creator 365 Pro** | **$33.25/mo billed annually (≈ $399/yr)**; monthly price not found | Creative Bloq (page read). Contents: "CC Deluxe, Headshot plugin and SkinGen Premium 4-in-1 Bundles" — [plans page](https://www.reallusion.com/plan-and-pricing/individual/subscription?product=cc) (undated, page read, no prices shown) |
| Reallusion 3D Suite 365 (CC Pro + iClone Pro) | $49.92/mo billed annually; $599/yr or $129/mo | Creative Bloq; CG Channel (page read). Staff gives $34.94/mo at 30% off (page read) |
| ZBrush Face Tools | Indie $299 (full CC4 licence, under $100,000/yr); Studio $1,490 | [CG Channel](https://www.cgchannel.com/2023/10/reallusion-ships-zbrush-face-tools) (2023-10-17, page read). The store lists a "ZBrush Face Tools (Indie)" for CC5; price is script-loaded |
| SkinGen Premium | $99 list (CC 3.3 launch). No current price found | [forum, CC 3.3 SkinGen First Look](https://forum.reallusion.com/PrintTopic446060.aspx) (about 2020, page read) |
| Iray plugin | Not found | — |
| FashionGen | Not found. Given free with $99 content orders in two promotions (to 2025-12-31 and January 2026) | [launch post](https://discussions.reallusion.com/t/16207) (2025-12-22, round one, page read); [manual install page](https://manual.reallusion.com/character-creator-fashiongen-plugin/install.htm) (page read, no price) |
| PRIME membership | $99/yr: 15% off code for all Reallusion stores, plus other perks | [KB 53029](https://kb.reallusion.com/Print53029.aspx) ("posted 4 years ago", page read). Renewal $79/yr — search snippet only |
| DA / Bonus / AI points | 100 points = $1. DA points come in 1,000 / 5,000 / 10,000 packs and never expire. AI points come from AI Cloud plans and reset monthly ("discounted by AI Cloud service tiers") | [DA points page](https://www.reallusion.com/da-points/default.html) (undated, page read) |
| AI Cloud plans | Free 500 AI points; Starter 1,100/month; Standard 3,500/month; Professional 9,500/month. Prices not shown | [AI Studio manual: Account Settings](https://manual.reallusion.com/ai-studio/ui/account-setting.htm) (page read) |
| Example AI price | Video Mocap 250 DA points per run (up to 60 s, one character) ≈ $2.50 | Digital Production (2025-11-03, search snippet only) |

Assessment:
- CC 365 Pro is about 4× CC 365 a year.
- Seen as a monthly cost, the full CC kit (Pro) is about $400 a year against $99 for the base app.

---

## 7 · Iray, MetaTailor, Python and Qt, the graphics API

### Iray in CC5: not supported
- Staff: "Headshot 1 and the Iray Plug-in are NOT supported in CC5" —
  [Pete_RL](https://discussions.reallusion.com/t/13783) (2025-04-08, page read).
- Users: "I show Iray Render as an option still for iClone and for CC4, but not CC5"; "CC5 does not
  support iray anyway" — [thread](https://discussions.reallusion.com/t/16491) (2026-01-27/28, page read).
  Users also speak of "the decommissioning of Iray" —
  [thread 15460](https://discussions.reallusion.com/t/15460) (2025-09-19, forum excerpt).
- The Iray product page names only "Character Creator 3 and iClone" —
  [Iray page](https://www.reallusion.com/render/iray/) (undated, page read).
- Assessment: the CC5 manual's Plugins menu entry for "Iray Render" is a leftover from CC4.
  Reallusion's path tracer is now RTX Render (below).

### MetaTailor plugin on CC5: works, after a short gap
- A user said the CC5 MetaTailor pipeline plugin was "missing from the initial release". Staff
  (luke_RL): "Yes, it will be released this week" (2025-09-15). On 2025-09-18 staff said "You need to
  set the CC5 program path first" —
  [thread](https://discussions.reallusion.com/t/15283) (page read).
- In 2026 users describe dressing CC5 characters through MetaTailor ("CC5 caracter in and out of
  Metatailor"), and say MetaTailor dresses non-CC characters that CC5's own clothes can't —
  [thread 16985](https://discussions.reallusion.com/t/16985) (2026-04/05, page read);
  [contest WIP 17747](https://discussions.reallusion.com/t/17747) (2026-08-11, forum excerpt).
- A user found the plugin asks for a paid MetaTailor subscription (no reply) —
  [thread](https://discussions.reallusion.com/t/15907) (2025-11-16, page read). For CC4, staff (Pete_RL, as quoted
  by a user) said the plugin "does require an active Pro subscription" —
  [thread 13683](https://discussions.reallusion.com/t/13683) (2025-05-07, forum excerpt).
- Bug: on "5.12" with MetaTailor 2.7, the character is replaced by a mannequin; status Active —
  [FeedbackTracker 12669](https://www.reallusion.com/FeedBackTracker/Issue/CC5-Character-not-uploading-to-meta-tailor) (2026-08-04, page read).

### Python and Qt in CC5
- Staff's CC5 sample plugins declare `rl_plugin_info = {"ap": "iClone", "ap_version": "8.0"}` and
  `import RLPy` — [Johnny_RL, morph sliders in CC5](https://discussions.reallusion.com/t/15814) (2025-11-06, page read);
  [Johnny_RL, accessory loading in CC5](https://discussions.reallusion.com/t/15908) (2025-11-21, page read).
- Reallusion's own in-app plugin for CC4/CC5 and iClone 8 imports `PySide2.QtWidgets`, `QtCore`,
  `QtGui` and `shiboken2`. Its README adds "Update to import for CC5 SubD characters" —
  [CCiC Blender Pipeline Plugin `btp/link.py`, `btp/qt.py`](https://github.com/reallusion/CCiC-Blender-Pipeline-Plugin) (pushed 2026-09-11, file read (facts only)).
  - Assessment: PySide2 exists only for Qt 5, so CC5's UI toolkit is Qt 5. The exact minor version
    (5.15.2 in the IC8 docs) wasn't re-confirmed for CC5.
- CC5 ships an interpreter, `CharacterCreatorpy`, in `Bin64`, with its own pip. Staff had a user
  upgrade numpy from 1.19.3 to 1.20.0, then 1.21.6, for Headshot 3 —
  [thread 17072](https://discussions.reallusion.com/t/17072) (2026-06-30 / 07-01, page read).
- The Python version conflicts:
  - IC8 docs: Python 3.8 and Qt 5.15.2 — [IC8 Python API](https://wiki.reallusion.com/IC8_Python_API) (2023-04-10, round one, page read).
  - A third-party CC5 project: "CC5 Python: Python 3.10 + PySide2 (not PySide6!)"; type hints need
    `from __future__ import annotations` —
    [cc5-mcp-server `CLAUDE.md`](https://github.com/MorphoCore-Pty-Ltd/cc5-mcp-server) (2026-09, file read (facts only)).
  - Assessment: numpy 1.19.3 and 1.20.0 shipped wheels only up to Python 3.9, while 1.21.6 also
    covers 3.10. So the evidence doesn't settle it; no Reallusion source states CC5's Python version.

### Viewport graphics API: DirectX 11
- "RTX Render is a second render engine that lives alongside the existing **DX11** engine. It does not
  replace DX11" — [staff, HansRL, RTX Render Open Beta (1)](https://discussions.reallusion.com/t/17902) (2026-07-13, page read).
- RTX Render:
  - Requirements:
    - Minimum: Windows 10 20H1 or 11, 16 GB RAM, NVIDIA GeForce RTX 3060 (8 GB), 100 GB SSD,
      "Graphics API: DirectX 12 (DXR 1.1)".
    - Recommended: RTX 4070 Super (12 GB), DXR 1.2.
    - NVIDIA Studio Driver 610.62 or later; the crash guide asks for 610.88 or later.
  - Not supported in RTX mode:
    - Displacement, AO, particles and PopcornFX, live Substance, toon, fog, GI settings, motion blur.
    - IES, light range and falloff.
    - The CC editing tools: Edit Mesh/Normal, Skin Weights, AccuRIG, Facial Profile Editor, SkinGen.
  - It comes as a separate unzipped build (iClone.exe or CharacterCreator.exe) next to the installed
    licence.
  - Sources: same post; [crash guide](https://discussions.reallusion.com/t/18035) (2026-07-29, page read).
- Beta3_0917 added volumetric spot and point lights, lens presets with sensor shift, AgX colour, and
  separate preview and final settings. Playback is about 3 FPS in RTX mode against about 60 in
  DX11 — [Beta3 post](https://discussions.reallusion.com/t/18527) (2026-09-23, page read).
- RTX Render and the real-time renderer are a "future free update". Renders from iClone Personal are
  for personal and social use only —
  [staff, iClone Personal / AI Studio launch](https://discussions.reallusion.com/t/17686) (2026-06-23, page read).
- The manual's cache page says DDS is "the basic image unit in Microsoft DirectX graphics" —
  [M: Cache Section](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/04-Introducing-the-User-Interface/Cache-Section.htm) (page read).
- Assessment:
  - CC5's core renderer is DX11 (Windows only).
  - The new path tracer is NVIDIA-only (RTX), DX12.

---

## 8 · Native file formats (`.ccProject`, `.ccAvatar`, iAvatar)

What is public:
- Native extensions named in CC5's own content —
  [M: New Embed Contents in Version 5](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/04-HD-Contents/New-Embed-Contents-in-Version-5.htm) (page read):
  - Project and character: `*.ccProject`, `*.ccAvatar`, `*.ccAvatarPreset`, `*.ccSlider`,
    `*.ccFacialProfile`.
  - Parts: `*.ccTeeth`, `*.ccEye`, `*.rlEyelashElement`, `*.rlWrinkle`, `*.rlHair`, `*.ccCloth`,
    `*.ccShoes`.
  - Skin and mixer: `*.ccSkin`, `*.ccSkinGenPreset`, `*.ccMixerPackage`, `*.ccMixerPreset`.
  - Motion and stage: `*.iMotionPlus`, `*.ccLightRoom`, `*.iAtm`, `*.iMtlPlus`, `*.iMtl`.
  - Also `.exr` displacement and `.png`/`.jpg` textures.
- `.iAvatar` is the export for iClone; CC1 and CC3 characters can be remeshed on export. "Selected
  Content" exports `*.iAccessory`, `*.iHair`, `*.iCloth` —
  [M: Exporting iAvatar](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/17-Export/Exporting_iAvatar.htm);
  [M: Main Menu – File](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/03-Main-Menu/Menu_File.htm) (page read).
- The **`.fbxkey`** — [M: About fbxkey file](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/08-Creating-Custom-Assets/About-fbxkey.htm) (page read):
  - It contains "DRM Base Content Information", the "bone scale for each bone", the "body skin
    weight for each vertex", and the "clothing type".
  - Without it, a character "will NOT be able to be imported back".
  - It's made only for character-only round-trip exports to Max, Maya or Blender: not for Unity or
    Unreal, and not when "Delete Hidden Mesh" or InstaLOD is chosen.
  - The import panel calls it a "Decrypt Key File", needed "to authenticate the assets" —
    [M: Settings for Importing Custom Assets](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/08_Cloth/Settings_for_Designed_Assets.htm) (page read).
- FBX exports carry a JSON sidecar of settings that FBX can't hold (§2). Reallusion's GPL Blender
  add-on reads it to rebuild materials. The same add-on also reads a binary "RLX" format for lights
  and cameras (big-endian values plus length-prefixed JSON blocks); whether it's sent by file or over
  the DataLink socket wasn't checked —
  [cc_blender_tools `rlx.py`](https://github.com/reallusion/cc_blender_tools) (file read (facts only)).
  - Assessment: the JSON keys are knowable from that GPL code; the native files are not.
- The content EULA policy calls "ccAvatars, ccProjects, ccSliders, ccHair, ccCloth, ccShoes, and
  ccGloves" "Character Creator's proprietary file format" (CC Components). "iContent" is "a
  proprietary file format … intended for use exclusively within Reallusion software" —
  [content policy](https://www.reallusion.com/license/content.html) (updated 2025-08-01, page read);
  [Content EULA §1.13](https://www.reallusion.com/Content/EULA/EULA.htm) (2025-08-01, page read).
- The content EULA also requires that 3D models shipped in your products "must be contained in
  proprietary formats so that they cannot be opened" by others (§6.3). Files from a lapsed content
  plan revert to "Trial Content … subject to DRM protection" (§3.2) — same EULA (page read).
- The software EULA forbids reverse engineering ("not to … reverse engineer, decompile, disassemble")
  — [Software EULA](https://www.reallusion.com/Content/EULA/AP/EULA_AP.htm) (2026-05-25, page read).

Not findable:
- No public description of the internal structure of `.ccProject`, `.ccAvatar` or `.iAvatar` (binary,
  zip or other), and no community parser.
  - Tried: web search, the manual, the forum (Reallusion's old forum: iAvatar export "requires iClone
    7 and either 3DXchange 7 Pipeline or Character Creator 3 Pipeline", no format talk), GitHub code
    and repository search, and RenderHub's format guide ("limited native support in external 3D
    software"; [RenderHub](https://www.renderhub.com/guides/3d-file-formats/iavatar), page read).
- Assessment: given the EULA's no-reverse-engineering clause and the DRM content, JustStage can only
  bring CC characters in through their FBX/OBJ/USD + JSON exports.

---

## 9 · Whether a 5.12 exists; build numbers

| Version | Build | Date | Source |
|---|---|---|---|
| 5.01 | 5.01.0909.1 | 2025-09-09 | [issues thread #108, staff Pete_RL](https://discussions.reallusion.com/t/15102) (page read) |
| 5.02 | 5.02.0923.1 | 2025-09-24 | same thread #129 (page read) |
| 5.03 | 5.03.1029.1 | 2025-10-30 | #145 (page read) |
| 5.04 | 5.04.1216.1 | 2025-12-23 | #155 (page read) |
| 5.05 | 5.05.1305.1 | 2026-01-06 | #157 (page read) |
| 5.06 | 5.06.1322.1 | 2026-01-26 | #166 (page read) |
| 5.07 | release note 2026-04-27; update **5.07.1705.1** on 2026-05-06 | | [release note](https://discussions.reallusion.com/t/17043); [staff HansRL, "build 5.07.1705.1"](https://discussions.reallusion.com/t/17155) (page read) |
| 5.1 | 5.1.1723.1 | 2026-05-25 | round one (page read) |
| 5.11 | **5.11.1823.1** | released 2026-06-23 | build from a user's Help › About — [thread 17072 #9](https://discussions.reallusion.com/t/17072) (2026-06-29, page read); release — [topic 17685](https://discussions.reallusion.com/t/17685) (page read). Paired with iClone 8.73: "iClone 8.73 / CC 5.11" — [joyhuang, thread 17928 #2](https://discussions.reallusion.com/t/17928) (2026-07-16, page read; not flagged as staff) |
| **5.12** | **5.12.1925.1** (the RTX beta build) and **5.12.1928.1** | August 2026 | users in [RTX Render Open Beta (1)](https://discussions.reallusion.com/t/17902) #54 (2026-08-03) and #62 (2026-08-05: "Character Creator 5: 5.12.1928.1", next to "iClone 8 RTX Beta: 8.74.5528.1") (page read) |
| 5.13 | **5.13.2031.1** | released 2026-09-01 | user: "product version 5.13.2031.1" — [thread 18419 #4](https://discussions.reallusion.com/t/18419) (2026-09-12, page read); release — [topic 18378](https://discussions.reallusion.com/t/18378) (page read) |
| 5.2 | not found | 2026-10-29 | [5.2 release note](https://discussions.reallusion.com/t/18782) (page read; no build stated) |

- More evidence for 5.12:
  - The Feedback Tracker's Version field reads "5.12" —
    [issue 12669](https://www.reallusion.com/FeedBackTracker/Issue/CC5-Character-not-uploading-to-meta-tailor) (2026-08-04, page read).
  - The manual has a `5.12/` folder of three topics (§2).
  - A Reallusion forum bug report names "CC 5.07 and CC 5.12" —
    [thread 18311](https://discussions.reallusion.com/t/18311) (2026-08-28, forum excerpt).
- The Character Creator Official category (all three listing pages via JSON) has release topics for
  5.01–5.07, 5.1, 5.11, 5.13 and 5.2, but **none for 5.12** —
  [category](https://discussions.reallusion.com/c/character-creator/official/22) (listing read 2026-10-29).
- Assessment: 5.12 shipped through the Hub between 5.11 (June 23) and 5.13 (Sept 1) without a forum
  release note. Its builds run 1925–1928.

---

## 10 · Any link between Z-Weave and CC

- The Z-Weave page names no third-party avatar source (no Character Creator, Reallusion, Daz or
  MetaHuman). It lists "Import DXF/OBJ/FBX", "Export DXF/OBJ/FBX/glTF/glb", "Export animation data
  (FBX+mc/Alembic/USD)", and its own formats (zpose / zcam / zbp for the "default avatar", rozy for
  patterns). Plugins: z-weave, z-maya, z-unreal —
  [z-emotion.com/z-weave](https://www.z-emotion.com/z-weave) (undated, page read).
- The help article "Custom Avatars" says custom avatars import as OBJ, FBX, GLB, glTF, USD or Alembic,
  with "Split per-vertex Normals" needed for OBJ and FBX from Maya. Alvanon avatars need `.avaz` plus
  a permission file — [Custom Avatars](https://help.z-emotion.com/hc/en-001/articles/6321035017999-Custom-Avatars)
  (search snippet only; the page returned 403).
- Reallusion's forum search for "z-weave", "zweave" and "z-emotion" returned no posts; web searches
  pairing Z-Emotion or Z-Weave with Reallusion, iClone or Character Creator found nothing (page read /
  search results, 2026-10-29).
- Assessment:
  - No integration exists in either direction.
  - A CC character exported as FBX or OBJ could be loaded into Z-Weave as a generic custom avatar,
    and garments could come back as OBJ or FBX accessories to fit in CC. That is an inference from
    the formats, untested.

---

## 11 · Licence lines (text served)

- **Reallusion Software EULA** (2026-05-25):
  - Licence: proprietary, perpetual or subscription; a subscription is a "Named User" right, used on
    one device at a time.
  - Commercial use: **yes** for images, video and models embedded in games, apps and 3D print.
  - The CC Base Model clause bars use "in any character generation system", for "AI training, machine
    learning, or synthetic data generation", in "any character-generating business", and reselling
    base-model meshes in third-party marketplaces.
  - It forbids reverse engineering.
  - Source: [EULA_AP](https://www.reallusion.com/Content/EULA/AP/EULA_AP.htm) (page read).
- **Reallusion Content EULA** (updated 2025-08-01):
  - Tiers: Standard (royalty-free, limited commercial licence; export to engines; use in games and
    XR) and Enterprise (negotiated; covers character generation and AI training).
  - Commercial use: **conditional** (by tier). The Standard licence excludes online or in-software
    character generation, character-generation APIs, and AI training —
    [Content EULA](https://www.reallusion.com/Content/EULA/EULA.htm) (page read).
- **Content licence tiers** (content policy, 2025-08-01):
  - iContent: 30% of Standard, renders inside Reallusion software only.
  - Standard: now includes export.
  - Extended: CC Components for mass character output in commercial games, XR and online services;
    one Standard licence covers one character in games.
  - Enterprise.
  - Commercial use: **conditional**.
  - Source: [content policy](https://www.reallusion.com/license/content.html) (page read).
- **Reallusion AI Service EULA** (2026-10-29):
  - Output rights follow the plan tier: "Free Plan: For testing and evaluation purposes only";
    Starter, Standard and Pro: "Commercial use granted".
  - Commercial use: **conditional** (by tier).
  - Source: [AI-Service](https://www.reallusion.com/Content/EULA/AI-Service.htm) (page read).
  - Conflict: a June 2026 staff post said the Starter tier is "limited to personal and social use" —
    [topic 17686](https://discussions.reallusion.com/t/17686) (2026-06-23, page read). The EULA dated
    today replaces it.

---

## Couldn't verify / open

- **Reddit (r/Reallusion and others)**: refused to both web search and fetch, so not reached.
  **Polycount** returned 403. **CGSociety** closed in January 2024. Outside opinion rests on one
  independent review (Creative Bloq), GameFromScratch, a CGDive listing, a third-party video summary
  and Epic forum bug reports.
- **Vertex counts** at any SubD level, and **per-mesh counts** (eyes, teeth, tongue, lashes,
  occlusion, tearline): not published. Tried the manual, product pages, the KB, Reallusion's two
  public plugin codebases, a third-party CC5 repo and web searches.
- **13,580 faces** and the Level Table's **80K** at Level 1: scope not stated anywhere.
- **Bone counts**: Reallusion says 100, 101 and 108 for CC3+. The 101-name list here is a
  reconstruction from Reallusion's GPL code, not a published list. **The names of CC5's ten added
  spine and head bones** were not found, and the base-model page still gives CC5 HD 100 bones.
- **UDIM tile numbers** aren't printed on any Reallusion page; the mapping comes from the add-on code
  and the manual.
- **Prices not found**:
  - Iray (never shown on any page found; not sold for CC5 anyway), FashionGen, today's SkinGen
    Premium and ZBrush Face Tools prices, the CC 365 Pro monthly price, and the AI Cloud plan prices.
  - Reallusion's store loads prices from a script, so the server HTML has none; the store's private
    API wasn't probed.
- **CC5's Python version**: 3.8 (IC8 docs, 2023) vs 3.10 (third party, 2026); no Reallusion statement
  for CC5. The exact Qt 5 minor version for CC5 wasn't confirmed.
- **The 5.2 build number** (released today).
- **AI Polygon Reduction**: local or cloud isn't stated.
- **Native file structure** (`.ccProject`, `.ccAvatar`, `.iAvatar`): nothing public. The EULA forbids
  reverse engineering, and the content files carry DRM.
- **Z-Weave**: the help article returned 403; no CC link exists in either direction.
- **Conflicts kept apart**:
  - Extended Plus non-linear sliders: 26 vs 50 (manual), 48 (round one's mapping page).
  - UDIM introduced in v3.2 vs v3.3.
  - Game Base head polycount 1,455 vs 1,466.
  - The SubD 1 head/body split on the base-model page doesn't match ×4.

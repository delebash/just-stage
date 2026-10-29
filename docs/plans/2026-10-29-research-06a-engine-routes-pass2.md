# Research 06a, pass 2 — engine routes (gap list S5)

Research agent notes, 2026-10-29. This pass fills the gaps in section S5 of
`2026-10-29-research-second-pass.md`; round one is `2026-10-29-research-06a-engine-routes.md`. Clean-room:
public docs, licence texts, release notes and repo files only. About 72 web searches used.

Every fact names its source, the source's date and how it was read:

- **page read** — fetched and read.
- **search snippet only** — seen in a search-result summary; the page was not opened.
- **repo file read** — fetched from raw.githubusercontent.com or projects.blender.org.
- **GitHub API** — read with `gh api`, read-only GETs.
- **Epic PDF read** — downloaded from an Epic host and converted with `pdftotext -layout`.
- **third-party quote** — a short clause quoted by ConductAtlas, an independent terms tracker.

Judgement is labelled **Assessment:** and kept apart from facts.

Files this pass made, all scratch (no commits):

- The Epic EULA PDF, from cdn1.epicgames.com:
  `F:\ClaudeCode\tmp\claude\E--Dev-3D\db107297-0b13-4da2-97d8-83fb9aaa2487\scratchpad\pass2-s5\dl\ue_eula_v2_r1.pdf`
  (64,041 bytes; SHA-256 `0fa36997…936ee459`).
- Its text:
  `F:\ClaudeCode\tmp\claude\E--Dev-3D\db107297-0b13-4da2-97d8-83fb9aaa2487\scratchpad\pass2-s5\txt\ue_eula_v2_r1.txt`.
- The Flax EULA text:
  `F:\ClaudeCode\tmp\claude\E--Dev-3D\db107297-0b13-4da2-97d8-83fb9aaa2487\scratchpad\pass2-s5\txt\flax_eula.txt`.
  It was converted from the copy that WebFetch kept of
  `flaxengine.com/wp-content/uploads/2017/11/Flax%20EULA.pdf` (WebFetch couldn't decode the PDF). No second
  download was made.

---

## Top findings

1. **Epic's merged EULA, read in full from an Epic host.** It keeps v15's Engine Tools definition word for
   word and the same rule for products. The document is an undated revision ("v2/r1") of the merged "Unreal
   Engine End User License Agreement", with a Royalty Addendum. It predates change-log update 20: it still says
   "Unreal Engine Marketplace" and "Notice of Distribution", has a 5% rate only, and puts law in North Carolina.
   - "* If your Product includes Engine Tools, it may only be Distributed pursuant to (C) above" — that is,
     only to other Unreal licensees, "through either the Unreal Engine Marketplace or through a fork of Epic's
     GitHub UnrealEngine Network".

   [cdn1.epicgames.com …/unreal_engine/en/v2/r1/7be11df29cd87f4c3fe0032ad5bc3220.pdf, undated, Epic PDF read](https://cdn1.epicgames.com/eulatracking-download/unreal_engine/en/v2/r1/7be11df29cd87f4c3fe0032ad5bc3220.pdf)
2. **The current EULA keeps the same Engine Tools channel, now named Fab.** It also adds seat subscriptions,
   the 3.5% rate, and clauses on AI, MetaHuman and cloud features. ConductAtlas quotes the 2026-05-05 text:
   - "If your Product includes Engine Tools, you may only Distribute it through either the Fab Marketplace or
     through a fork of Epic's GitHub UnrealEngine Network."
   - Seats are needed "for each developer … unless you qualify for an exception", and there is no seat need
     while "you, together with any entities in your corporate group, have generated less than $1,000,000 USD
     in gross revenue over the last 12 months".

   A newer capture (2026-10-13) exists, but ConductAtlas has not re-checked these clauses against it.
   [ConductAtlas, captured 2026-05-05, third-party quote](https://conductatlas.com/platform/unreal-engine/unreal-engine-eula/provision/CA-P-059496/engine-tools-distribution-restricted-to-fab-or-github/)
3. **Unreal's runtime export is narrow:**
   - **glTF:** export works at runtime, but material baking and material-expression matching do not.
   - **FBX:** there is no built-in runtime exporter. The FBX factory needs `UnrealEd`; only paid third-party
     Fab plugins export FBX from packaged builds.
   - **USD:** a stage can be *loaded* at runtime (Set Root Layer); no runtime export is documented.

   [Epic glTF scripting docs (zh-CN), search snippet only](https://dev.epicgames.com/documentation/unreal-engine/scripting-gltf-exports-in-unreal-engine?lang=zh-CN)
4. **Unreal MCP (5.8) is an experimental editor plugin.** It serves HTTP at `127.0.0.1:8000/mcp` with no
   authentication, and runs tool calls one at a time on the game thread. Toolsets are added in Python or C++
   through the Toolset Registry. Since 2026-08-20 it also runs in UEFN.
   [dev.to guide, 2026-07-28, page read](https://dev.to/gamedevtoollab/using-unreal-mcp-in-ue-58-from-codex-setup-toolsets-and-safe-editor-automation-4pon) ·
   [fortnite.com, 2026-08-20, search snippet only](https://www.fortnite.com/news/unreal-mcp-is-now-available-in-uefn)
5. **Flax's EULA (last updated 2023-10-31), read in full, has the same shape as Unreal's:**
   - "The Product may not contain … any Engine Tools."
   - Public distribution of Engine Tools only "through the Store … or through a fork of Flax's GitHub Network".
   - GPL, LGPL (except dynamic linking) and CC-BY-SA are prohibited; BSD, MIT, Ms-PL and Apache are allowed.
   - "You may not sublicense the Licensed Technology in Source Code format."

   [Flax EULA PDF, 2023-10-31, page read (WebFetch copy converted)](https://flaxengine.com/wp-content/uploads/2017/11/Flax%20EULA.pdf)
6. **O3DE ships `Skin` and `Eye` material types, which closes round one's "skin SSS not found".**
   - `Skin`: "tailored for rendering skin, with support for blended wrinkle maps that work with animated vertex
     blend shapes". It has a subsurface-and-transmission group, dual specular, and up to 4 wrinkle layers
     driven by `COLOR0`.
   - `Eye`: refraction, iris and sclera, and limbus size.

   [O3DE Materials/Types, development branch, GitHub API + repo file read](https://github.com/o3de/o3de/tree/development/Gems/Atom/Feature/Common/Assets/Materials/Types)
7. **O3DE has no exporter.** No export Gem exists in o3de or o3de-extras. Its docs: "O3DE uses `.fbx` as its
   primary format for scene source assets … support for `.gltf` is enabled and currently in development"
   (through Assimp).
   [docs.o3de.org scene settings, page read](https://www.docs.o3de.org/docs/user-guide/assets/scene-settings) ·
   [GitHub API Gems listing, 2026-10-29](https://github.com/o3de/o3de/tree/development/Gems)
8. **Blender's Vulkan default comes in 5.3, not 5.1.** The 5.3 notes say "Vulkan backend is now default on
   Windows (not ARM) and Linux"; 5.3 "is currently in **Beta** until November 4, 2026".
   [blender-developer-docs release_notes/5.3, repo file read 2026-10-29](https://projects.blender.org/blender/blender-developer-docs/src/branch/main/docs/release_notes/5.3/eevee.md)
9. **Upstream Blender has no GPU skinning.** PR #149020, "WIP: Accelerate ArmatureModifier via GPU Compute",
   has been open and unmerged since 2025-10-29 (last update 2026-08-04). UPBGE 0.50 has experimental GPU
   skinning. Blender 5.1 did make playback faster: shape-key playback in one chart is 158.7 fps against 39.2 in
   5.0.
   [projects.blender.org PR #149020, API read](https://projects.blender.org/blender/blender/pulls/149020) ·
   [blender.org 5.1, page read](https://www.blender.org/download/releases/5-1/)
10. **A commercial DCC is built on Godot.** Sparseal's Uniform, an iPad app for sculpting, low-poly modelling,
    UVs, retopology and PBR paint ($49.99), is "coded as a Godot 4 C++ module" and "uses Godot build system and
    rendering device for portability". Sparseal was founded by Blender's former sculpt lead and a Godot
    developer.
    [80.lv, 2023-11-21, page read](https://80.lv/articles/cozyblanket-devs-present-a-new-asset-creation-2d-3d-software-for-ipad/) ·
    [cgchannel, 2024-05-16, page read](https://www.cgchannel.com/2024/05/uniform-is-an-intriguing-ipad-modeling-and-painting-app)
11. **Godot has no official MCP, but many community ones.** The largest are Coding-Solo/godot-mcp (6,419 stars,
    MIT) and hi-godot/godot-ai (3,278 stars, MIT, pushed 2026-10-29). Built in are LSP (port 6005) and DAP
    (port 6006) while an editor runs.
    [GitHub API search, 2026-10-29](https://github.com/Coding-Solo/godot-mcp) ·
    [Godot 4.7 docs, page read](https://docs.godotengine.org/en/stable/tutorials/editor/external_editor.html)
12. **Stride 4.4 (2026-10-09) changes round one's "Windows-only editor".** Game Studio now runs on Linux through
    Proton/Wine, and "Game Studio is being rewritten to be cross-platform". The release also overhauled Vulkan
    and Direct3D 12 and added a CLI.
    [Stride releases/4.4.0 notes, GitHub API](https://github.com/stride3d/stride/releases/tag/releases%2F4.4.0)
13. **Tiny Glade uses Bevy ECS and Bevy App with a custom renderer** (Bevy's creator, on Bevy's blog,
    2024-08-10). Pounce Light's public forks include Bevy, MoltenVK (pushed 2026-05-06) and iced; they have no
    wgpu fork.
    [bevy.org fourth birthday, page read](https://bevy.org/news/bevys-fourth-birthday/) ·
    [GitHub API, PounceLight repos](https://github.com/PounceLight)
14. **Bforartists v5.2.0 is a full release.** GitHub lists it with `prerelease=false` and Intel and Apple
    Silicon Mac builds. The pre-release is v5.2.3 (2026-10-27), which settles round one's conflict.
    [GitHub API releases, 2026-10-29](https://github.com/Bforartists/Bforartists/releases)
15. **Epic's EULA currently bars AI training on Unreal Engine and MetaHuman outputs.** Tim Sweeney: "Yes
    currently but we are working to remove this restriction from EULA terms" (no timeline).
    [Game Developer, 2026-10-27, page read](https://www.gamedeveloper.com/programming/epic-is-updating-the-eula-to-allow-ai-training-on-outputs-from-unreal-engine-and-metahuman)

---

## 1 · Epic's own terms: the current EULA, the Royalty Addendum and seat terms

### What an Epic host serves as text

- **The merged EULA PDF is on Epic's own CDN.** It was found through a search result
  ([search snippet](https://cdn1.epicgames.com/eulatracking-download/unreal_engine/en/v2/r1/7be11df29cd87f4c3fe0032ad5bc3220.pdf)),
  downloaded with a plain `curl` (HTTP 200, `application/pdf`, 10 pages) and read in full. Epic PDF read; the
  document is undated.
- **The download path is versioned**: `eulatracking-download/<product>/<lang>/v<N>/r<M>/<hash>.pdf`. Other
  products on the same path:
  - `emporium/en/v4/r1/…pdf`, the Marketplace Content License
    ([search snippet only](https://cdn1.epicgames.com/eulatracking-download/emporium/en/v4/r1/2b42ccdae5f8a8b42f1d7e7f869e4c9c.pdf));
  - the Epic privacy policy and terms of service PDFs (search snippet only).

  The hash can't be guessed, so a newer `unreal_engine` revision could not be found. Not findable — tried: four
  searches for `eulatracking-download` paths, the Royalty Addendum and the Content License as PDFs.
- **The tracking API was not used.** Epic's Online Services rules say access is allowed only "through the SDK,
  the Developer Portal, or means as otherwise expressly authorized by Epic"
  ([onlineservices.epicgames.com AUP, search snippet only](https://onlineservices.epicgames.com/services/terms/aup?lang=ja)).
  So the undocumented `eulatracking` API that the launcher uses was not called.
- **Epic hosts that refused this pass** (none retried with other headers, archives or proxies):
  - `link.unrealengine.com/eula/unreal` → 301 to `www.unrealengine.com/eula/unreal`, which is known to
    refuse; not followed.
  - `www.twinmotion.com` news → 403.
  - `store.epicgames.com` → 403.
  - `www.epicgames.com/help` → 403.
  - `docs.unrealengine.com/5.2/…` → 403.
  - dev.epicgames.com pages return only their title. Their document JSON endpoint answered a Cloudflare
    challenge (403), so I stopped there.
- **A route for the user** (Epic help, search snippet only): "You can view and download the Epic Games
  agreements you have accepted from your account settings" (Account → Legal History). The current EULA PDF can
  be got there.
  [epicgames.com/help, search snippet only](https://www.epicgames.com/help/en-US/account-c-202300000001645/account-services-c-202300000001752/how-do-i-get-a-copy-of-the-agreements-i-have-accepted-with-epic-games-a202300000016118)

### The merged EULA v2/r1 (Epic PDF read; undated)

- **Products:** anything Distributed that incorporates the Licensed Technology "must incorporate the Licensed
  Technology only in object code and only as an inseparable part of the Product" (§3).
- **Royalty-free distributions (§3(a)):**
  - Non-Engine Products, e.g. "rendered video files" and "asset files, such as character models and
    animations … including in Products that use or rely on other video game engines".
  - Products that don't directly generate revenue.
  - Distribution inside your company group, or to a client who hired you.
  - Distribution to other licensees "through either the Unreal Engine Marketplace or through a fork of Epic's
    GitHub UnrealEngine Network". The text adds: "you may Distribute a plugin, modding tool, or editor to end
    users through the Unreal Engine Marketplace or through Epic's Unreal Engine GitHub repository."
- **The Engine Tools rule:** "* If your Product includes Engine Tools, it may only be Distributed pursuant to
  (C) above."
- **The Engine Tools definition (§3)**, identical to v15 §25: "(i) editors and other tools included in the
  Engine Code; (ii) any code and modules in either the Developer or Editor folders, including in object code
  format, whether statically or dynamically linked; and (iii) other software that may be used to develop
  standalone products based on the Licensed Technology."
- **End users (§3(c)):** "You may not permit your end users to incorporate any Licensed Technology into their
  own products, services, or other projects."
- **Public distribution of Engine Tools (§4(a)(i)):** "Any public Distribution of Engine Tools … must take
  place through a marketplace operated by Epic such as the Unreal Engine Marketplace (e.g., for Distributing a
  Product's modding tool or editor to end users) or through a fork of Epic's GitHub UnrealEngine Network".
- **Other languages (§4(c)):** an integration of a language other than C++ must be distributed "in Source Code
  … free of charge, to all third parties who are separately licensed by us to use Unreal Engine, and under a
  license that permits licensees to Distribute the integration free of charge, on all platforms, in any
  Product." Same as v15 §1(A)(f).
- **Non-compatible licences (§5(a)):** no combining with "GNU General Public License (GPL), Lesser GPL (LGPL)
  (unless you are merely dynamically linking a shared library), or Creative Commons Attribution-ShareAlike".
- **Supersedes the old agreements (§7(b)):** "this Agreement supersedes any prior Unreal Engine End User License
  Agreement For Publishing or … For Creators". Content moves to the "Epic Content License Agreement
  (unrealengine.com/eula/content)".
- **Governing law (§14):** North Carolina, Wake County.

### The Royalty Addendum, as in v2/r1 (Epic PDF read)

- **The rate:** "5% of all Royalty Revenue … regardless of whether that revenue is received by you or any other
  person". It is charged on gross revenue: on a $10 App Store sale, the royalty is $0.50.
- **Excluded from Royalty Revenue:**
  - Any calendar quarter in which the product grosses under $10,000.
  - "the first $1,000,000 in lifetime gross revenue for each Royalty Product", which in this revision "applies
    only if you have submitted your Notice of Distribution on time".
  - The first $5,000,000 from the Oculus Store.
  - Sales on the Unreal Engine Marketplace or the Epic Games Store.
  - Revenue from a product "Distributed … only to third parties who are separately licensed by us to use
    Unreal Engine".
  - MegaGrants.
  - Location-based use.
- **Reporting:** within 45 days of each quarter's end. Late fee: 2% per quarter, compounding.

### The current EULA (ConductAtlas quotes, taken from the text captured 2026-05-05)

All these are third-party quotes. ConductAtlas says each comes from capture CA-V-001373 (2026-05-05) and "has
not been re-checked" against its current capture CA-V-007505 (2026-10-13, unchanged as of 2026-10-21). It also
logged corrections: 2026-10-12, "Five provisions listed for the EULA had no source in any capture", withheld;
and 2026-10-06, one quote that "omitted the condition it depends on".
[ConductAtlas index, page read](https://conductatlas.com/platform/unreal-engine/unreal-engine-eula/)

- **Engine Tools channel:** "If your Product includes Engine Tools, you may only Distribute it through either
  the Fab Marketplace or through a fork of Epic's GitHub UnrealEngine Network."
  [CA-P-059496](https://conductatlas.com/platform/unreal-engine/unreal-engine-eula/provision/CA-P-059496/engine-tools-distribution-restricted-to-fab-or-github/)
- **Public distribution:** "Any public Distribution of Engine Tools … must take place through a marketplace
  operated by Epic such as the Fab Marketplace…"
  [CA-P-059472](https://conductatlas.com/platform/unreal-engine/unreal-engine-eula/provision/CA-P-059472/public-engine-code-distribution-only-via-epic-marketplace-or-github/)
- **Object code only:** "Any Product that you Distribute that incorporates Licensed Technology must incorporate
  the Licensed Technology only … and only as an inseparable part of the Product." Unchanged from v2/r1.
  [CA-P-059446](https://conductatlas.com/platform/unreal-engine/unreal-engine-eula/provision/CA-P-059446/object-code-only-distribution-requirement/)
- **End users:** "You may not permit your end users to incorporate any Licensed Technology into their own
  products, services, or other projects." Unchanged.
  [CA-P-059466](https://conductatlas.com/platform/unreal-engine/unreal-engine-eula/provision/CA-P-059466/end-users-cannot-incorporate-licensed-technology-into-own-products/)
- **Royalties or seats:** "you may need to pay Epic royalties on the worldwide gross revenue attributable to
  each Royalty Product. See the Royalty Addendum…" Then: "For any other use of the Licensed Technology, you
  will need to purchase seat subscriptions (described in Section 6(a)) for each developer who accesses the
  Licensed Technology unless you qualify for an exception."
  [CA-P-059444](https://conductatlas.com/platform/unreal-engine/unreal-engine-eula/provision/CA-P-059444/royalty-obligation-for-royalty-products/) ·
  [CA-P-059445](https://conductatlas.com/platform/unreal-engine/unreal-engine-eula/provision/CA-P-059445/seat-subscription-fee-requirement/)
- **Seat exceptions:**
  - Personal and indie: "During any period that you, together with any entities in your corporate group, have
    generated less than $1,000,000 USD in gross revenue over the last 12 months, the Seat subscription
    requirement will not apply to your Users."
  - Non-commercial: "The Seat subscription requirement does not apply to your Users when they are accessing
    the Licensed Technology…" (truncated; the condition is non-commercial use).
  - Educational institutions: title only (CA-P-059488).

  [CA-P-059486](https://conductatlas.com/platform/unreal-engine/unreal-engine-eula/provision/CA-P-059486/personal-and-indie-seat-subscription-exception/) ·
  [CA-P-059490](https://conductatlas.com/platform/unreal-engine/unreal-engine-eula/provision/CA-P-059490/non-commercial-use-seat-subscription-exception/)
- **Seat mechanics:** "An individual Seat is personal to the User to which it has been assigned". Titles also
  list "Two Users on One Computer Occupy Two Seats" and "Single User May Access from Multiple Computers".
  [CA-P-059480](https://conductatlas.com/platform/unreal-engine/unreal-engine-eula/provision/CA-P-059480/seat-assignment-personal-to-individual-user/)
- **The 3.5% rate:** "If your Royalty Product qualifies as a Launch Everywhere with Epic Release … the Royalty
  Rate will be reduced to 3.5% of all Royalty Revenue collected going forward across all platforms and stores."
  Other provisions on the page are about Epic Games Store parity (content, features, marketing) and a waiver of
  the iOS requirement.
  [CA-P-059597](https://conductatlas.com/platform/unreal-engine/unreal-engine-eula/provision/CA-P-059597/reduced-royalty-rate-of-35-for-launch-everywhere-with-epic/)
- **Ports:** "A Royalty Product includes any Ports of that Royalty Product." A Port is "an adaptation of an
  already released Royalty Product…"
  [CA-P-059462](https://conductatlas.com/platform/unreal-engine/unreal-engine-eula/provision/CA-P-059462/port-products-subject-to-royalty-addendum/)
- **The $1M lifetime exclusion:** quoted as "the first $1,000,000 in lifetime gross revenue for each Royalty
  Product;" with no Notice-of-Distribution condition in the fragment.
  [CA-P-059625](https://conductatlas.com/platform/unreal-engine/unreal-engine-eula/provision/CA-P-059625/first-one-million-usd-lifetime-gross-revenue-excluded/)
  The change log says update 20 removed the Release Form "as a condition to being entitled to the $1,000,000
  lifetime gross revenue royalty exclusion".
  [unrealengine.com change log, search snippet only](https://www.unrealengine.com/eula-change-log/unreal)
- **Generative AI:** the text forbids activities that "result in using the Licensed Technology as a training
  input to any Generative AI Program or as prompt-based input where the Generative AI Program trains on input
  data."
  [CA-P-059498](https://conductatlas.com/platform/unreal-engine/unreal-engine-eula/provision/CA-P-059498/prohibition-on-using-licensed-technology-as-generative-ai-training-input/)
- **MetaHuman and AI:** do not "use, or permit others to use, MetaHuman digital characters and animation curves
  (or any rendered output thereof if crafted to replicate the functionality of MetaHuman) to build or enhance
  any database or training…"
  [CA-P-059499](https://conductatlas.com/platform/unreal-engine/unreal-engine-eula/provision/CA-P-059499/prohibition-on-using-metahuman-for-ai-database-building/)
- **Cloud features:** "You will ensure you do not provide Cloud Input Data unless you have all rights necessary
  … obtained all necessary consents from any individuals whose likeness is captured". Titles also list "Epic
  Does Not Retain Cloud Input Data After Processing".
  [CA-P-059515](https://conductatlas.com/platform/unreal-engine/unreal-engine-eula/provision/CA-P-059515/user-must-have-rights-to-cloud-input-data-including-likeness-consents/)
- **Governing law** changed to New York: "governed by New York law, exclusive of its choice of law rules".
  [CA-P-059554](https://conductatlas.com/platform/unreal-engine/unreal-engine-eula/provision/CA-P-059554/new-york-law-governs-agreement-disputes/)
- **Late payments:** the provision titles name "Late Royalty Payments Accrue Interest at SOFR Rate" (v2/r1: a
  2% compounding late fee). Title only; text not shown.

### The change log and pricing (all search snippet only; Epic's pages refuse scripted reads)

- **Update 20:** adds the 3.5% "Launch Everywhere with Epic Release" rate; renames "Notice of Distribution" to
  "Release Form" and drops it as a condition of the $1M exclusion; adds "express language against use of the
  Licensed Technology as a training input or prompt-based input into Generative AI Programs".
  [unrealengine.com/eula-change-log/unreal, search snippet only](https://www.unrealengine.com/eula-change-log/unreal)
- **Update 21:** restricts using MetaHuman characters and animation curves with AI technologies; "defines the
  use of cloud features"; makes Ports subject to the Agreement; lets Epic share an employer-provided email with
  the employer to check seat compliance.
  [same, search snippet only](https://unrealengine.com/eula-change-log)
- **The Content License change log** has its own numbering. Update 2 lets third parties use UE-only content to
  make content for public distribution. Update 3 adds an AI section and bans "NoAI"-tagged content in
  generative-AI datasets.
  [unrealengine.com/eula-change-log/content, search snippet only](https://www.unrealengine.com/en-US/eula-change-log/content)
- **Seat price: $1,850 per seat per year.** Puget Systems' write-up of the subscription:
  - It applies to companies with "over $1 million in annual gross revenue" doing non-game work.
  - The subscription does not apply to "creating applications that rely on Unreal Engine code at runtime and
    are licensed to third-party users" — those pay the royalty instead.

  [Puget Systems, 2024-03-12, page read](https://www.pugetsystems.com/blog/2024/03/12/unreal-engine-5-4-subscription-what-you-need-to-know/)
- **Seats no longer bundle Twinmotion:** "Beginning May 27, 2026, Unreal Subscriptions no longer include
  Twinmotion and RealityScan."
  [Epic blog note, search snippet only](https://www.unrealengine.com/blog/we-are-updating-unreal-engine-twinmotion-and-realitycapture-pricing-in-late-april)
- **The price held in 2026, per one third-party site.** It says the $445 Twinmotion and $1,850 Unreal figures
  did not change between its April and September 2026 checks.
  [renderahouse.com, 2026, search snippet only](https://www.renderahouse.com/blog/twinmotion-pricing)
- **AI training on outputs:** Epic's EULA "does not allow any output from Unreal Engine or Epic's MetaHuman" to
  be used for AI training. Sweeney (on X, answering Kotaku's 2026-10-26 piece): "Yes currently but we are
  working to remove this restriction from EULA terms."
  [Game Developer, 2026-10-27, page read](https://www.gamedeveloper.com/programming/epic-is-updating-the-eula-to-allow-ai-training-on-outputs-from-unreal-engine-and-metahuman)

**Assessment: does v15's Engine Tools and distribution wording survive?**

- The definition is the same in v15 and in v2/r1, word for word.
- The current text (2026-05-05 capture) keeps the same structure:
  - object code only, as an inseparable part of a Product;
  - Engine Tools only to other licensees, publicly through an Epic marketplace (now "Fab") or a GitHub fork;
  - end users may not build on the Licensed Technology;
  - non-C++ language integrations free and in source.
- What changed since v15: two agreements merged into one; the Royalty Addendum; the 3.5% rate; seat
  subscriptions; New York law; and clauses on AI, MetaHuman, cloud features and Ports.
- Whether the *definition* text itself changed in the current version is unverified: ConductAtlas has no
  record of the definition.

---

## 2 · Unreal: runtime exporters, morph targets, the 5.8 MCP plugin, what a packaged app may include

### Runtime exporters

- **glTF:**
  - Epic's page covers "using the Export to glTF function from Blueprint or Python … and exporting at runtime".
  - At runtime, material baking and material-expression matching don't work. Most materials need a pre-baked
    glTF proxy material made in the editor, or C++ changes through the GLTFBuilder API.

  [dev.epicgames.com scripting glTF exports (UE 5.8; zh-CN copy), search snippet only — the page body is
  client-rendered](https://dev.epicgames.com/documentation/unreal-engine/scripting-gltf-exports-in-unreal-engine?lang=zh-CN)
- **What the glTF exporter covers:** materials, static meshes, skeletal meshes, animation sequences, level
  sequences and level variant sets.
  [dev.epicgames.com exporting to glTF, search snippet only](https://dev.epicgames.com/documentation/unreal-engine/exporting-unreal-engine-content-to-gltf)
- **glTF options:**
  - `export_morph_targets` exports morph targets.
  - `export_vertex_skin_weights` is required for animation sequences.
  - `export_uniform_scale` defaults to 0.01 (centimetres to metres).
  - The plugin and module are both named `GLTFExporter`.

  [UE 5.1/5.2 Python API GLTFExportOptions, search snippet only](https://docs.unrealengine.com/5.2/en-US/PythonAPI/class/GLTFExportOptions.html)
  (the page itself answered 403).
- **The glTF exporter replaced a third-party plugin:** a Fab listing says "Epic Games has implemented the
  functionality of this plugin into the engine itself as of Unreal Engine 5.4".
  [Fab/Marketplace listing, search snippet only](https://docs.unrealengine.com/marketplace/ja/product/unreal-to-blender-batch-exporter-gltf)
- **USD:**
  - Runtime *loading* exists: "Unreal Engine supports the loading of USD files at runtime through calling the
    Set Root Layer Blueprint node on a USD Stage Actor".
  - No runtime *export* is documented. Export is from the editor (Prism docs: Outliner, Sequencer, USD Stage
    window).

  [dev.epicgames.com USD, search snippet only](https://dev.epicgames.com/documentation/en-us/unreal-engine/universal-scene-description-in-unreal-engine) ·
  [prism-pipeline.com, search snippet only](https://prism-pipeline.com/docs/latest/plugins/USD/usd_in_unreal/)
- **USD in packaged builds is unreliable, per user reports:**
  - "[Runtime] USD components randomly fail to display in Packaged Build" (2026).
  - A UE 5.6.0 fix for USD static meshes at runtime by SixelA_EG, not Epic staff (2026-03-16): "at runtime,
    `BuildFromMeshDescription()` … does NOT initialize the `BuffersSize` property".

  [forum, search snippet only](https://forums.unrealengine.com/t/runtime-usd-components-randomly-fail-to-display-in-packaged-build-especially-in-large-levels/2758199) ·
  [forum post #13, page read](https://forums.unrealengine.com/t/has-anyone-actually-got-usd-to-work-at-runtime-on-a-packaged-build/1933902/13)
- **A "monolithic builds" reply on OpenUSD was not found:** one search summary credits an Epic reply saying
  "OpenUSD is not possible with packaged games since they are built monolithically". The page I opened didn't
  contain it. Unverified.
- **FBX:**
  - There is no built-in runtime FBX exporter.
  - A forum answer: "fbxfactory currently requires UnrealEd to be able to work and is meant to only be used in
    the editor".
  - Two paid Fab plugins export FBX from packaged builds ("Runtime Animation Exporter" and "Runtime FBX Mesh
    Exporter Pro").

  [answers.unrealengine.com, search snippet only](https://answers.unrealengine.com/questions/55385/view.html) ·
  [Fab listing, search snippet only](https://www.fab.com/listings/f50882ff-8e0b-4d8d-be7c-595437ba7455) ·
  [Fab listing, search snippet only](https://www.fab.com/listings/c453193e-8ffa-4d99-a13b-d936ff5d99ba)
- **Runtime mesh editing:** Geometry Script works on `UDynamicMesh` in Blueprint and Python. A user reports
  that every Geometry Script mesh-writing function crashes in packaged builds on UE 5.8.3 (unconfirmed by
  Epic).
  [forum, search snippet only](https://forums.unrealengine.com/t/all-geometry-script-mesh-writing-functions-crash-on-first-call-in-packaged-non-shipping-and-shipping-builds-ue-5-8-3-windows/2836311)

### Morph-target limits

- **No UE5 document states a hard cap** on morph targets per skeletal mesh (not findable: three searches for
  UE5 docs, cvars and MetaHuman counts).
- **The UE3-era docs:** no limit on active morph targets apart from processing and memory.
  [docs.unrealengine.com UDK MorphTargets, search snippet only](https://docs.unrealengine.com/udk/Three/MorphTargets.html)
- **UE 4.20/4.21 forum reports:** morph targets past the 127th did not respond with GPU morph targets on. The
  workaround was `r.MorphTarget.Mode 0` (CPU) or turning off "Use GPU for computing morph targets".
  [answers.unrealengine.com, search snippet only](https://answers.unrealengine.com/questions/858530/view.html)
- **Bone limits per section:** 65,536 by default; clamped to 256 without 16-bit index mode.
  [dev.epicgames.com skeletal mesh rendering paths, search snippet only](https://dev.epicgames.com/documentation/en-us/unreal-engine/skeletal-mesh-rendering-paths-in-unreal-engine)
- **MetaHuman face:** expressions are stored as joint animations, plus per-vertex displacement "only in LOD0".
  The LOD0 blend-shape count was not found.
  [MetaHuman DNA docs, search snippet only](https://dev.epicgames.com/documentation/metahuman/metahuman-dna-rig-definition-and-rig-operation)

### The 5.8 MCP plugin

- **Names and pieces:**
  - Plugin Browser name "Unreal MCP"; identifier and console prefix `ModelContextProtocol`.
  - The Toolset Registry (enabled as a dependency) discovers tools and generates schemas; AllToolsets enables
    the bundled toolsets.
- **Transport:** HTTP with Server-Sent Events at `http://127.0.0.1:8000/mcp`. It accepts loopback only and has
  "no authentication layer".
- **Behaviour:** tool calls are "executed serially on Unreal Engine's game thread". It serves Tools only (no
  Resources or Prompts).
- **Extending it:** custom toolsets derive from `unreal.ToolsetDefinition` (Python) or `UToolsetDefinition`
  (C++); `ModelContextProtocol.RefreshTools` reloads them.
- **Status:** described as "an experimental plugin that exposes Unreal Editor operations to AI agents".

[dev.to GameDevToolLab, 2026-07-28 (sources checked 2026-07-21), page read](https://dev.to/gamedevtoollab/using-unreal-mcp-in-ue-58-from-codex-setup-toolsets-and-safe-editor-automation-4pon)

- **Epic's API reference** has a `ModelContextProtocol` plugin with these classes: `FModelContextProtocolServer`
  (serves MCP tools over HTTP), `UModelContextProtocolSettings` (port, URL path, `bAutoStartServer`, a
  tool-search option), and `IModelContextProtocolModule`.
  [dev.epicgames.com API, search snippet only](https://dev.epicgames.com/documentation/unreal-engine/API/Plugins/ModelContextProtocol)
- **Epic's page "Unreal MCP in Unreal Editor":** tools for "spawning actors, configuring lighting, creating
  material instances, inspecting Slate widgets, and running automation tests". It warns that "many features
  are incomplete or missing". The server takes only local connections, with no authentication.
  [dev.epicgames.com, search snippet only](https://dev.epicgames.com/documentation/unreal-engine/unreal-mcp-in-unreal-editor)
- **In UEFN** since 2026-08-20: agents "write and compile Verse, place devices, and run play sessions". Not all
  5.8 toolsets work there yet.
  [fortnite.com news, 2026-08-20, search snippet only](https://www.fortnite.com/news/unreal-mcp-is-now-available-in-uefn)
- **Whether it runs in a packaged build:** not stated anywhere I could read. The guide calls it an
  editor-extension entry point and "warns against using it as a production-build endpoint".

### What a packaged Unreal app may include

- **Module host types:**
  - "Runtime loads on all targets, except programs".
  - "Editor loads only when the editor is starting up".
  - "DeveloperTool | Loads on any targets where bBuildDeveloperTools is enabled".
  - "UncookedOnly | Only loads in uncooked games".
  - "Developer" is deprecated.

  [dev.epicgames.com EHostType, search snippet only](https://dev.epicgames.com/documentation/unreal-engine/API/Runtime/Projects/EHostType__Type)
- **UnrealEd doesn't build for game targets:** user reports say UnrealBuildTool won't build `UnrealEd` for
  non-editor targets. The fix is a separate Editor-type module that the game target doesn't reference.
  [answers.unrealengine.com, search snippet only](https://answers.unrealengine.com/questions/712813/view.html)
- **Remote Control is off in packaged builds:** "Remote Control is disabled by default in packaged projects or
  in -game … You can enable Remote Control by adding … -RCWebControlEnable -RCWebInterfaceEnable".
  [dev.epicgames.com, search snippet only](https://dev.epicgames.com/documentation/en-us/unreal-engine/remote-control-for-unreal-engine)
  A third-party README confirms it: "If you are using a packaged UnrealEngine project … you need to run the
  UnrealEngine project with the -RCWebControlEnable flag", bound to 127.0.0.1 by default (port 30010 in its
  examples).
  [soda-sim-remote-ctrl README, repo file read](https://github.com/soda-auto/soda-sim-remote-ctrl)
- **The licence side:** see §1. A Product may carry the Licensed Technology only as object code, inseparable
  from it, and without Engine Tools — that is, without the editor, without the Developer and Editor folders'
  code, and without "other software that may be used to develop standalone products".

**Assessment:**

- A packaged JustStage on Unreal ships only Runtime-type modules (and DeveloperTool ones only in non-shipping
  builds). Every authoring tool and every exporter beyond glTF (with baked materials) is ours to write.
- Distributing an editor build goes only to people who already hold an Unreal licence, through Fab or a GitHub
  fork.

---

## 3 · Godot: MCP servers, control channels, and non-game products

### Control channels

- **No official MCP.** No Godot Foundation MCP and no godot-proposals issue for one were found (two searches).
  The Asset Library listings say they are "not affiliated with or endorsed by the Foundation".
  [godotengine.org asset library, search snippet only](https://www.godotengine.org/asset-library/asset/edit/23816)
- **Community MCP servers, largest first** (GitHub search for "godot mcp" returns 684 repos;
  [GitHub API, 2026-10-29](https://github.com/Coding-Solo/godot-mcp)):

  | Repo | Stars | Licence | Last push | What it is |
  |---|---|---|---|---|
  | Coding-Solo/godot-mcp | 6,419 | MIT | 2026-04-16 | Launches the editor, runs projects |
  | hi-godot/godot-ai | 3,278 | MIT | 2026-10-29 | "Production-grade MCP server" |
  | yurineko73/Godot-MCP-Native | 862 | MIT | — | MCP server written in Godot itself |
  | youichi-uda/godot-mcp-pro | 637 | NOASSERTION | — | 162 tools |
  | tugcantopaloglu/godot-mcp | 505 | MIT | — | 157 tools, GDScript and C# |
  | IvanMurzak/Godot-MCP | 316 | Apache-2.0 | — | C# editor addon |

- **Built in:** "Godot supports the Language Server Protocol (LSP) for code completion and the Debug Adapter
  Protocol (DAP) for debugging." "A Godot instance must be running on your current project"; the default ports
  are "6005 for LSP, and 6006 for DAP".
  [Godot 4.7 docs, page read](https://docs.godotengine.org/en/stable/tutorials/editor/external_editor.html)
- **Command line and headless:** round one's facts stand (page read). Re-checked: "RenderingDevice is not
  available when running in headless mode or when using the Compatibility rendering method".
  [Godot 4.7 class reference, page read](https://docs.godotengine.org/en/stable/classes/class_renderingdevice.html)
- **Accessibility:** 4.7 adds "Landmark navigation for enhanced accessibility".
  [godotengine.org/releases/4.7, page read](https://godotengine.org/releases/4.7/)

### Products built on Godot that are tools, not games

- **GameFromScratch's list (2024-02-20)** names 15 apps: the Godot Editor, Material Maker, Pixelorama, RPG In a
  Box, CozyBlanket, Uniform, PixelOver, The Mirror, Arrow, Union Bytes Painter, GodSVG, Dungeondraft,
  Wonderdraft, Lorien and Heavy Paint.
  [gamefromscratch, 2024-02-20, page read](https://gamefromscratch.com/godot-developed-non-game-applications/)
- **Uniform (Sparseal), a commercial 3D DCC on Godot:**
  - Pablo Dobarro (co-founder): Uniform is "coded as a Godot 4 C++ module" and "uses Godot build system and
    rendering device for portability".
    [80.lv, 2023-11-21, page read](https://80.lv/articles/cozyblanket-devs-present-a-new-asset-creation-2d-3d-software-for-ipad/)
  - Sparseal was "founded by former Blender sculpting tools lead Pablo Dobarro, and Godot Engine developer Joan
    Fons". iPad only at launch; desktop to "depend on distribution and hardware compatibility".
    [cgchannel, 2023-11-20, page read](https://www.cgchannel.com/2023/11/sparseal-unveils-uniform/)
  - Uniform 1.0: $49.99, iPadOS 17.4+.
    - Sculpting: "brushes can be customized with stamps, alphas and vector displacement maps".
    - Retopology: "Geometry can be retopologized by sliding edges around directly".
    - It covers UV unwrapping and paint of colour or displacement.

    [cgchannel, 2024-05-16, page read](https://www.cgchannel.com/2024/05/uniform-is-an-intriguing-ipad-modeling-and-painting-app)
- **CozyBlanket** is Sparseal's earlier iPad retopology app, listed as Godot-developed by GameFromScratch (page
  read above). Its use of Godot is not confirmed by Sparseal.
- **MSEP.one**, "a complex nanotechnology design utility using Godot" (GodotCon Boston 2025 talk, HP van
  Braam).
  [talks.godotengine.org, page read](https://talks.godotengine.org/godotcon-us-2025/speaker/XBY83F/)
- **The Mirror** is a Godot-based game-creation platform (listed by GameFromScratch).

**Assessment:** Uniform is the strongest evidence that a professional sculpt, model and paint DCC can be a
Godot C++ module using Godot's RenderingDevice. It is iPad only, so its desktop editor UI is unproven.

---

## 4 · Products built on O3DE, Stride, Flax, Fyrox and Bevy

- **O3DE:** "Made with O3DE" lists four games: State of Matter (PC, 2024-07-19); MadWorld (Android, iOS),
  Awaken Guardian (PC) and Reverb (PC), all three "TBD". No tools or simulations are listed.
  [docs.o3de.org, page read](https://docs.o3de.org/docs/learning-guide/made-with-o3de/)
  - Robotics: Robotec.ai joined in March 2023 and built the ROS2 and RGL lidar Gems. The ROS 2 integration is
    "currently supported only on Linux". The sources are promotional.
    [Linux Foundation press, search snippet only](https://www.linuxfoundation.org/press/open-3d-engine-sees-momentum-across-robotics-industry)
  - o3de-extras holds ROS2, ROS2RobotImporter, ROS2Sensors, SimulationInterfaces, WarehouseAutomation and
    MachineLearning Gems.
    [GitHub API, 2026-10-29](https://github.com/o3de/o3de-extras)
- **Stride:** the docs list as released Distant Worlds 2, FPS Infinite, Snaaker Friends, Children of the Galaxy,
  One Late Night: Remake, Banpo's Bridge Wondrous Worlds, Pistonica and DySector. One non-game app is listed:
  "Virtual Desktop", a "VR desktop streaming app powered by Stride".
  [doc.stride3d.net 4.3 games and demos, page read](https://doc.stride3d.net/4.3/en/community-resources/games-and-demos.html)
- **Flax:** the official and community project lists hold samples, plugins and tools only; none is marked
  shipped.
  [docs.flaxengine.com public projects, page read (commit a723b65)](https://docs.flaxengine.com/manual/contributing/public-projects.html)
  An undated forum post: "no serious game have been created with it, but a wishlist of one is available on
  steam" (Kostka).
  [forum.flaxengine.com, search snippet only](https://forum.flaxengine.com/t/im-evaluating-flax-looking-for-games-in-the-app-stores/766)
  No shipped commercial product found.
- **Fyrox:** the showcase lists Station Iapetus ("A DeadSpace-like horror game"), Fish Folly, rusty-shooter,
  soccer, RustCycles and Breakfloor. None has a release date or store link.
  [fyrox.rs/games, page read](https://fyrox.rs/games)
- **Bevy:** Bevy's own post (Carter Anderson, 2024-08-10) lists these shipped products:
  - games: Tunnet (Steam, itch.io), El Mono (Steam), GLOW (Steam), Zoolitaire (mobile);
  - Storyteller.ai, "AI music and film creation tool";
  - Foresight Spatial Labs' data-rendering tools;
  - Airbus satellite on-board software.

  It says Tiny Glade is "a game that uses Bevy ECS and Bevy App (alongside a custom renderer)".
  [bevy.org, 2024-08-10, page read](https://bevy.org/news/bevys-fourth-birthday/)
- **Tiny Glade:** "made with a custom version of Bevy". Full release 2024-09-23 (Windows, Linux); macOS on
  2026-05-13. By Pounce Light (Anastasia Opara, Tomasz Stachowiak).
  [Wikipedia, page read](https://en.wikipedia.org/wiki/Tiny_Glade)
  - Bevy's creator, earlier: "Tiny Glade … Uses Bevy ECS / Bevy App + a custom renderer".
    [HN comment by _cart, 2023-11-04, read via the HN Algolia API](https://news.ycombinator.com/item?id=38146018)
  - Pounce Light's public forks: `PounceLight/bevy` (from bevyengine/bevy, pushed 2024-08-29), `MoltenVK`
    (pushed 2026-05-06), `iced`, `winit`, `rapier`, `steamworks-rs`. No wgpu fork.
    [GitHub API, 2026-10-29](https://github.com/PounceLight)
  - **Assessment:** the MoltenVK fork, pushed a week before the macOS release, suggests a Vulkan renderer run
    on Metal through MoltenVK. This is an inference, not a source statement.

**Assessment:** none of the five has a shipped creation tool on the scale of a DCC. Bevy has the most shipped
products; O3DE's real use is robotics simulation.

---

## 5 · Blender: GPU skinning, the Vulkan default, and MIT in "GPL compliant"

- **GPU skinning is not in upstream Blender.** PR #149020, "WIP: Accelerate ArmatureModifier via GPU Compute,
  Improves performance by 10-15x", is open, unmerged, created 2025-10-29 and updated 2026-08-04. Its body
  lists open issues: the mesh is packed once and topology changes break it, and "GPU SubD modifier doesn't
  work".
  [projects.blender.org API, page read](https://projects.blender.org/blender/blender/pulls/149020)
  - In the thread (2025-12-01), fclem says the geometry-node modifier work (#142075) is not meant to replace
    the Armature modifier "in the short term", and that this GPU evaluation still makes sense.
  - A UPBGE developer ported UPBGE's skinning to the viewport in a branch (2025-11).
  - An earlier PR, #146505 "Add the possibility to deform objects with compute shaders in python", was closed.
- **UPBGE 0.50** (built on Blender 5.0.1) "launches with GPU skinning" (experimental).
  [alternativeto.net, 2026-01, search snippet only](https://alternativeto.net/news/2026/1/upbge-0-50-launches-with-gpu-skinning-faster-add-object-2d-filter-overhaul-and-more)
- **CPU playback got faster in 5.1:** "Blender 5.1 delivers a major boost to animation playback performance".
  Shape-key evaluation in one chart is about 158.7 fps against 39.2 fps in 5.0 (24 threads, Ryzen 9900X), and
  "Actions now evaluate much faster … on armatures with many bones keyed".
  [blender.org/download/releases/5-1, released 2026-03-17, page read](https://www.blender.org/download/releases/5-1/)
- **The Vulkan default comes in 5.3:**
  - 5.3 notes: "Vulkan backend is now default on Windows (not ARM) and Linux. (blender/blender!158803)". The
    minimum drops to Vulkan 1.1.
  - The 5.3 index: "Blender 5.3 is currently in **Beta** until November 4, 2026."
  - The 5.1 and 5.2 EEVEE notes don't make Vulkan the default (benchmarks only).

  [blender-developer-docs 5.3/eevee.md and index.md, repo file read 2026-10-29](https://projects.blender.org/blender/blender-developer-docs/src/branch/main/docs/release_notes/5.3/eevee.md)
  This settles round one's conflict (5.1 plan against 5.3) in favour of 5.3.
- **Release dates:** 5.0 "November 18th, 2025".
  [blender.org 5.0, page read](https://www.blender.org/download/releases/5-0/)
  5.1 "March 17th, 2026" (page read above).
- **EEVEE Next:** "EEVEE Next: Subsurface Scattering" (#107407) was merged 2023-06-15; "EEVEE Next: Hair &
  Curves" (#109833) was merged 2023-07-14.
  [projects.blender.org API](https://projects.blender.org/blender/blender/pulls/109833)
  The 5.2 notes add that EEVEE SSS "now evaluates indirect light separately" in some cases.
  [5.2/eevee.md, repo file read](https://projects.blender.org/blender/blender-developer-docs/src/branch/main/docs/release_notes/5.2/eevee.md)
- **MIT as GPL-compatible, one line:** the FSF list calls the Expat licence "a lax, permissive non-copyleft free
  software license, compatible with the GNU GPL. It is sometimes ambiguously referred to as the MIT License."
  This is quoted through a mailing-list copy
  ([koha-devel, 2015, search snippet only](https://lists.koha-community.org/pipermail/koha-devel/2015-April/041409.html)).
  gnu.org answered HTTP 429 twice and was not retried another way.

---

## 6 · O3DE skin, sequencer and export; export and Python for Stride, Fyrox and Bevy

### O3DE

- **The `Skin` material type** reads: "Material Type tailored for rendering skin, with support for blended
  wrinkle maps that work with animated vertex blend shapes." Its property groups:
  - Base Color, Occlusion, Normal, Roughness, Specular, **Dual Specular**, Detail Maps, and **Subsurface and
    Transmission**.
  - Wrinkle Layers: "The number of wrinkle map layers to use. The blend values come from the 'COLOR0' vertex
    stream, where R/G/B/A correspond to wrinkle layers 1/2/3/4", with base-colour and normal maps per layer.

  [Skin.materialtype, development branch, repo file read 2026-10-29](https://github.com/o3de/o3de/blob/development/Gems/Atom/Feature/Common/Assets/Materials/Types/Skin.materialtype)
- **The `Eye` material type** reads: "Material Type tailored for rendering eyes, with support for refraction,
  iris blending, and other eye-specific properties." It has iris depth and radius, "IOR Inner Eye" (aqueous
  humour) and limbus size.
  [Eye.materialtype, repo file read](https://github.com/o3de/o3de/blob/development/Gems/Atom/Feature/Common/Assets/Materials/Types/Eye.materialtype)
- **Other material types in the same folder:** `EnhancedPBR`, with `EnhancedPBR_SubsurfaceState.lua`, and
  `StandardMultilayerPBR`.
  [GitHub API listing, 2026-10-29](https://github.com/o3de/o3de/tree/development/Gems/Atom/Feature/Common/Assets/Materials/Types)
- **AtomTressFX:** "provides realistic hair and fur simulation and rendering … enhances the open source TressFX
  4.1 by AMD and includes a more advanced handling of lighting using the Marschner lighting model".
  [docs.o3de.org, page read](https://docs.o3de.org/docs/user-guide/gems/reference/rendering/amd/atom-tressfx/)
- **Track View, the sequencer:**
  - "the primary tool to create and manage cinematic sequences"; "you can use the Track View to control
    cameras, component entities, global variables in a level, and so on".
  - A track "displays animation keys on a timeline in relation to the property that is animated on a node".
  - Related pages: "Using Animation Curves", "Using Record Mode", "Capturing Image Frames".

  [docs.o3de.org Track View, page read](https://docs.o3de.org/docs/user-guide/visualization/cinematics/track-view/)
  It comes from the Maestro Cinematics Gem.
  [docs.o3de.org Maestro, search snippet only](https://docs.o3de.org/docs/user-guide/gems/reference/animation/maestro/)
- **Export:** none (see top finding 7). O3DE imports `.fbx` (primary), `.stl` and `.gltf` (in development)
  through Assimp. The 83 Gems in o3de/development and the o3de-extras Gems include no exporter.

### Stride

- **Export:** none found. The manual lists import formats only: ".3ds, .blend, .dae, dxf, .fbx, .glb, .gltf,
  .md2, .md3, .obj, .ply, .stl, .stp, .x".
  [doc.stride3d.net 4.2, search snippet only](https://doc.stride3d.net/4.2/en/manual/animation/import-animations.html)
- **Python:** none found. "Stride scripts are written in C#."
  [doc.stride3d.net, search snippet only](https://doc.stride3d.net/4.0/en/Manual/scripts/index.html)
  GitHub search for "stride3d python" returns 0 repos ([GitHub API](https://github.com/search?q=stride3d+python)).
  pythonnet could bridge Python to .NET, but no Stride use was found.
- **Skin SSS** (re-check): `MaterialSubsurfaceScatteringScatteringProfileSkin` "Calculates the scattering
  profile for skin, which is applied during the forward pass using the subsurface scattering shading model. It
  also calculates a scattering kernel based on the "Falloff" and "Strength" parameters."
  [doc.stride3d.net latest API, page read](https://doc.stride3d.net/latest/en/api/Stride.Rendering.Materials.MaterialSubsurfaceScatteringScatteringProfileSkin.html)

### Fyrox

- **Export:** the source tree has `fyrox-impl/src/resource/fbx` and `…/gltf` *loaders* ("GltfLoader enables the
  importing of *.gltf and *.glb files"). Its `export` folders (`editor/src/export`, `fyrox-build-tools/src/export`
  with android, pc and wasm) build games for platforms, not models. No model exporter.
  [GitHub API tree + gltf/mod.rs, master, 2026-10-29](https://github.com/FyroxEngine/Fyrox)
- **Renderer, newer than round one:**
  - Master is version `2.0.0-rc.1` and has `fyrox-graphics-wgpu` ("Wgpu-based graphics server for Fyrox Game
    Engine", MIT, wgpu 30.0.0).
  - The `fyrox` crate has features `backend_opengl` (the default) and `backend_wgpu`.
  - The latest release is still v1.0.0 (2026-03-29).

  [GitHub API, Cargo.toml files, master](https://github.com/FyroxEngine/Fyrox/tree/master/fyrox-graphics-wgpu)
- **The 1.0 RC post:** "The renderer still lacks any global illumination, but that's planned for the future
  releases (most likely for Fyrox 2.0)". OpenGL was isolated in its own crate "to transition to modern GAPIs".
  [fyrox.rs 1.0 RC 1, undated, page read](https://fyrox.rs/blog/post/fyrox-game-engine-1-0-0-rc-1/)

### Bevy

- **Export:** core Bevy has no glTF writer (none found).
  - `open-rmf/bevy_gltf_export` (MIT on GitHub; docs.rs lists Apache-2.0): "export arbitrary meshes and
    materials from Bevy into glb files. It currently doesn't support scenes". Last push 2025-10-24.
    [README, repo file read](https://github.com/open-rmf/bevy_gltf_export) ·
    [docs.rs, search snippet only](https://docs.rs/bevy_gltf_export)
  - `bevy_gltf_kun` (Bevy 0.13) "adds support for glTF exporting".
    [docs.rs, search snippet only](https://docs.rs/bevy_gltf_kun)
- **Python:** `pybevy/pybevy`, "PyBevy: A Python Real-Time Engine Built on Bevy" (Apache-2.0 on GitHub;
  README badge MIT/Apache; 86 stars; pushed 2026-10-17).
  - "**Beta.** Python 3.12+. API evolving, breaking changes expected. Independently developed,
    community-maintained."
  - "A native MCP server puts coding agents on the same loop"; wheels for Linux x86_64, macOS and Windows.

  [README, repo file read](https://github.com/pybevy/pybevy)
- **The Bevy Remote Protocol** (re-check): bevy_remote 0.20.1 is "based on the JSON-RPC 2.0 protocol", over
  `RemoteHttpPlugin`. Methods include `world.query`, `world.spawn_entity`, `world.insert_components`,
  `world.mutate_components`, `world.trigger_event`, `registry.schema` and `rpc.discover`.
  [docs.rs, page read](https://docs.rs/bevy_remote/latest/bevy_remote/)
  Community MCP over BRP: natepiano/bevy_brp (79 stars, pushed 2026-10-28) and Ladvien/bevy_fairy (Apache-2.0).
  [GitHub API](https://github.com/natepiano/bevy_brp)

---

## 7 · Flax: the full EULA

Source: "Flax Engine End-User License Agreement — Last updated: October 31, 2023", 10 pages.
[flaxengine.com Flax EULA PDF, linked from flaxengine.com/licensing; page read through WebFetch's saved copy](https://flaxengine.com/wp-content/uploads/2017/11/Flax%20EULA.pdf)

- **To end users, §1(A)(a):** "You may Distribute the Licensed Technology incorporated in object code format
  only as an inseparable part of a Product … The Product may not contain any Paid Content Distributed in
  uncooked source format or any Engine Tools."
- **To other licensees, §1(A)(b):** Engine Code, modified or not, may go in source or object form "to an Engine
  Licensee who has rights under its license to the same Version". "Any public Distribution … that includes
  Engine Tools … must take place either through the Store (e.g., for distributing a Product's modding tool or
  editor to end users) or through a fork of Flax's GitHub Network (e.g., for distributing source code)."
- **Sublicensing, §1(A):** "You may not sublicense the Licensed Technology in Source Code format." Object code
  only to let end users use, or publishers distribute, a Product.
- **Release notice:** "When you generate revenue from a Product or Distribute it to end users, you must provide
  Flax with advance notification at www.flaxengine.com/release".
- **Non-compatible licences, §1(C):** GPL, LGPL (unless merely dynamically linking) and CC-BY-SA are
  prohibited; "BSD License, MIT License, Microsoft Public License, or Apache License" are allowed. "You may not
  sublicense the Licensed Technology under a Non-Compatible License."
- **Single user, §2:** "The Licensed Technology is licensed to you for use by a single User".
- **Royalty, §3:**
  - 4% of worldwide gross revenue, except "The first $250,000 in gross revenue for each Product per calendar
    quarter".
  - Also excluded: non-recoupable work-for-hire; linear media that doesn't contain or rely on the technology;
    products "only Distributed to Engine Licensees (such as through the Store)"; and others.
  - The royalty is payable "for as long as any Engine Code or Content … are protected under the copyright".
  - §4: a 10% late fee per quarter, compounding.
- **Telemetry, §7:** "as a default setting, the Engine Code will collect and send to Flax anonymous hardware
  and basic usage data from end users of Engine Tools", which can be turned off.
- **Law, §9:** Poland. **Amendments, §14:** at most once per calendar quarter, and you may stay on the earlier
  version.
- **Definitions, §16:**
  - "Engine Tools" means "(a) editors and other tools included in the Engine Code; and (b) other software that
    may be used to develop standalone products based on the Licensed Technology". There is no clause (ii) about
    folders, unlike Unreal's.
  - "Product" means anything made with the Licensed Technology "regardless of how much or little … is used".
- **Custom licences, §17:** they replace these terms for Custom Products. The custom-licensing page offers to
  reduce or remove the royalty "in favor of flat-fee, per-seat licensing", with no prices.
  [flaxengine.com/custom-licensing, page read](https://flaxengine.com/custom-licensing)
- **The 1.7 release notes** (re-check): "Removed ability to revoke or terminate the license"; amendments
  limited "to once per calendar quarter". The first 1.7 changelog entry is dated 2023-10-31.
  [docs.flaxengine.com 1.7, page read](https://docs.flaxengine.com/manual/release-notes/1_7/index.html)

**Assessment:**

- **Editor redistribution:** only to other Flax licensees, through the Flax Store or a GitHub fork, not inside
  a Product.
- **An open-source Flax-based app:** our own code can carry MIT, BSD or Apache (GPL and LGPL are banned). The
  engine part can't be sublicensed in source form, so the app as a whole cannot be released as open source.
  The shape matches Unreal's EULA.

---

## 8 · Bforartists 5.2.0: pre-release or release

- **v5.2.0 is a full release:** `prerelease=false`, published 2026-07-29, with Linux, Intel-Mac, Apple-Silicon
  Mac and Windows builds, titled "Cumulative Refinement Release".
- **v5.2.3** (2026-10-27, "Rotation and Dopesheet Gizmo Stability Release") is `prerelease=true`, with no Mac
  build.

[GitHub API releases, 2026-10-29](https://github.com/Bforartists/Bforartists/releases)

- Round one's "GitHub marks it pre-release" no longer holds; a release mirror still shows the old pre-release
  tag. [newreleases.io, search snippet only](https://newreleases.io/project/github/Bforartists/Bforartists/release/v5.2.0)

---

## 9 · Re-check of round one's snippet-only facts

| Round-one fact | Result this pass | Source and read mode |
|---|---|---|
| [U3] 5.8 moved MegaLights, Audio Insights, Live Link Hub, Iris and MRG out of Experimental | **Partly confirmed.** "Movie Render Graph is now Production-Ready", "Live Link Hub is now Production-Ready", "MegaLights has also reached Production-Ready status", "Chaos Cloth and Dataflow are now Production-Ready"; "Control Rig Physics has moved to Beta"; Mesh Terrain and MetaHuman Collections remain Experimental. Audio Insights and Iris are named only in snippets. Epic's news line "the last planned major Unreal Engine 5 release on our roadmap as we ramp up work on UE6" is snippet only | [digitalproduction, 2026-06-18, page read](https://digitalproduction.com/2026/06/18/unreal-engine-5-8-tidies-up/) · [Epic news, search snippet only](https://www.unrealengine.com/news/unreal-engine-5-8-is-now-available?lang=pt-BR) |
| [U4] 5.7: production-ready PCG, an in-editor AI assistant | **Confirmed, with a correction.** "PCG … has moved into full production-readiness"; "Substrate … is now fully production-ready"; the AI assistant is "An Experimental built-in tool"; MegaLights "has moved to Beta". The article is dated 2025-11-12 | [gamefromscratch, 2025-11-12, page read](https://gamefromscratch.com/unreal-engine-5-7-released/) |
| [U7] MetaHuman Creator's recommended spec | **Same text again, snippet only.** 16 cores, 32 GB (and "may be higher … exceeding the recommended 32GB" with large textures), RTX 3070, RX 6800 XT or M2 Ultra with 8 GB; "M1 … won't be able to render strands" | [dev.epicgames.com, search snippet only](https://dev.epicgames.com/documentation/metahuman/hardware-requirements) — page body is client-rendered |
| [U8] EULA wording | **Read at Epic's PDF and in third-party quotes** — see §1 | §1 |
| [U9] Pricing | **Confirmed at a third-party page:** $1,850 a seat; the runtime-application exclusion | [Puget Systems, 2024-03-12, page read](https://www.pugetsystems.com/blog/2024/03/12/unreal-engine-5-4-subscription-what-you-need-to-know/) |
| [U10] ARK Dev Kit, GROUND BRANCH Mod Kit | **ARK confirmed:** "a modified version of the Unreal Engine 4 editor", got through the Epic launcher Store, "around 500GB". **GROUND BRANCH:** store page 403; snippet again: "specially extended version of the Unreal Engine 4 editor", 40 GB minimum and 60 GB recommended | [ark.wiki.gg, page read](https://ark.wiki.gg/wiki/Modding) · [store.epicgames.com, search snippet only](https://store.epicgames.com/p/ground-branch-mod-kit) |
| [U11] Cine Tracer | **Confirmed:** a UE-based "cinematography simulator", $89.99, Steam only, Windows 10 and macOS 10.13+ (2019). How it ships (with or without editor) is not stated. "No updates for two years" not re-checked | [cgchannel, 2019-07-18, page read](https://www.cgchannel.com/2019/07/check-out-ue4-based-cinematography-simulator-cine-tracer) |
| [U12] Twinmotion "built on Unreal Engine technology" | **Not re-checked.** twinmotion.com 403; the Wikipedia fetch landed on the Epic Games article, which says only that Epic bought Twinmotion from Abvent in May 2019 | [Wikipedia, page read](https://en.wikipedia.org/wiki/Twinmotion) |
| [U13] Runtime Python plugin | **Confirmed:** `jokance/UnrealPython`, MIT, 13 stars, created 2026-05-20. The author's post claims UE 5.7 and 5.8, CPython 3.14.5, runtime on Win64, Android, Mac and iOS | [GitHub API](https://github.com/jokance/UnrealPython) · [forum, search snippet only](https://forums.unrealengine.com/t/open-source-unrealpython-runtime-python-integration-for-unreal-engine-5/2731632) |
| [U14] Remote Control in packaged builds | **Confirmed by a third-party README;** Epic's page snippet only | §2 |
| [U15] Screenshot Comparison tool | **Not re-checked** — dev.epicgames.com body unreadable by script | — |
| [U16] Install sizes (Arch wiki) | **Blocked:** the Arch wiki answered an Anubis bot check ("Access Denied"). Not worked around | — |
| [U17] Editor hardware: 8 GB VRAM, 32 GB RAM | **Not re-checked** — dev.epicgames.com | — |
| [F5] Flax 1.12 | **Confirmed, with a correction:** "DDGI is Production Ready"; "initial support for building games for Web" (experimental). Round one's "jiggle physics" is the "Spring Bone Physics" node ("sway, flutter, jiggle"). First 1.12 changelog entry 2026-05-19 | [docs.flaxengine.com 1.12, page read](https://docs.flaxengine.com/manual/release-notes/1_12/index.html) |
| [F6] Flax 1.7 EULA loosening | **Confirmed** — §7 | §7 |
| [F7] Flax Subsurface model; no hair model | **Confirmed:** shading models Unlit, Lit, Subsurface, Foliage, Custom Lit; Subsurface is "intended to be used by materials like skin, jade, wax or foliage"; no hair model | [docs.flaxengine.com shading models, page read](https://docs.flaxengine.com/manual/graphics/materials/shading-models/index.html) |
| [G1] Godot 4.7 stable on 2026-06-19 | **Corrected:** the GitHub release `4.7-stable` was published 2026-06-18T12:06Z. 4.6-stable on 2026-01-26; 4.7.2 on 2026-08-18 | [GitHub API](https://github.com/godotengine/godot/releases/tag/4.7-stable) |
| [G3] 4.7 features | **Confirmed:** HDR output (Windows, macOS, iOS, visionOS, Wayland), `AreaLight3D`, the Asset Store; nothing on SSS, hair or IK | [godotengine.org/releases/4.7, page read](https://godotengine.org/releases/4.7/) |
| [G9] RenderingDevice headless | **Confirmed** (Godot 4.7 docs) | §3 |
| [G11] 4.4 Metal; 4.3 D3D12 | **Metal confirmed:** "Metal support is currently limited to Apple Silicon (ARM) devices"; before, "Godot used a library called MoltenVK". That Intel Macs use MoltenVK is not stated on the page. D3D12 in 4.3 not re-checked | [godotengine.org/releases/4.4, page read](https://godotengine.org/releases/4.4/) |
| [G12] py4godot | **Confirmed:** niklas2902/py4godot, MIT, 329 stars, pushed 2026-10-29, "Python scripting for Godot. This GDExtension plugin…" | [GitHub API](https://github.com/niklas2902/py4godot) |
| [G13] Non-game Godot apps | **Confirmed and extended** — §3 | §3 |
| [O7] AtomTressFX | **Confirmed** (page read) — §6 | §6 |
| [O8] Made with O3DE | **Confirmed** (page read) — §4 | §4 |
| [O9] O3D Foundation members | **Not re-checked:** o3d.foundation/members redirects to o3df.org/members, which is 404 | — |
| [S3] Stride 4.4 and 4.3 | **4.4 confirmed and extended** (releases/4.4.0, 2026-10-09; 4.4.1 on 2026-10-17): SDSL rewritten "around a modern SPIRV-centric pipeline"; Vulkan and D3D12 overhauled ("Direct3D 12 also requires Enhanced Barriers"); a CLI; Linux and macOS builds. **4.3:** GitHub release 4.3.0.2507 published 2025-11-22 (round one's snippet said 2025-11-14) | [GitHub API](https://github.com/stride3d/stride/releases) |
| [S4] Avalonia editor "experimental prototype" | **Superseded:** 4.4 says "Game Studio is being rewritten to be cross-platform" and runs on Linux through Proton/Wine. The only Avalonia repo found is manio143/StrideComponentsEditorAvalonia (13 stars, last push 2020) | [Stride 4.4 notes, GitHub API](https://github.com/stride3d/stride/releases/tag/releases%2F4.4.0) |
| [S5] Stride skin SSS profile | **Confirmed** (API page read) — §6 | §6 |
| [B6] Bevy Remote Protocol | **Confirmed** (docs.rs page read) — §6 | §6 |
| [Y3] Fyrox OpenGL, no GI | **Confirmed** (RC post page read); a wgpu backend is now on master — §6 | §6 |
| [L4] Blender 5.0 and 5.1 dates | **Confirmed:** 2025-11-18 and 2026-03-17 (blender.org, page read) | §5 |
| [L5] Vulkan default | **Settled: 5.3** — §5 | §5 |
| [L8] Armature deform is CPU-bound; UPBGE GPU skinning | **Confirmed by the open PR** (#149020) and UPBGE 0.50 — §5 | §5 |
| [L9] EEVEE Next SSS and hair | **Confirmed:** #107407 merged 2023-06-15; #109833 merged 2023-07-14 | §5 |
| [L10] Bforartists | **Settled** — §8 | §8 |
| [P1] Panda3D 1.11 preview | **Partly:** GitHub's latest release is still v1.10.16 (2025-12-25). The NuGet preview was not re-checked | [GitHub API](https://github.com/panda3d/panda3d/releases) |

---

## Couldn't verify / open

- **The live current Unreal EULA text.** The newest Epic-hosted copy found is v2/r1, which predates update 20.
  The current wording comes only from ConductAtlas's 2026-05-05 capture, and ConductAtlas has not re-checked
  it against its 2026-10-13 capture. Three things are unverified:
  - the current Engine Tools *definition* (no ConductAtlas record);
  - the full Royalty Addendum after updates 20 and 21 (3.5% rules, Release Form, SOFR late interest);
  - Section 6(a), how seats are bought.

  Tried:
  - six searches for Epic-hosted PDFs;
  - the `link.unrealengine.com` redirect (not followed);
  - twinmotion.com, store.epicgames.com, epicgames.com/help and docs.unrealengine.com (all 403);
  - dev.epicgames.com (client-rendered; its JSON endpoint is behind a Cloudflare challenge).

  The user can download their accepted agreements from the Epic account (Account → Legal History, per Epic help
  snippet) or read `unrealengine.com/eula/unreal` in a browser.
- **The Epic Content License Agreement text:** not found as an Epic-hosted PDF. Only the Marketplace one,
  `emporium/en/v4/r1`, turned up, and it was not downloaded: it is a different document, and only the Epic
  EULA, Royalty Addendum or Content License were approved.
- **MetaHuman's own licence page:** still login-only; not tried again.
- **Unreal runtime export, unconfirmed:**
  - whether the `GLTFExporter` module works in a Shipping build (Epic's page says "runtime export … is also
    possible, but there are some limitations"; its details are in client-rendered text);
  - whether the USD exporter can run at runtime.

  Not findable without reading Engine source. I did not open Epic's source repo: it is licensed Engine Code,
  not public docs.
- **A UE5 morph-target cap and MetaHuman's LOD0 blend-shape count:** not findable. Tried three searches (UE5
  docs, `r.MorphTarget`, MetaHuman DNA).
- **The Unreal MCP plugin in packaged builds:** not stated in any readable source.
- **FSF wording read at gnu.org itself:** gnu.org answered 429 twice; the quote comes from an older mailing-list
  copy.
- **Tiny Glade's renderer API:** no developer statement found. The MoltenVK fork suggests Vulkan (an
  inference). Two searches for the 80.lv interview didn't find it.
- **Shipped Flax products:** none found. Tried the docs project lists, the forum and a Steam search.
- **Snippet-only facts still unchecked:**
  - [U12] Twinmotion — twinmotion.com refuses.
  - [U15] Unreal's screenshot test tools and [U17] its hardware page — dev.epicgames.com unreadable.
  - [U16] Arch wiki install sizes — Anubis bot check.
  - [O9] O3D Foundation members — 404.
  - [G11] Godot's D3D12 in 4.3.
  - [P1] Panda3D's NuGet preview.
  - Cine Tracer's "no updates for two years".
- **Blocked or refused this pass** (none worked around):
  - HTTP 403: `www.unrealengine.com`, `twinmotion.com`, `store.epicgames.com`, `epicgames.com/help`,
    `docs.unrealengine.com`, `developer.blender.org` (the docs source repo was used instead).
  - Cloudflare challenge: `dev.epicgames.com` JSON.
  - Anubis bot check: `wiki.archlinux.org`.
  - HTTP 429: `gnu.org`.
  - GitHub's anonymous API limit: switched to `gh api`, read-only.

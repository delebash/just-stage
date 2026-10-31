# TASKS — the live open-work tracker (just-stage)

> One entry per open item, with a pointer to its detail. **Close = delete** — git keeps history.
> Decisions are recorded as the exact text the user approved. A tracker line is a claim, not
> evidence. Facts live in [`RESEARCH.md`](RESEARCH.md).

## Research: what JustStage is built on, its features and its standards — the go [2026-10-29]

GO:     the user, verbatim (2026-10-29, the opening request): "i want to start working on a clone of reallusion
        character creator and iclone with all the plugin features built in but also with plugin cpabalilty, i know
        you can do this as i pointed out another user made clones of all dobe software. I know you can also create
        assets for this. Lets start with character create 5 latest and do some research as to what we are going to
        use to recreate this, what langauge, do we use existing software and build atop it like unreal engine,
        blender ect, what is currenetly out there that we could aldread use and enhance to be a clone or close to
        it. It doesnt have to look exactly like CC5 but it needs most or all of the features. We can think about
        the features and see if we want to improve how they work or how they are layed out or maybe even not add a
        particular feature or add new features. Can you research this but go excessive. How should we procede do
        you need to setup some type of agentic workflow would that work best like how
        https://github.com/storytold/photocraft. I want an api that user can connect to so we need to define
        standards for everything we do before we write code so things can stay consistant for cc5 and iclone and
        plugins and any other apps in this type."
        Then, verbatim, in order:
        - "i dont think we do this in family stack for performance reasons, many 3d apps use python or have python
          api or are in c++ rust can be ok but again this is part of research what langauge what is out there what
          can we reuses ect." … "this will probably be new family as i am not sure web technology stack is correcte
          for this type of app, this is part of your research"
        - "think about 3d software as character create and iclone kindof act like a game engine like unreal unity
          godot and also apps like blender"
        - "houdini cinema4d Cascadeur specialized character"
        - "none said stick with the languages i gave you it could be .net too"
        - "yes add maya and any others"
        - "we still can keep the name just prefix i think"
        - "i think integrating justdirect into this was well might be something good"
        - "but if we decide its one app then iclone makes scenes too not just actores"
        - "well i dont know if it is one app that is for your research but i lean to 1 app but easy to use almost
          like two apps but in one system so easy to distingush but this is part of research"
        - "justStage it is"
        - "you have a go on your rec" — on the recs below.
        - "also another app might be intereseting MakeHuman https://blender-addons.org/mb-lab-add-on/
          https://blendercharacterproject.org/ i am sure there are others" — added to §5's candidates.
        - "features i also want z brush ability or clone, things like making clothes metatailor marvelous
          designor, making props, the whole feature to make anything we need to create character scene animate
          pass to unreal engine like cc5 has features to push to different software z-weave, we also might want
          fx creation but this are things we can add later but we need to be able to add them in the orginal
          design cc5 has popcorn fx, but with ai we might just need character creation prop scene and camera
          managment then let ai create movie, this is just a thought we need to keep in mide, makesure all of
          this reaserch and ideas we chat about are saved" — the features in SCOPE and RESEARCH §2–§4, §7–§8;
          the AI-movie thought in IDEAS.md and §10. "z-weave" is Z-Emotion's Z-Weave (the next answer).
        - "needs to be crossplatform the additions are fine if you recommend them and have thought adverserialy
          about them, 3 it will be open source i prefer mit but if we have to use some components that are lgpl
          ect then thats ok, dont limit the license yet but it will be open source. z-weave https://z-emotion.com/
          https://z-emotion.com/z-weave snd it has cloth sim" — cross-platform and the licence in SCOPE; the
          additions below approved; Z-Weave in RESEARCH §4.

APPROVED RECS (verbatim as shown, 2026-10-29):
        - Method: "Use the deep-research skill: about 8 research agents running at once, one per area listed
          below. Each agent gets questions, not my guesses, so it doesn't just come back confirming me. I add each
          result to RESEARCH.md as soon as it arrives. I check every licence, and every claim a recommendation
          depends on, at its source myself. A Workflow would add a checking agent per area at about twice the
          cost. It needs your opt-in, and it isn't needed if I do the source checks. No parallel *coding* agents
          until the standards exist. Before that they would write inconsistent code, which is exactly what you
          want to avoid."
        - Model: "Opus 5.5 does all the research. The synthesis and the standards spec run in a fresh session on
          Fable that reads RESEARCH.md and TASKS.md. Everything else stays on Opus." And: "Keep the effort at
          xhigh."
        - References: "Maya and MotionBuilder are in. For "any others", I'm adding the direct competitors and the
          tools CC and iClone users hand their work off to: Daz Studio … MetaHuman Creator … ZBrush … Marvelous
          Designer … Substance 3D Painter … Mixamo … Each one is researched only for the parts that overlap CC5
          and iClone, so the research doesn't balloon."
        - Name: JustStage (`just-stage`) — "the Character workspace has to be the obvious first thing you see,
          and the tagline has to name both sides, for example "JustStage — characters, scenes, animation"" and
          "That makes the trademark search a must before anything goes public."
        - Folder: "E:\Dev\3D\ the 3D family's root, beside Web and Unreal; named for the field, not a stack" with
          the app repo under it, "You'd open sessions at `E:\Dev\3D`. The general memories get copied there".
        - The global CLAUDE.md edit (the three lines shown): `## Stack` → `## Stack (web family, E:\Dev\Web)`;
          `In a family app the kit and template come first` → `In a web-family app (E:\Dev\Web) the kit and
          template come first`; a new line under Stack: `- 3D family (E:\Dev\3D): its stack comes from its own
          docs once research decides; the web kit, template and /new-just-app don't apply there.`

SCOPE:  the subjects of [`RESEARCH.md`](RESEARCH.md) §2–§10 — CC5 in depth first; iClone 8 and the plugins
        (scene features included) deep enough to fix the shared standards; CC/iClone treated as an engine plus an
        editor; the routes (a game engine, Blender, our own engine, a mix) with the language chosen per layer and
        nothing ruled out; the feature references; the building blocks; the standards; the legal checks; one app or
        two (the user's lean above); JustDirect inside JustStage or beside it. Features the user named
        2026-10-29: sculpting at ZBrush's level, making clothes (Marvelous Designer, MetaTailor), making props,
        the pipeline out to Unreal Engine and other software as CC5 has, and FX (PopcornFX in iClone) — FX may
        come later, but every later feature gets its place in the first design. Cross-platform: Windows, macOS
        and Linux. Licence: open source, MIT preferred, LGPL-type components acceptable, not limited yet — the
        research shows what licence each route would need.
        Requirements added 2026-10-29 (the user, verbatim in the APPROVED entries below): characters at "the quality of
        cc5 and metahuman characters or better" — pass/fail in the rec list; "pull in assest from other programs just
        like cc5 and unreal engine and daz studio"; "the best of the best" — "meet or exceed character mesh skin eyes
        ect of cc5 and unreal" for "all of the character realism hair the whole human" ("like teeth lips"), and where
        nothing existing meets the bar (texture baking, garment cloth and the rest)
        "we need to do are own" — "if we can reuse if not build"; character assets interoperable with MetaHuman and
        CC5. Out: Omniverse, paid-only products, single-vendor core parts, Unity. In: Unreal; a Blender fork.

ADDITIONS (shown 2026-10-29, approved — "the additions are fine if you recommend them and have thought
        adverserialy about them"); each folds into an existing subject, no new agent, to keep the one round:
        - Routes (§6): platforms and graphics APIs (Windows, macOS, Linux; DirectX 12, Vulkan, Metal); editor
          UI toolkits (Qt, Dear ImGui, egui, Avalonia, WPF, Slint); more engine candidates (NVIDIA Omniverse
          Kit; Wicked Engine and The Forge as bases for our own engine); how AI agents test a 3D app (a
          headless mode, image snapshots, a control channel).
        - Building blocks (§7): a path tracer beside the real-time viewport; hair grooming tools; live mocap
          streams (Live Link, VMC, OSC; iPhone, Rokoko, Xsens, webcams); open motion and asset libraries and
          their licences (CMU mocap, AMASS, LAFAN1, Poly Haven, Mixamo's terms).
        - Feature references (§4): mocap apps (Rokoko Studio, Move.ai, DeepMotion, Plask); AI-film references
          (Autodesk Flow Studio, formerly Wonder Studio; ArtCraft); Blender's own character tools (Rigify,
          hair curves).
        - Standards (§8): the asset library (how characters, clothes, props and motions are stored, tagged and
          shared); importing existing characters from CC, Daz, MetaHuman and VRM — what's allowed and how.
        - Legal (§9): JustStage's own licence per route; whether Blender treats add-ons that use its Python API
          as GPL.

NOTES from the chat (2026-10-29): CC5 + iClone 8 + the plugins is years of work for a large team, so delivery
        is phased and tracked with a parity scorecard; the research sets the phase order. Assets are made
        through code (meshes, morph targets, rigs, shaders, materials, icons) and AI generators; a realistic base
        human with production topology and hundreds of morphs comes from an open base if one is good enough
        (§5) — never promised to match Reallusion's content library.

STATE:  setup DONE 2026-10-29 — this repo and its docs, the global CLAUDE.md edit, the general memories copied
        to the `E:\Dev\3D` project. Research DONE 2026-10-29: round one (8 agents) and the second pass (S1–S10), all
        in `docs/plans/2026-10-29-research-*.md` and distilled into RESEARCH.md. The rec list is written (NEXT).

REPO:   public at https://github.com/delebash/just-stage since 2026-10-29 — the user, verbatim: "go ahead and make repo and
        push", then "create public go" (my rec was private until the spec's LICENSE files land). It has no LICENSE
        file yet; the approved licences (R2: GPL-3.0-or-later for the extension, MIT for the libraries) land with the
        standards spec.
NEXT:   the standards spec — DRAFT WRITTEN 2026-10-29 by the Fable session (its brief:
        [`../plans/2026-10-29-standards-spec-brief.md`](../plans/2026-10-29-standards-spec-brief.md)); WAITING on the
        user's approval, which goes here verbatim before any code:
        - the spec: [`../standards/README.md`](../standards/README.md) (index, the NOT STANDARD list N1–N5, the 3D
          family's "one way per job" table, the repo layout) and its twelve documents; the synthesis:
          [`PRD.md`](PRD.md), [`ARCHITECTURE.md`](ARCHITECTURE.md); evidence fetched while writing:
          [`../plans/2026-10-29-spec-evidence/`](../plans/2026-10-29-spec-evidence/README.md) (RESEARCH §6, §8, §10).
        - open for the user's word, by name: N1 the character JSON schema (+ its USD applied-schema mirror); N2 hm08
          without MakeHuman's helper geometry; N3 HD morphs as displacement deltas; N4 the face control vocabulary
          (ARKit 52 + ours); N5 the body correctives schema; the kit gap — a generic image-job route in `just-core`
          (`POST /v1/ai/image/jobs`), filled in a just-core session before step 2; the API port 17480; the MetaHuman
          terms reading (the recs' "not recs" item) for "Send to Unreal as a MetaHuman" and DNA import.
        - gate measurements the spec names for step 1: VRAM of one skin job beside the EEVEE viewport; the shape-space
          wrap errors. (The UE5 Mannequin bone list was read from the user's UE 5.7 project the same day — RESEARCH §8.)
        - the user's answers 2026-10-29, verbatim: "4 fine that seems at least based on well known standard" → **N4
          APPROVED**; "5 ok" → **N5 APPROVED**; "6 core already has open session which it is working" → the kit gap is
          the open just-core session's; "7 ok" → **port 17480 APPROVED**; "8 any again dont wory we do whatever to make
          it owrk not worry about license" → the MetaHuman terms item is DROPPED: "Send to Unreal as a MetaHuman" and
          DNA import ship enabled, terms shown as a label; and "i told you never give me a rec or list you havent
          verrified like the exact ue5 manaquin stop doing that always do complete job" (memory updated). Questions 1
          ("so how do we get character in other apps if we use our own custom json instead of usd or aousd?…"),
          2 ("are you making some non standard skeleton?") and 3 (N3, "i dont even understnad what this means") answered
          in chat with revised recs; N1, N2, N3 still open.
        - Then, verbatim (2026-10-29): "so why after adversirally researching and thinking did you recommend json, i
          dont trust you lazy logic"; "then rethink all your recs and make sure you have the correct one, do it
          adversarilly, check you work and recs"; "so do i trust all the docs you have written to be correct i bet the
          answer is no"; "it is a rule do standard unless there is no better alternative, stop breaking rule" → the
          **standard-first pass** over every piece of the spec, same day: eleven changes, listed in
          [`../standards/README.md`](../standards/README.md) §6 (USD applied schemas through Blender's USD hook API
          instead of a JSON companion; primvars, GeomSubsets, relationships, assetInfo; the UE5 skeleton's names
          verbatim; one extension with modules instead of inter-dependent extensions and a custom manifest table; MCP
          as the only remote protocol; pytest as the only runner; the 8 GB texture budget; the `cc5` preset fixed; one
          map per HD morph; every "verify later" item verified at the source or on this machine — RESEARCH §1, §6, §8).
          Still open for the user's word, by name: **N1** (the fields of the USD schemas), **N2** (hm08 without
          helpers), **N3** (HD morphs as displacement blends). N4, N5 and the port stand approved.
        - Then, verbatim (2026-10-29, after switching the session to Opus 5.5): "fable messed up on the standards by
          trying to roll its on json file for characters and a bunch of other non standard hand rolled stuff when
          openusd handled it, i dont trust fables synthesis so can you revoiew all of fables work" → the review is
          [`../plans/2026-10-29-spec-review-opus.md`](../plans/2026-10-29-spec-review-opus.md): 20 findings with recs,
          WAITING on the user's word; the spec is unchanged until then. Two approvals rest on premises the review shows
          false — **N5** (DNA's RBF and twist-swing layers already carry body correctives) and **N4**'s reason for our own
          control names (MetaHuman's control names are in the user's UE 5.8 DNA files); they stand until the user says
          otherwise. Three approved recs would change: **R17** (FBX out through Blender's exporter), **R19** (Blender
          Lab's server speaks MCP 2025-11-25, not 2026-07-28), and the Blender floor of **R1** (kept at 5.2 LTS). The
          user, mid-review: "blender 5.3 beta is installed but dont run just now anothe session is using memory
          E:\blender-5.3.0-beta" and "unreal 5.8 is on f drive under epic" (RESEARCH §1 corrected).
        - Then, verbatim (2026-10-29), in order: "1 i dont understand does this mean we are using unreal keep
          explantiatons simple as what we are doing or what you are sugesting rethink on all your recs again just to
          make sure you dont change your mind"; "like what is MPFB2 you have to explain in simple short terms what each
          is for and why we are using and if it is standard"; "what does omniverse use it seems it has a lot of oepn
          standars whatr do it use for materials and hair and other things"; "is there another better body we can use,
          can we make one, can we use cc5 or is ther eanother blender body pluginkl i feel you ddint reasearch well";
          "one addition we need to create non human body as well like creatures just like cc5 allows and i think
          another app i listed as example, is that include in specs"; "if makehuman doesne work could you Custom /
          Clean Quad Base Mesh: Sculpt or commission a clean, neutral androgynous base mesh with standard quad topology
          (often inspired by Blender/ZBrush anatomy standards) and write your own blendshapes or skeletal deformation.
          maybe there are free ones on the web, i dont know but i want standard if we can so we can share with other 3d
          engines blender autodesk ect"; "these things might be good to look at CharMorph for code features or how to
          do something just to n0ote"; "you are using google for head but it doesnt have eyes mouth how are you fixing
          that"; "ok think on your recs again and give me a list of what you are doing, explain simply what each is for
          and why so try not to use just acronyms"; "finish what you are doing before you give me recs again" → the
          second pass over the review's recs is in the review file ("Second pass over these recs"): 7, 11, 13 and 19
          changed; three items added — 21 N3 (missed by the first pass), 22 creatures (a new requirement: making
          non-human characters, not only importing them; changes R21's order), 23 the fallback body. Facts in
          RESEARCH §5 and §8. WAITING on the user's word, item by item; the spec is unchanged until then.
        - Then, verbatim: "did you look at https://humgen3d.com/" (read; RESEARCH §5 — stays out as paid, its assets
          can't be shared); "i want our app to look like a custom app so user donest have to load plugin it just
          laucnhe like an app we built even thought it is using blender core features", with a pasted text on Blender
          as a Python module, application templates and stripping the UI → review item 24 (shipping as its own app),
          WAITING on the user's word.
        - Then, verbatim: "since you change your rec should you rethink again?" → the third pass (review file, "Third
          pass"): 7 refined (commands registered at runtime so plugins reach assistants); 21, 22, 24 extended; a fourth
          angle found nothing more. The complete list, 1–25, WAITS on the user's word, item by item.
        - Then, verbatim: "we are definitly adding lots of good ai features to this app like cc5 and we will come of with
          more"; "well we dont have to do it now but i want user to be able to descibe a person and the app creates
          that person mesh, or creates stuff like that that" → review item 25 (one way to add AI features) and an
          IDEAS.md entry (describe a person, get the character — not scheduled).
        - Then, verbatim: "we want features like unreal has where you can do mocap face with iphone and other motion
          capture stuff unreal just added new motion caputre stuff in the last few releases" → review item 26 (motion
          capture: in Unreal now per R13; live capture doors inside JustStage with the Animate workspace). The
          complete list, 1–27, WAITS on the user's word, item by item.
        - Then, verbatim: "just to check our app will have main app with plugins that add features like headshot and
          skingen or is this just built into the app, i like the modular design idea, what do you think?" → review
          item 27; "1 you say game enine cant carry so they are baked is this how cc5 works?" → item 1's wording
          corrected (review file).
        - Then, verbatim: "why not build on better blender? tjhat is waht i downloaded for you to test on, it will probe
          be production soon"; "why do you think i donwloaded beta for you to use, i did not do it for my health you
          made bad decisiion again" → review item 16 REVERSED: build and test on Blender 5.3 (beta now, final
          2026-11-04), move with each new release; R1's floor "5.2 LTS onward" → "5.3 onward", on the user's word.
          Still in force: "dont run just now anothe session is using memory" — Blender is run only once the user says
          the memory is free.
        - Then, verbatim: "serioulsy how did you get blender version wrong 18 says blend installed the only version
          installed is beta and yet you built your recs on non installed version, uggh you need to think before you
          act!!!!!"; "think on recs again and give me list, uggh!!!!" → every Blender fact re-checked on the installed
          5.3 (review file, "Re-check on the installed Blender 5.3"); the complete list, 1–27, shown in chat, WAITING on
          the user's word item by item.
        - Then, verbatim: "so are we mainluy testing quality first bedofre we add things like wrinkels, hair mustache
          makeup all the cool stuff cc5 has? i agree with your recs" → **the review's recs 1–27 APPROVED 2026-10-29**
          (the review file, its second and third passes and the 5.3 re-check), including the approved-rec changes
          they carry: R1's floor → Blender 5.3 onward (item 16), R17 (FBX out through Blender's exporter; correctives
          in the DNA, no own JSON schema — items 1, 13), R19 (MCP 2025-11-25 through Blender Lab's server — item 8),
          R21 (creatures in step 4 — item 22); N2 withdrawn (item 2); N5 replaced by the DNA body layers (item 1).
          Still waiting, because the user's rule says a blanket go never covers a NOT STANDARD piece and an outward
          step needs its own word: the word **go** for rewriting the spec; by name — **N1** (the names of about ten
          `juststage:` attributes, item 6), **N3** (the slider-driven fade of the HD detail maps, item 21), **the
          command registrar** (our own small module that registers every command from its `Params`, item 7), **item
          10** (MetaHuman's control names — an exception to AGENTS.md's clean-room rule); **item 15** (sending the
          image-job route request to the just-core session).
        - Then, verbatim: "your rec on all 1-6 as long as you think on it again and make sure you dont change your mind
          go" → **GO 2026-10-29** on the six: (1) rewrite the spec to the 27 approved items; (2) **N1 APPROVED** — about
          ten `juststage:` attributes; (3) **N3 APPROVED** — the slider-driven fade of HD detail maps; (4) **the command
          registrar APPROVED** (NOT STANDARD, our own small module); (5) **item 10 APPROVED** — MetaHuman's control,
          face-joint and part names on our face rig, names only, an exception to AGENTS.md's clean-room rule; (6)
          **item 15 APPROVED** — the image-job route request goes to the just-core session. The final re-check before
          acting (review file, "Final check before the rewrite") changed no rec.
        - DONE 2026-10-29: (6) the image-job route request was sent to the `core` session (just-core's own item; the
          route's shape is theirs); (1) the spec is rewritten — `docs/standards/` (all twelve documents and the index),
          `PRD.md` (§2 and §7 still DRAFT for the user's answers, item 19) and `ARCHITECTURE.md` — to the review's items
          1–28. While rewriting, item 9's CC column was corrected again (by humanoid role: `Waist`/`Spine01`/`Spine02` →
          `spine_01`/`spine_03`/`spine_05`; the review had read Reallusion's UE4 table — RESEARCH §8).
        - Then, verbatim: "did you look at apps like meshy https://www.meshy.ai/features/ai-animation-generator could
          that be useful https://mesh2motion.org/ https://www.mixamo.com/#/"; "Bonus Alternative: If you only want a
          static mesh to sculpt on without procedural sliders, use the Blender Studio Asset Bundle. Its topology is
          hand-crafted by professional animation artists specifically for film and game production pipeline"; "you
          have go on adding those things" → **item 28 APPROVED and written into the spec**: Mesh2Motion's CC0 creature
          rigs and animations, its human animations retargeted, Blender Studio's CC0 base meshes as sculpting starting
          points — all in the starter library.
        - The kit gap is FILLED: the `core` session shipped the image-job route on just-core's main (`333ac9e3`,
          2026-10-29 — `makeImageJobsRouter`, `POST /v1/ai/image/jobs`, the result fetched once as PNG); checked in the
          kit's code and written into `ai-engines.md` §2–§3 and RESEARCH §10. PNG only: float channels are converted
          to EXR inside Blender.
        - Then, verbatim: "1 as with all my apps they are for anyone to use open source on any computer crossplatform
          and any grpahics 2 what do you think?" → PRD §2 written from answer 1 (anyone, open source, every OS, every
          graphics vendor); for 2 (what the first release holds) my rec was shown in chat, WAITING on the user's word:
          R21's steps 1–6 — the passed gate; body, head and face, skin with makeup layers, eyes, hair with beards;
          photo-to-head and photo-to-body; rig and expressions with creatures; clothes fitting; import and export with
          the full Unreal plugin (mocap in Unreal with it); the installer on Windows, macOS and Linux; the Plugins page;
          the API with its tests; user docs. After it: sculpt extras (7), clothes from patterns (8), then Animate with
          JustStage's own live capture, Scene, FX and describe-a-person.
        - Then, verbatim (2026-10-29): "i agree go code it, unless you really need my input just think adversrially on
          your decisions and take your own recs once you adversarialy thoughts finish, go" → **PRD §7 APPROVED** (steps
          1–6 as the first release) and **GO ON CODE**: R21 step 1 (the quality gate with a first Unreal plugin) starts,
          on the approved spec; every choice the spec leaves open is decided here after an adversarial pass, written
          down with its reason, and built — the user is asked only where their input is really needed. Blender: the
          GPU had 928 MiB of 8 GiB in use and 18 GiB of RAM free when the work began; headless runs only, GPU-heavy
          renders re-check first.

STEP 1 — the quality gate (R3), the plan (each line closes when its test passes; the order is the build order):
        1. DONE 2026-10-29 (`a540fe7`): the foundation — add-on, core API, command declaration with its operator mirror
           and match test, the dev run on JustStage's own folders (`tools/dev.py`), pytest on CPython and in Blender.
        2. DONE 2026-10-29: the base — MakeHuman's CC0 data fetched and checked at MPFB2 `6ff1eb35`
           (`tools/fetch_data.py`); `juststage.body.create` builds a human on the whole hm08 (helpers and joint cubes
           kept, masked), MPFB2's vertex groups, MakeHuman's macro blending ported from MPFB2 with its shape-key names;
           joint cubes move with the body. Next in this line: the detail sliders of `target.json` (step 2 proper).
        3. DONE 2026-10-29: levels 1–2 — `juststage.body.subdivide` puts Blender's Multires (Catmull-Clark) first in the
           stack, before the helper mask; level 2 shows 214,048 faces (the body's 13,378 × 16). Displacement maps come
           with the skin generator (4).
        3b. DONE 2026-10-29: `libs/wrap/gnm_to_hm08.py` (MIT) reads GNM v3.0's model file as plain arrays (SHA-256
           checked; no GNM code runs — installing GNM's package from GitHub was refused by the permission check, so its
           data is used directly), fits its skin onto hm08's head (eyes for the start, trimesh's Amberg NICP; fit error
           mean 0.87 mm, p95 2.17 mm) and writes 170 MakeHuman targets with a neck fade and a fade where hm08 reaches
           past GNM's skin (crown, shoulder tops); `juststage.head.set_identity` puts a GNM identity (coefficients or a
           seeded normal draw) on a character as one shape key. The launch path was fixed on the way: the template now
           sits in JustStage's own user folder and switches the add-on on through Blender's load handlers
           (`BLENDER_SYSTEM_SCRIPTS` broke `bl_pkg` on 5.3 — measured).
           Was: decided 2026-10-29 (adversarial pass): the gate head carries Google's GNM scan-based head shape wrapped onto
           hm08 (R4: "realism comes from MHR's and GNM's scan spaces"), so the gate judges the approach R4 chose rather
           than hm08's artist-made face alone — the attack (more work before the first render) loses to a gate round
           wasted on a face R4 already said would read stylised. Wrap: offline non-rigid registration (trimesh's
           Amberg optimal-step NICP, MIT) in the MIT `libs/`, the result shipped as MakeHuman targets (`gnm` space).
        4. The engine host from the kit's template with `sdcpp`, and the skin generator's first image features.
           BLOCKED 2026-10-29 on kit work (another repo — the user's word): the kit's template runs no image
           engine (`template/server/src/app.js`: `runtimes: []`, `runtimeModels: []`, no image feature in its catalog —
           "The template runs no image model"), so ai-engines.md §2's stand-in ("the kit's own template server … with
           `sdcpp` on") can't run unchanged; and `scripts/new-app.js` makes only a whole app (Quasar, Electron and
           server), no server-only package, registering its ports in `check-family.js` (`APPS`, `APP_PORTS`). The
           card is free since 2026-10-29 (JustVoice: "card free").
           The user, 2026-10-29, verbatim: "i dont care about two apps managinemment memory that is uyser
           responsibliyt, you are overthinking and complicating things" — no cross-app memory rules (ai-engines.md §4
           rule 3 dropped). And on reuse: "we do what full ai in just stage so yeah reusing the kit is good idea its just
           sucjs we have to have node installed now" — Node ships inside JustStage's installer (plugins.md §5).
           The user, 2026-10-29, verbatim, on that parking: "no i did not mean waits you need it i just mean doing
           full jv you still need image for character creator test that is what got us donw this path"; then "i dont
           care if you use the new-app.js or if you need to adjust its code, you are overthinking just manually copy
           the stuff if need be insead of new app"; "ok so we do need a new server for this app just like we have for
           jw and jv and we just copy the files" → "go"; "ok go your rec all go"; and "i my change this later and make
           it all inside blender as it just seems not seemles this way, but for now why we are still testing if it
           even works well enough this is fine".
           The user, 2026-10-29, verbatim, on the copy: "why it in folde named host will all other apps haver server
           ffolder this was the point of the tmeplate consistancy and you are already breaking it"; "you didnt run the
           new-app; but you where still should follow poarts of templat that relate what you need"; "the tempalte is so
           we have consistency, this app is differnt but still there still should be rules and consistency you follow
           with server design location ect, that is point of tmeplate"; "you can adjust as needed you are smart this is
           you job to figure out what to use and not use". So: `server/`, the generator's names for JustStage
           (`just-stage-server`, `JUST_STAGE_*`, product `JustStage`, version 0.1.0 with the app), the template's server
           tests (48, moved off its Notes demo onto the settings), its `biome.json`, the root workspace and scripts.
           DONE 2026-10-29 (images): JustStage's server is `server/` (every family app's server folder) — the kit template's server copied by hand (its Notes
           demo out), port 17481, the image engine on with just-house-paint's FLUX.2 klein 4B row (the family cache
           shares the engine and the 8.7 GB model already on this machine). `juststage.engines` starts it when it
           isn't running and runs image jobs over the kit's routes; `juststage.skin.add_detail` asks its
           `juststage.skin_detail` feature for a skin close-up, keeps its fine relief as a seamless height map
           (`core/skin_detail.py`), packs it with its provenance and tiles it over the body's UVs as a bump on the
           skin material — tested against the real server (10 s a picture on the 2070 Super, the card's peak 6,060
           MiB). A kit bug found on the way — the route's `seed` never reached sd.cpp, every picture was seed 42 —
           reported and fixed by the core session (just-core `b41154a7`). DONE 2026-10-29: the AI panel (3D view sidebar,
           JustStage tab) — the server running or not with Start, an AI settings link, each feature with its model,
           the running jobs with progress and Cancel; an AI command has two halves (`start` submits, `finish` applies)
           so a button never freezes Blender — a `bpy.app.timers` follower runs between them; `main` still waits for
           scripts. Two kit bugs found and reported to the core session (2026-10-29): a Cancel sent the moment a job
           starts (right after another ends) is lost — `runner/sdcpp.js` `runNativeJob` listens for the abort only
           after its submit — and a second job while one runs failed at once ("The graphics card is busy …", 409)
           instead of queueing — both fixed by the core session (just-core `04e81a12`); the 12 AI tests pass. The
           user, 2026-10-29: "lets just do the basics of what we need for ai so we can just test what we need nad see
           if the app concept works we are spending to much time trying to build ai even before we know if 3d stuff
           works" — AI stops at these basics. Deferred in 4 (my call, 2026-10-29): the kit's AI pages on the server
           (the template's web front end — 42 files and Quasar's build) wait until there is a second model or engine
           to choose between; the engine and FLUX.2 klein are installed already and the panel shows the model, so the
           AI settings link is hidden until the pages exist. Speech waits for JustVoice's move into the kit.
        THE FACE TEST (the user's go 2026-10-29, "your rec go", on: "stop adding parts and do one realism test on the
           face first" — paint-and-project skin, the cheap fixes, then renders beside MetaHuman and CC5 for the user's
           verdict). The user's words on the way: "do you think we will get realism if not there is no point in this
           … even if we have to make everyhting ourselves"; "how does cc5 and metahuman do it we are supposed to do it
           professional and tye same way"; "can we do cc5 more detailed base and with ai gen we should be ahle to gen
           high quality images like what cc5 uses, correct?" → "your rec go".
           FIRST RESULT 2026-10-29 (`tools/face_test/`): seven clay views of the bare head (Cycles, even white world
           light), each repainted as a photograph by FLUX.2 klein on JustStage's server (`juststage.face_paint`, the
           view as init AND reference — house-paint's way; init alone was ignored), projected back onto the 4096² UV
           (`core/uv_projection.py`) as the ratio painted/clay — so the clay's light cancels and the calibrated skin
           colour stays on average — blended by facing, depth-tested, faded toward each picture's frame and where
           views barely reach. The face gains real skin: freckles, redness, eyelid creases, nasolabial folds, lip
           colour (renders `.dev/facetest/render_*_painted.png` beside `_plain`). Open: the painted brows double the
           strand brows; a soft band on the shoulders; resolution soft; no specular/roughness map yet; the eye shells;
           studio HDRI lighting (Poly Haven, CC0); the MetaHuman and CC5 references for the side-by-side.
           ROUND 2 2026-10-29 (the user: "keep going if you think you can get the model to look real"; "it has to be
           as good as the real photo or there is no point in this project"): three close face views, a bump map and a
           shine map from the painted skin, Poly Haven's CC0 "Studio Small 09" HDRI, each render beside the AI photo
           from its camera (`.dev/facetest/compare_*.png`). WORSE than round 1: the AI moves the face a little when it
           paints (its eyes lower, its mouth shifted), so projected eyelids and irises land below the 3D eyeballs
           (doubled eyes) and the lips misregister; the close views' edge shows as a ring on the forehead (their
           weight ×(0.78/d)⁴ too strong); the calibrated skin colour renders darker and browner than the AI's skin.
           Next: align each painted view to its clay view by facial landmarks before projecting (warp the painting
           so its eyes, nose, mouth and jaw sit on the mesh's), softer close-view weights, and the skin tone taken
           from the AI's painting.
           ROUND 3 2026-10-29 — the projection works: `tools/face_test/align_paintings.py` (MediaPipe Face
           Landmarker, Apache-2.0, in `.dev/venv-tools`; a thin-plate-spline warp) measured the AI's drift — 5–15 px
           on the head views, ~40 px (worst 182) on the close face views — and warps each painting back to 4–11 px
           (the detector's own noise ~4 px); each texel takes mostly its one best view (facing weight cos¹⁶ — blending
           many views smeared the detail flat); only the detail travels (each view's ratio around 1) and the tone
           stays the calibrated skin model's (paler: melanin 0.012, blood 0.022) — keeping the AI's tone clipped the
           ratio flat, and as a hue it came out grey (the AI's pictures and our renders differ in colour handling).
           Result (`.dev/facetest/compare_face.png`, `compare_left40.png`): the 3D head carries the photo's freckles,
           pores, wrinkles and folds, no doubled eyes. Still short of the photo: darker, contrastier light (the
           photo is high-key), a different face shape (our GNM head), dark eyes without wetness or shells, the lips'
           lower edge misregistered, a light band at the temple where views change.
           ROUNDS 4–5 2026-10-29/30: exposure, background and skin tone calibrated against the photo; a two-band seam
           blend; the photo's light fitted (a 1.6 m soft light, far left, face height); painted broad shading divided
           out (the user: "the neck is wrong it looks like the adams apple is indented … stuff like that" — a painted
           shadow read as a dent). Closer in light and tone; the photo's skin texture stronger; the face a different
           person. A landmark shape fit (`test_face_fit.py`: GNM identity by Gauss-Newton on MediaPipe's points) FAILED
           — 16.1 → 14.3 px while bending the identity 19.5 sd — not used. Then the user: "did you search for latest
           techniques for all of our app functions?" — no, not for texturing a given mesh; the research is RESEARCH §10
           *web, 2026-10-30*, and continues.
           RESEARCH DONE 2026-10-30: five areas (`docs/plans/2026-10-30-research-*.md`, every search logged), key
           facts re-checked by API and licence files; the rec list is `docs/plans/2026-10-30-realism-recs.md` —
           SHOWN to the user, waiting for their word. Nothing built meanwhile.
           APPROVED 2026-10-30 — the user, verbatim: "3 clean room means we build it ourselves but using textures files
           from reallusion as long as they are free and open source that is ok, our app is going to be different
           enough from cc5 anyway so if you think they are useful you can use them, your rec on the rest go". So recs
           1–8 and decisions 1, 2, 4 as recommended; decision 3: Reallusion's texture files may be used where they are
           free and open source (their own terms read first — CC Blender Tools' code is GPL-3, the textures inside may
           carry Reallusion's). First step: measure the refcontrol LoRA on our engine, then RealDenseFace's memory.
           STEP 1, THE PAINTER MEASURED 2026-10-30 (`docs/plans/2026-10-30-research-image-models.md`): the refcontrol
           LoRA gives a small gain — the painted face points 11.3 px from our head's on left40 against 14.5 without it,
           12.7 on klein base (468 s). The user then asked, verbatim: "dont we use flux.3 is there an updated version?",
           "does flux 3 not do this already?", "what about krea 2 and krea 2 turbo", "user do report flux 3 may acutall
           not be as good as flux2", and: "your rec go only test flux 3 and krea 2 if you think it is worth it". FLUX 3
           Image Klein (already on this PC) painting from the clay view alone: 6.2 px on left40 (seed 2: 7.2), 12.7 and
           7.9 px on the close face views where FLUX.2 klein drifts 39 and 44 px; photoreal; ~99 s a view, card peak
           7,165 MiB. Krea 2 not tested (text-to-image only, not on this PC; FLUX 3 already near the detector's ~4 px).
           MY CALL (under that go): rec 1 paints each view with FLUX 3 Image Klein from the clay view; one face across
           views from painting each next view on a render of the paint already projected (rec 1's second half). The
           refcontrol LoRA and the kit LoRA request are dropped. FLUX.2 klein 4B stays beside it as a choice, each
           model labelled (FLUX 3: FLUX Kommunity License, gated at BFL, free under US$5M revenue — secondary source).
           RealDenseFace measured 2026-10-30 (RESEARCH §10): its network takes 1.1 GB (ViT-B, 0.1 s a picture) or 0.5 GB
           (ViT-S) on the card — fits beside anything. STEP 1 DONE. Rec 4 needs the FLAME 2023 Open file, whose download
           needs a sign-in at flame.is.tue.mpg.de — the user's account.
           ROUNDS 6–7 2026-10-30: all ten views painted by FLUX 3 Image Klein (`sd-cli`, seed 1, the clay view as its one
           reference); the landmark warp took them from 5.6–12.7 px to 3.7–9.3 px. Round 6's tone fit hit the darkest
           corner of its grid (melanin 0.022, blood 0.034 — FLUX 3's photo is warmer than any tone our skin model makes,
           and the chin patch is stubbly), so round 7 fixes round 3's tone (`FACETEST_TONE=0.012,0.022`). Result
           (`.dev/facetest/compare7_*.png`): the features land on the mesh (no doubled eyes or lips) and the tone is
           close, but it is still another person and still reads as CG — the photo's eye bags, brow ridge and lips are
           shape our head doesn't have (rec 4), the skin detail is weaker after projection, the AI's shaved-stubble patch
           on the back of the scalp carried onto the head (next prompt: completely bald, no stubble), and the mouth is
           open showing teeth. Round 5's pictures kept in `.dev/facetest/round5/`. Next: rec 1's second half — each next
           view painted on a render of the paint already projected, for one person across views.
           Then the user, verbatim: "keep going until you get a photo realistic version, if cc5 can do it and metahuman
           can do it you can, so keep testing keep researching you have permision to do whatever research you need but i
           need photo realism, can you keep going without stoping unitl you figure out how to get it to photo reaslism?";
           "dont worry about rules you can run or do whatever you want" (auto mode still blocks some downloaded code —
           not worked around); on pores: "so we test all approaches and can do this too to find what works best for our
           setup". JustDirect goes on in its own session (the user's main goal is movies); the card is shared by message.
           ROUNDS 8–11 2026-10-30 — the scan studios' way (shape to a normal map, light-free colour to the albedo):
           repainted with "completely bald … mouth closed" (FLUX 3 still paints a shaved-stubble cap on the back of the
           scalp); Sapiens2 normals per view (`view_normals.py`), only their detail under 15 mm kept over our mesh's
           shape; each painting's light fitted as an even part plus one soft direction and divided out with our mesh's
           occlusion (`delight_views.py`); full albedo and relief projected two-band, each view's brightness levelled
           by a global gain; an object-space normal map; lashes as strands (the brow groom was huge and doubled the
           painted brows — removed); the lips closed by a shape key; iris and sclera projected onto the eyeballs; the
           render in Standard view; calibration from linear EXR renders (8-bit renders clipped red and ran the colour
           away — round 9); the light fit chooses the fill too (the photo is lit evenly: fill 1.0, a 3 m key). Round 11
           (`.dev/facetest/compare11fixed_face.png` — the 16-bit PNG trap: Blender reads 16-bit PNGs as linear, so
           `compare10/11_*` show the render too dark): tone, light and background match the photo; eye bags, smile
           lines and forehead creases are relief; the skin carries the photo's colour variation. Still CG: grey, milky
           irises without the dark limbal ring or wet look; brows and pores washed faint by blending misaligned views;
           one flat skin roughness, no sheen; a thin gap between the lips.
           ROUNDS 12–18 2026-10-30 (`.dev/facetest/compare18fixed_*.png`, `eyes18.png`; each round saves its scene as
           `.dev/facetest/round.blend` for quick shading trials, ~25 s a render): the fine band from each texel's single
           best view (blending misaligned views had washed brows and pores out); a cavity map taking shine out of pores,
           Coat as the oil lobe (0.12, roughness 0.3), Sheen 0.1 (research rec 5); the irises unwrapped from the close
           painting by MediaPipe's iris points onto the eye's polar UVs (the painting shows a ±30° band between the lids;
           sampled inside 0.88 of MediaPipe's radius, a dark limbal ring added); the white only from pale texels; the
           upper lids turned down 9° about each eyeball (the neutral head stared); the cornea clear (a refracting or a
           Fresnel shell greyed the eye — trials 2026-10-30); a contact shadow in the eye map; the skin's colour gain on
           the eyes. Skin, tone and light are close to the photo; the eyes still read as CG — the white too clean, no
           tearline or caruncle, the lid rim visible — and a pale streak on the neck where coverage ends, red patches in
           the ears. Next: rec 6's eye parts (occlusion shell, tearline, caruncle; the iris at its depth), then the
           neck and ear artefacts, then the pore approaches the user asked for side by side ("so we test all approaches
           and can do this too to find what works best for our setup": from the paintings, a scanned micro-normal tile,
           procedural, SeedVR2-upscaled paintings).
           ROUNDS 19–26 2026-10-30 (`.dev/facetest/compare26fixed_*.png`, `eyes26_left40.png`). The user, verbatim:
           "so you are still hving problems i cant beleive it is this hard i am sure others already do it, did you
           research thoroughly the newest best techniques and check how the code it and check confyui … but keep going".
           My answer: the skin follows the pros' method and works; on the eyes I had been hand-tuning our own shading
           instead of using the proven open eye setups the research listed — corrected: MPFB2's procedural eye
           ("EnhancedEye", `data/node_trees/procedural_eyes.json` at 6ff1eb35, CC0 data) built by our loader
           (`tools/face_test/mpfb_nodes.py`) onto our eye's polar UVs (one eye per map, eyeball UV radius 0.46, iris 0.40
           of it; their two-eye distance node had to have its second centre moved off the map), iris colours from the
           painting; both lids brought to the iris per 10° slice (upper 11°, lower 5°); the lid underside that faces the
           eye takes the rim's colour (the paintings put eye colours there — the "shiny strip"); the cornea clear with
           half a Fresnel reflection; a weak catch light by the camera; the occlusion shell tried and set aside (its
           shading blotched). Trials on `.dev/facetest/round.blend` (~25 s a render) found each cause. Still open: the
           eyes dry (no strong catch-light) and lashless (the lash groom hangs across the eye — needs curl), the neck
           streak behind the jaw, red ear cavities, the lips' contact line, the scalp's painted stubble.
           Card: handed to the JustDirect session ("card free", 2026-10-30) — no GPU work here until it hands back.
           ROUNDS 27–31 2026-10-30 (the card shared with the JustDirect session by message, "card free" both ways):
           MakeHuman's CC0 lash cards fitted by MHCLO (`eyelashes01`; the groom's strands had hung across the eye) — real
           lashes on the lids, still long and full for this man; pores compared on one cheek (`.dev/facetest/
           pores_compare.png`: the paintings' own, the Lee Perry-Smith scan tile at its measured size, both) — alike at
           this distance, both richest, kept as default; the photo's pores catch highlights ours don't (shine, next);
           MakeHuman's photographic CC0 eye texture baked onto our eyes — rejected (its brown reads red-orange when lit);
           MPFB2's procedural eye kept. Next: the lids shaped from the painting — MediaPipe's 16 lid-contour points per
           eye in the painting against the clay, each lid slice turned until our edge lands on the painted one (the eyes
           still stare); the lashes shortened; skin shine; the neck streak; the ears.
           ROUNDS 32-34 2026-10-30: measured (MediaPipe on the face view) that the rendered eye already matches the
           painting's shape - opening 7.7-7.9 mm vs 7.8-8.2, iris centre 0.46-0.47 vs 0.44-0.45 of the opening, the
           upper lid over 1.8-2.1 mm of iris vs 1.9-2.2 - so the stare was shading: the eye calibrated like the skin
           (linear colour at MediaPipe's iris and lid points, painting vs render): iris x (1.0, 0.78, 0.82), the white
           beside the iris x (1.89, 1.56, 1.41) - EyeWhiteColor (0.94, 0.70, 0.59) (sampling toward the corners caught
           pink tissue and overshot - round 32); relief from the paintings kept up to 25 mm (15 lost the eye bags);
           MakeHuman's CC0 brow cards (`eyebrow001`) by MHCLO; the lash cards at 60% length (tips pulled toward the lid).
           Round 34 (`.dev/facetest/compare34fixed_*.png`): eyes read as eyes, defined brows. Still: the lips fuller than
           the painting's with a contact line, a slight stare, the ears, the neck streak, no wet catch-light, the skin's
           shine. Pore approaches compared (rounds 27-29): alike at portrait distance.
           ROUNDS 35-36 2026-10-30: the catch light bright and small (0.12 m, 15 W), seen by glossy rays only and linked
           to the eyes alone (Blender's light linking - at 40 W on everything it turned the skin and lips oily, round 35);
           the lips closed with 0.4 mm overlap and 12% thinner in height. Next: the iris bump down (it glittered), the
           lips' contact line, the ears, the neck streak.
           ROUND 37 2026-10-30: the lips' inner surfaces take the lips' own colour, darker (the contact line); the light
           removal's occlusion floor 0.5 (0.2 boosted the ears' hollows 5x). Still: the iris grey-blue from the side (the
           cornea's grazing reflection of the grey studio), the brow cards too heavy and arched (`eyebrow001` - try a
           sparser set or lower opacity), the ears' hollows still red, the neck streak behind the jaw.
           ROUNDS 38-39 2026-10-30: brows `eyebrow012` (straight, sparse), mid-brown; MPFB2's eye keeps its outer layer
           (alpha 0 turned the eye black - round 38) at IOR 1.15 (a fifth of the shine; 1.33 mirrored the grey studio from
           the side); our cornea's reflection at 0.3 of Fresnel. Round 39 (`compare39fixed_*.png`): eyes brown from the
           side, brows read as this man's. Still: the ears' hollows red, the neck streak, the scalp's painted stubble (the
           painting has it too), the photo's warmer contrast around the eyes.
           ROUNDS 40-41 2026-10-30: each view's paint kept clear of its silhouettes (pixels on an outline are part
           background) and the UV islands padded 16 texels (a bake's margin) - both standard, both kept; neither moved the
           pale line on the neck behind the jaw (narrow, bluish: likely the relief map or a crease catching light - next,
           traced on `round.blend` by toggling the normal and albedo maps). The ears' hollows stay red (partly the
           painting's own backlit red).
           ROUND 42 2026-10-30: paint kept clear of every depth jump too (standard; kept). The neck's pale line traced on
           `round.blend`: it stays with the relief map off and goes with a flat colour - it is in the albedo; not in
           left40's or left90's light-free paintings (only the AI's natural neck creases there) - another view's edge
           (perhaps `below`); left open, small.
           ROUND 43 2026-10-31 (after a compaction the user, verbatim: "you auto compacted to re read rules docs session
           nots your rec go"). Trials on `round.blend` measured against the painting (face view): the brow cards rendered
           as a grey film - MakeHuman's own `.mhmat` for these cards says "specularColor 0 0 0", "castShadows False", ours
           had the default shine and cast shadows; with that fixed and the card masked like a hair card, every MakeHuman
           brow set (010, 011, 012) still sat higher and more arched than the painting's brows and doubled them - with no
           cards, the painted brows in the skin read as hair (kept: no brow cards; the lash cards take the `.mhmat`'s no
           shine, no shadow). The pupil 33 px wide against the painting's 21 (PupilSize 0.27; 0.14 gave 18, 0.20 gave 26)
           -> 0.16. The lower lash cards dropped (the painting shows none). The white over all its visible pixels has the
           painting's hue, ~20% darker - kept (a neutral white measured at one spot read lavender). The full Fresnel
           cornea greyed the eye - 0.3 kept. Lips (MediaPipe, per eye-corner span): upper 0.090 -> 0.086 (painting 0.080),
           lower 0.133 -> 0.130 (0.122), width 0.594 -> 0.585 (0.557), the seam 0.025 -> 0.031 (0.004) - barely moved:
           the clay views were rendered with the head's open mouth and lids, so the landmark warp stretched the painting's
           closed lips open again (the pale band between the lips), and the depth test ran on the old shape. Next (round
           44): the mouth and lid shape keys moved to `face_shape.py` and applied before the clay and depth renders, so
           the paintings are aligned to and projected onto the same surface; the open-mouth stage kept in
           `.dev/facetest/round43_open_mouth/` (what FLUX 3 painted from).
           ROUNDS 44-45 2026-10-31: the clay and depth views re-rendered with the lips closed and the lids lowered
           (`face_shape.py`, applied in `test_face_clay.py`); MediaPipe's 20 inner-lip points left out of the warp (a
           closed mouth has no inner edge on the clay - the detector guessed one at the crease, 0.051 against the
           painting's 0.004). The lips' seam went 0.031 -> 0.003 (painting 0.004), width 0.585 -> 0.562 (0.557), nose to
           mouth 0.164 -> 0.177 (0.172), mouth to chin 0.277 -> 0.286 (0.304); the pale band between the lips gone. The
           flat contact colour over the inner lips removed (it read as a strip once the projection lined up). The eye's
           shape measured against the painting: opening/width 0.340 vs 0.339, the same lid cover over the iris, tilt +8.0
           vs +6.5 degrees - the eye's shape is not the difference. Its white was one flat colour: ambient occlusion within
           6 mm (Cycles' AO node) darkens it toward the lids and corners - with the cornea shell in the eye's object AO
           turned the white black, so the cornea is split into its own object, unseen by shadow and diffuse rays (still
           light-linked to the catch light); its brightest tenth 0.258 vs the painting's 0.248 (0.287 before). The lower
           lash cards: by tip direction 100 dropped but forward-pointing lower cards stayed (dark marks on the lower lid);
           by root height 169 dropped, the upper ones too (round 45); now by eyelashes01's texture layout (upper strips on
           its top half, lower strips bottom right): 88 lower, 96 upper. Still: the upper lip 0.086 vs 0.080 and the lower
           0.128 vs 0.122; the painting's hooded upper lid (a fold over the lid, shading the eye) - shape our head lacks.
           ROUND 46 2026-10-31: the lower lashes dropped by the texture's strips (88), the upper 96 kept - no marks on the
           lower lid. The white sampled at its outer side (7x7 spots beside each iris): ours redder and a third brighter than
           the painting's, whose clean white is near neutral (r/g 1.16-1.19) - the whole-white median had mixed in its dark
           red inner corners; EyeWhiteColor (0.94, 0.70, 0.59) -> (0.68, 0.60, 0.54) for round 47. The user's FLAME files
           (2026-10-31): FLAME 2023 Open, the Mediapipe Landmark Embedding and the Vertex Masks into
           `.dev/cache/flame/` (folder made); the download page's registered expression data (FaMoS, D3DFACS, CoMA,
           VOCASET, LYHM) noted for testing the face rig later - data licence not read.
        5. Parts DONE 2026-10-29: GNM's eyes (`eyeLeft`, `eyeRight`) and teeth with gums and tongue (`teeth`) —
           MetaHuman's part names — placed in hm08's head by the wrap tool and bound to hm08's eye, teeth and tongue
           helpers with MHCLO (`tools/bind_parts.py`, round trip 0.08 mm); `juststage.head.add_parts` fits them to the
           character and refits them when the head shape changes; the head helpers now follow GNM shapes. Still in 5:
           the eye occlusion and tearline shells, the card lashes (`eyelash.L/R`), nails, the skin's micro normal
           and texture layers. DONE in 5 on 2026-10-29: the part materials (`389619b`) — one Principled BSDF per
           GNM region, the cornea's 1.376 and enamel's 1.63 measured, the rest starting values for the gate; strand
           brows and lashes are grooms (step 6); the skin material — `juststage.skin.set_tone`
           builds Principled BSDF with Random Walk (Skin) subsurface from `core/skin_optics.py` (Donner & Jensen's
           chromophores, calibrated on NIST's 100 measured skins: mean RMS 0.0098), IOR 1.4, the paper's roughness.
        6. The scalp groom with Blender's hair node groups. DONE 2026-10-29: `juststage.hair.add` attaches one of
           MakeHuman's CC0 hair-editor styles (`hair.blend` by Tomáš Klecer; the pack fetched and SHA-256-checked by
           `tools/fetch_data.py`) the way MPFB2's hair editor attaches it — MPFB2's 16 listed styles: 8 scalp, 2
           eyebrows, 4 beards and moustaches, 2 eyelashes — each a Curves object shaped by the Blender hair node
           groups it carries. Colour is Principled Hair BSDF by melanin, per strand (`melanin` and `redness` curve
           attributes; Blender's defaults 0.8 and 1.0). The body now stands on the floor (MPFB2's `feet_on_ground`,
           where the styles were groomed) with Blender's rest position on, so the strands follow its shape keys:
           roots 0.1–1.4 mm from the skin (median, all 15 styles with strands), the same on a baby's head. My decision under the go ("take your
           own recs"), attacked first: a procedural groom (Generate Hair Curves inside a scalp mask) was built and
           dropped — no standard source marks the hairline (MakeHuman's hair helper and MPFB2's scalp makeup region
           both take in the forehead, measured), and artist-made grooms are what CC5 and MetaHuman ship; one way per
           job, so the procedural command is gone. Open for later steps: the `groom_*` export attributes (step 8),
           body hair (the pack's `fur.blend`, 15 regions), hair cards (`hair.bake_cards`).
        7. The first face rig: OpenRigLogic's Python bindings built for Blender 5.3's Python 3.13; three expressions.
        8. The first Unreal plugin: import the package, build materials and groom, render.
        9. The gate renders and contact sheets (EEVEE, Cycles, Unreal) beside CC5 and MetaHuman; the user's verdict.
        The rec list, version 2, is APPROVED 2026-10-29 — the user, verbatim: "go your rec all":
        [`../plans/2026-10-29-recs.md`](../plans/2026-10-29-recs.md), R1–R21, plus two items for the user to read. Version 1 (R1–R17, CC5 + iClone on a
        Blender fork, `64f47a4`) was shown first; the user's questions and word since, verbatim: "1 what is the unreal
        plugin isnt there exisng blender metahuman plugin i dont understand that and reason for fork"; "why makehuman
        mesh cant we use methuman mesh now that it is mit?"; "what if we just focus on cc5 features for now and either
        worry about iclone later or essentially use unreas as iclne replacement"; "how can quality be metahuman if the
        mesh is not exaclty methauma?"; "ok think on your recs again and go for character creation for now and not
        iclone," → version 2. Then, verbatim: "i definelty want headshot" → R10 (photo-to-head) moved from step 7 to
        step 3 of R21, right after the base and the generators. Was: the second pass → the lead
        distills it → one complete rec list, every item researched and argued against, each piece marked
        standard (with its doc link) or NOT STANDARD → a fresh Fable session writes the synthesis and the
        standards spec → the user approves → code.

APPROVED 2026-10-29 — the user: "1 and 3 your rec go", then "3 go", then "foget 1 as you said that is in
        another session":
        - (3) The global "one way per job" rule keeps its text and gets one sentence appended after "A second
          way to do a job the kit already has is a bug.": ` In the 3D family (E:\Dev\3D) the table is the one
          JustStage's standards spec creates; until then there is none.` — DONE 2026-10-29 in
          `F:\ClaudeCode\config\CLAUDE.md`; the standards spec includes that table.
APPROVED 2026-10-29 in the `E:\Dev\3D` session — the user: "go on the just-stage research, recs 1 and 2 in
        TASKS.md", then, after the USPTO half of (1) was done: "dont worry about trademark research or to much on
        lincese research, i am more interested in getting the correct app design tools engine ect than leagal
        stuff". The recs as shown:
        - (1) The trademark check first: before the research agents start, the research session searches USPTO and
          EUIPO for JUSTSTAGE / JUST STAGE in classes 9 and 42 and records the result in §12 — a database check,
          not legal clearance. (Was "before anything goes public"; moved up because the name is already in the
          folder, the memories and these docs, and a rename gets dearer every week.)
          → USPTO DONE 2026-10-29 (RESEARCH §12). EUIPO not searched — dropped on the user's word above.
        - (2) The research: the user opens a session at `E:\Dev\3D` on Opus 5.5 at xhigh and says go there. One
          round of 8 agents — §2 CC5, §3 iClone, §4 references, §5 bases, §6 routes, §7 building blocks,
          §8 standards, §9 legal; the lead does §10 itself from the web kit's register and the JustDirect note.
          Each brief carries its section, the "don't re-derive" line, the questions and a done-when line. No
          second round of agents without the user's word; gaps after round one are filled by the lead with
          targeted lookups.
          → RUNNING 2026-10-29, changed on the user's word above (my call on the how): no §9 agent — every agent
            gives each product, library, model and asset set a one-line licence label (licence, commercial use
            yes / conditional / no / unclear, link), no legal analysis; the freed slot goes to the engine
            question, so §6 runs as two agents — (6a) existing engines and 3D apps as the base, (6b) our own
            engine's parts and the layers every route needs (render libraries, editor UI toolkits, language per
            layer, scripting and plugin embedding, AI-agent testing). Still 8 agents, Opus 5.5 at xhigh. The
            lead still checks at its source every claim a recommendation depends on.
        - Then, verbatim (2026-10-29, while round one ran): "omnivers is out it only works on nvidia cards we dont
          want restricsions anything that is commercial cost money we dont want either you cna remove from resear
          and realocate agents to other researh or a second pass"
          → sent at once to the running agents for §5, §6a, §6b, §7 and §8: Omniverse out everywhere; anything
            that costs money out as a base or a part; anything that runs on one GPU vendor only out of the core,
            and optional parts (AI models, mocap) labelled with the GPU vendors they run on; free-but-proprietary
            options (Unreal, Unity, Flax, Autodesk's FBX SDK, Mixamo) held at one short row each while the user
            decides (asked 2026-10-29); the saved effort goes into the open-source candidates. CC5, iClone and
            the reference apps stay in §2–§4 — they are studied for features, not built on (my reading). A
            second pass, if needed, runs after round one's results, on its gaps.
        - Then, verbatim, on the question about free-but-closed options: "unreal may be ok as it does have generous
          free tier, not sure about unity"
          → sent to the agents: Unreal, Unity and Flax back as full candidates in §6a, each with its terms in plain
            lines (the free tier and its revenue line, royalties or seat fees after it including non-game uses,
            what may be redistributed, whether an open-source app can ship on it); the FBX SDK, Mixamo and other
            free-but-closed parts back to normal labelled rows. Omniverse and paid-only products stay out. Unreal
            and Unity are decided by the user at the rec list, on those facts.
        - Then, verbatim: "unreal is ok i use it all the time , i dont know what unity license restrictions are if it
          doesnt have generous free tier like unreal then it is out, can you check"
          → checked at Unity's own pages (RESEARCH §6): Unity Personal ends at $200K of revenue plus funding a year,
            then $2,310 per seat per year — far smaller than Unreal's tier, so by the user's test **Unity is OUT**;
            **Unreal is IN** as a full candidate. Sent to the §6a agent.
        - Round one DONE 2026-10-29: all 8 notes in `docs/plans/2026-10-29-research-*.md`, distilled into RESEARCH
          §2–§8 (commits c2d88e3, a6c966a). The session's 200 WebSearch calls ran out partway, so each notes file has
          a "Couldn't verify / open" list.
        - Then, verbatim: "can i open a new session and get around that limit?", "i dont want to search to be
          truncated and give us limited data". My rec shown: (1) let the two running agents finish; (2) save round
          one and write one gap list, area by area; (3) find out how the cap works from Claude Code's docs; (4) a
          second pass in fresh sessions, sized to the budget — the rec list waits until every gap is closed or
          marked not findable. The user: "your rec go", then "once you verify how it works if each session has new
          limit then we open 1 session per agent".
          → (1)–(3) DONE 2026-10-29. The cap (RESEARCH §13, Claude Code's docs, verified): 200 per interactive
            conversation, shared with subagents; refills ~100 an hour; a new conversation or `/clear` resets it;
            `CLAUDE_CODE_MAX_WEB_SEARCHES_PER_SESSION` raises it. So (4) is one session per area: the eight briefs,
            the shared rules and the launch line are in
            [`../plans/2026-10-29-research-second-pass.md`](../plans/2026-10-29-research-second-pass.md) — S1 CC5,
            S2 iClone, S3 references, S4 bases, S5 engine routes, S6 own engine and layers, S7 building blocks,
            S8 standards. Each session researches itself (no subagents), writes its own `-pass2.md` and commits
            only that file; the lead distills all eight at once.
        - Then my rec shown: raise `CLAUDE_CODE_MAX_WEB_SEARCHES_PER_SESSION` so one session can run all eight
          passes as agents. The user, verbatim: "CLAUDE_CODE_MAX_WEB_SEARCHES_PER_SESSION do that so you can run it
          like you orignally planned, my 2070 runs unreal and blend and cc5 and iclone well enough. i am sure you
          can find a way to download epic licnese use another fetch or search method, your rec go"
          → DONE 2026-10-29: the cap is "2000" in the user settings' `env` (`F:\ClaudeCode\config\settings.json`;
            my call on the file — the only settings file this running session watches; it took effect without a
            restart, RESEARCH §13). Epic's EULA v15 downloaded from Epic's own CDN and read (RESEARCH §6); the live
            EULA and change log still refuse scripted reads (403, not worked around), so the current text is S5's to
            find, else the user's to read. The 2070's performance is the user's word (RESEARCH §1) — the
            "measure the finalists" item is dropped. The second pass RUNS as 8 agents in this session, one per
            section of the second-pass file, ~200 searches each, Opus 5.5 at xhigh.
        - Then, verbatim (2026-10-29, while the second pass ran): "just a note the https://github.com/storytold built all
          those adobe apps film photo ect from scratch i think so if you think it is better to actaully build the cc5
          clone and iclone and plugins from scratch that is an option we dont have to use an exisitng piece of
          software, but i thought if something is out there that is already built and tested and maintained it would
          be better than starting from scratch, but we can as https://github.com/storytold did a good job and it
          stratde from scratch i think it i am sure used some prebuilt rust components and stuff"
          → both routes are already in the research (§6a / S5 existing bases; §6b / S6 our own app on libraries).
            The lead adds storytold's repo list (GitHub's API) as evidence for the from-scratch route when it writes
            the rec list. The user's lean here is context, not a criterion (was: "a criterion" until 2026-10-29 —
            the user, below: "dont let me influence your rec").
        - Then, verbatim: "make human assests are they the quality we need, one of the main factors is that it has to
          have the quality of cc5 and metahuman characters or better hopefully even better"
          → answered from RESEARCH §5: not on their own (artist-made ~13.7k-vertex mesh, no scan detail, ARKit 52 face
            vs CC5 HD 262 + 128 correctives); scan-based open options and the gaps listed in chat. The bar is now a
            pass/fail requirement (SCOPE).
        - Then, verbatim: "its ok to fork blender there is already an artist fork, and are you shure the ui isnt
          editable withought fork, yea do we make it an epic plugin or standalone i am not sure i will let your
          research give me a rec.  dont let me influence your rec"
          → a Blender fork is an allowed route. The UI answer, checked at Blender's manual source and code: an
            application template reworks most of the UI without a fork; new editor types or core changes need one
            (RESEARCH §6, corrected). The rec rests on evidence and the hard requirements; the user's leans are
            context, never criteria.
        - Then, verbatim: "we need to be able to pull in assest from other programs just like cc5 and unreal engine and
          daz studio" — my rec shown: a 9th second-pass agent, S9 "Pulling in assets from other programs", its own
          ~200 searches (folding it into S7/S8 mid-run would stretch their budgets — the way round one got cut).
          The user: "you have ago" → S9 RUNNING 2026-10-29 (second-pass file, section S9); importing from other
          programs is a requirement (SCOPE). Then, verbatim: "things like openusd help alot as unreal i think already
          can export assets in this format" → added to S9's brief before launch: USD import and export per program and
          what survives each way.
        - Then, verbatim: "your reec on all go make sure you keep thinking about your recs adverserialy" → the plan runs
          on: the nine passes land → the lead distills them into RESEARCH.md → the one complete rec list, each rec
          attacked before it is shown, with what the attack changed.
        - Then, verbatim: "i want the best of the best in this app if that means none of the existing stuff meets the
          quality bar like texture baking grament cloth ect, then we need to do are own, we need to meet or exceed
          character mesh skin eyes ect of cc5 and unreal, cant you make your own skin textures and stuff if need be
          that meat or beat the quality of cc5, cant you make your own asset generator for skin texture, hair eyes ect.
          maybe based on metahuman or cc5 or better but interoperable with both?" — answered: the generators are
          buildable; skin realism rests on scan data, not code; eyes and hair generate more readily; interop by design
          (the UE5/MetaHuman skeleton CC5 aligned to, MetaHuman DNA through OpenRigLogic, ARKit names, CC5's UDIM
          layout; CC's base-model clause means interop by export). My rec: an S10 agent on making our own character
          assets. Then, verbatim: "i bet there are large datasets that exist for 1-3 and of course i know there are
          current ai that generate human images with all sorts of options, i think you can find a way if need be, but
          if we can reuse if not build" → folded into S10's brief. Then, verbatim: "your rec go on all"
          → S10 RUNNING 2026-10-29 (second-pass file, section S10); the requirement is in SCOPE. Then, verbatim: "not
          just mesh skin eys, i mean all of the character realism hair the whole human", "like teeth lips" → the bar
          covers the whole human; S10's brief widened and sent to the running agent.
        - Then, verbatim, on the Reallusion terms S9 found (RESEARCH §8): "it will be ok to import cc model if unreal can
          do it we can" → DECIDED: JustStage imports characters users export from CC5, as Unreal and Blender do.
          Using CC's base mesh as the base JustStage generates characters from stays out — the clean-room rule
          (`AGENTS.md`) and CC's base-model clause both bar it.

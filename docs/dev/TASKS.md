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

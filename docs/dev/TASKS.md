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
        to the `E:\Dev\3D` project. The research is RUNNING since 2026-10-29 in the `E:\Dev\3D` session (recs
        (1) and (2) below): 8 agents, each writing `docs/plans/2026-10-29-research-<subject>.md`; each lands in
        RESEARCH.md as it arrives.

NEXT:   the research → one complete rec list, every item researched and argued against, each piece marked
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

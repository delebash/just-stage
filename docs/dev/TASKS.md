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
        two (the user's lean above); JustDirect inside JustStage or beside it.

STATE:  setup DONE 2026-10-29 — this repo and its docs, the global CLAUDE.md edit, the general memories copied
        to the `E:\Dev\3D` project. The research is NOT STARTED: it runs in a session the user opens at
        `E:\Dev\3D`, on the user's go there.

NEXT:   the research → one complete rec list, every item researched and argued against, each piece marked
        standard (with its doc link) or NOT STANDARD → a fresh Fable session writes the synthesis and the
        standards spec → the user approves → code.

## The global "one way per job" rule names the web kit's table — for the user's word [2026-10-29]

FOUND:  the global CLAUDE.md rule "**One way per job** … find its job in the kit's table
        (`just-core/docs/app-structure.md` §19)" was not part of the approved edit and still points every
        session, this family's included, at the web kit's table. JustStage has no such table yet. Not changed —
        waiting on the user's word.

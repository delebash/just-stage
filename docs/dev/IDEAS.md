# IDEAS — the backlog

The one place to drop ideas for this app that aren't scheduled work. Not a plan, not a spec — a
holding pen so nothing good gets lost. Committed work lives in `TASKS.md`; when an idea is picked up
it moves to a plan and gets a link here (or is struck through).

- Keep entries short: the itch, the rough shape, why it matters.
- Newest at the top. Date each one.
- Anyone (user or agent) can add here; adding an idea is never starting it.

---

## 2026-10-29 — Describe a person, get the character

The user, verbatim: "we are definitly adding lots of good ai features to this app like cc5 and we will come of with
more", then "well we dont have to do it now but i want user to be able to descibe a person and the app creates that
person mesh, or creates stuff like that that". Rough shape, on pieces the plan already has: a local text model (the
kit's llama.cpp) reads the description and picks values for our named sliders (MakeHuman's 234 labelled slider
categories, review item 3) through the same commands an assistant calls (item 7); the image model makes the skin and
hair textures; a picture can go through photo-to-head (R10); or an image-to-3D model's mesh (trellis.cpp, RESEARCH §7)
is wrapped onto our base, CC5's way (its cloud AI 3D generator plus Body Wrap, RESEARCH §2). The same pattern fits
props and clothes. The rule every AI feature follows is review item 25.

## 2026-10-29 — AI makes the movie

The user, verbatim: "with ai we might just need character creation prop scene and camera managment then let
ai create movie, this is just a thought we need to keep in mide". JustStage builds the characters, props,
scene and cameras; an AI model renders the film from them. Ties to JustDirect and RESEARCH §10.

## 2026-10-29 — Workspaces, a sketch from the chat

Not decided: Character (the CC5 side), Scene (sets, props, lights, cameras), Animate (timeline, mocap,
face and lip-sync), Render / Export, Direct (if JustDirect moves in). The real list comes from the feature
inventory (RESEARCH §2–§3); the user leans to one app that feels like two distinct apps.

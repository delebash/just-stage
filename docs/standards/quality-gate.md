# The quality gate — procedure (R3)

> **Status: DRAFT, 2026-10-29 — for the user's approval** (see [`README.md`](README.md)). R3: "The bar is a measured
> gate, before the features." The user's bar (TASKS): "the quality of cc5 and metahuman characters or better", for
> "all of the character realism hair the whole human", "like teeth lips". Facts: RESEARCH §5, §7 (S10 §4: no source
> compares any open asset with CC5 or MetaHuman — only our renders can).

## 1 · What is built for the gate (step 1 of R21)

One JustStage head and shoulders, from the standards above and nothing else: the base head at level 2 with
displacement, generated skin (albedo, specular, roughness, cavity, micro normal, displacement; the melanin and
haemoglobin layers; pores and wrinkles), eyes (shader, procedural iris, wetness, occlusion, tearline), lips, teeth,
gums and tongue, brows, lashes, a scalp groom, nails on one hand, one neutral and three expressions (`jawOpen`,
`mouthSmileLeft`+`Right`, `browInnerUp`) through the first face rig. Plus the first, minimal Unreal plugin: import the
package, build the materials and groom, render.

## 2 · The comparison set

| Subject | Source | Note |
|---|---|---|
| JustStage head | this build | |
| CC5 HD character | one of CC5's shipped HD characters, exported by the user from their CC5 with the Blender and Unreal presets (the user owns CC5; Reallusion's terms allow export to other software — §8) | kept out of the repo (Reallusion content EULA) |
| MetaHuman | one preset MetaHuman from the user's Unreal install | kept out of the repo (Epic's terms) |

## 3 · Renders

Same camera (85 mm, head-and-shoulders framing), same HDRI (a Poly Haven CC0 studio HDRI, named in the report),
same resolution (2048 × 2048), same colour management (AgX / Unreal's default tone mapper noted), four views (front,
three-quarter, profile, close-up of the eye and lip corner), the neutral and the three expressions:

| Renderer | Platform | Who renders |
|---|---|---|
| EEVEE (Blender 5.2 LTS) | the user's RTX 2070 Super | the gate script, headless |
| Cycles (256 samples, OIDN) | the same | the gate script |
| Unreal 5.8 (Lumen, the MetaHuman shaders for the MetaHuman; our plugin's materials for ours; CC5's Auto Setup for CC5's) | the same | the plugin's test map |

CC5's own viewport is not a renderer here (Windows DirectX 11, not scriptable from our side); its exported character
is rendered in Blender and Unreal beside ours.

## 4 · Measurements recorded with the renders

- EEVEE viewport fps with the head alone and with the body (level 2) at the 2K, 4K and 8K working resolutions, VRAM
  in use at each (Blender's statistics; `nvidia-smi`) — the numbers that fix the resolution budget of
  [`character-data-model.md`](character-data-model.md) §3.1; Cycles time per frame at 8K.
- The peak VRAM of one skin-generation job on the engine host beside the EEVEE viewport ([`ai-engines.md`](ai-engines.md) §4).
- The shape-space wrap errors (max, mean, mm) for MHR and GNM onto the base ([`character-data-model.md`](character-data-model.md) §1.2).
- The face rig's control count and the shapes it drives.

## 5 · The verdict

The user judges the contact sheets **part by part** — skin, eyes, lips, teeth and gums, tongue, brows, lashes, scalp
hair, nails, overall — and per renderer, each as *above*, *equal* or *below* CC5 and MetaHuman. **The gate passes when
no part is below either reference in any renderer** (R3: "at or above both"). A failing part gets a named fix list;
the gate repeats on that part only.

The report (`docs/gate/<date>/report.md` with the contact sheets, the numbers of §4 and the user's words verbatim) is
the proof; TASKS records the verdict as the approval of step 1.

## 6 · After the gate

The passing head becomes the first library asset, the first golden-image fixture and the first scorecard `done` rows
(skin, eyes, mouth, brows and lashes, scalp hair, face rig minimal). The gate's numbers become the baseline every later
step must hold (a golden-image test fails if a change drops a part below its gate render by more than the oiiotool
threshold).

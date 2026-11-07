# The quality gate — procedure (R3)

> **Status: APPROVED** - written 2026-10-29 (the review's items 2, 3, 4, 16, 21, 23 - TASKS; review file
> [`../plans/2026-10-29-spec-review-opus.md`](../plans/2026-10-29-spec-review-opus.md)); brought to the user's later
> decisions 2026-11-07 (Q-SPEC, [`../plans/2026-11-06-the-plan.md`](../plans/2026-11-06-the-plan.md) §2, §19.1): the
> bar is CC5's HD Aaron (TASKS "HD AARON IS THE BAR", "THE GATE PART BY PART", "THE ONE PRIORITY"); MetaHuman was
> dropped as a benchmark (TASKS 2026-11-04, "CC5 IS THE STANDARD") and stays a design reference only. R3: "The bar is
> a measured gate, before the features."

## 1 · The bar

CC5's HD Aaron, rendered in Blender, part by part - every part of the body, toenails too (the user, 2026-11-05: "it
has to be all parts of body meat quality bar not just skin"; "toe nails too, all body parts"). Then the same method,
with no per-character tuning, on four or more different characters (sex, age, tone, face shape) - THE ONE PRIORITY.
**The bar is the live view: ours against Aaron, both in EEVEE** (the user, 2026-11-05: "realism in live view is the
bar with known improvement with cycles render"; 2026-11-07: "my concer was live view in cc5 = eevee, so why do you keep
worrying about cycles?"; "that has always been the bar ... why do you keep changing the bar we set multple time").
Cycles is not part of the verdict and Aaron is never compared in it. It is a diagnostic only: when ours is off from
Aaron, our own Cycles render of the same scene tells whether the gap is our content or EEVEE's shortcut (AGENTS.md's
oracle rule), and the film is checked to be no worse than the live view.

## 2 · The comparison set

| Subject | Source | Note |
|---|---|---|
| JustStage | the library's characters built the app's way (`tools/gate/parts_gate.py`: Average man, the scan skin, the hair library's scalp and brows, stubble as a groom) | inputs audited CC5's way first (`../plans/2026-11-06-inputs-audit.md`) |
| HD Aaron | the user's CC5 Blender Pipeline export (SubD 1), imported by CC Blender Tools; hair and stubble on | a LOCAL test: kept out of the repo, nothing of it ships (AGENTS.md) |
| HD Ariana | the same, once the user exports her (plan §19.2) - the women's reference for the multi-character run | as above |
| CC5's own captures | through the cc5 MCP bridge, only where Blender's Aaron may fall short: eyes, brows and lashes, teeth with the jaw open, nails | 600 x 600, the trial's logo across the middle |

Unreal is out of the part gate (plan §19.1 item 4); it is judged with the full plugin.

## 3 · Renders

`tools/gate/parts_gate.py render`: each character alone on the app's stage (key, rim, the studio image at 0.25) and
through the app's look (AgX "Medium High Contrast", -0.3 - `core/viewport.py`), 2048 x 2048, 85 mm, in EEVEE (Cycles,
256 samples, OIDN, only for ours when a gap is diagnosed - §1). Twenty-one views, each camera placed from anatomy measured on each character (front,
three-quarter, profile, face, back of the hair, eye, lips, lip corner, cheek, ear, torso, hand, nails, foot,
toenails, full body; jawOpen, smile, browInnerUp), so a view frames the same part on both. Each render's frame width
goes to `frames.json` beside it.

## 4 · Measures

`tools/gate/measure.py` on the renders, per view and window (fractions of the frame, outlined on a copy of each render
and looked at before a number is used):

- **colour** - CIE L*, a*, b* of the window's skin (sRGB D65, through the app's look);
- **detail by scale** - the L* power spectrum, radially averaged (ISO 25178-2's power spectral density), summed over
  bands of real size on the skin: micro 0.06-0.3 mm, pores 0.3-1.5, folds 1.5-7, form 7-30 (an RMS in L* units; a band
  the view doesn't resolve reads None);
- **ridges** - Frangi's 1998 vesselness at 1.5-8 mm (veins, tendons, creases apart from speckle), dark and light;
- **repeatability** - each measure's spread with the window moved 1.5% of the frame (3 x 3 positions);
- **texture structure** - DISTS (Ding et al. 2020) as two samples of skin (`tools/gate/dists.py --patches`): five
  patches per view, ours against his beside his against his own; "the same texture" is an excess (ours-against-his
  less the two within-means' average) of ~0. Not the 1.5%-jitter floor - that is the same pixels moved (2026-11-07).

Also recorded, as before: the live view's frame time on the GPU (`--gpu-backend opengl --profile-gpu` - OpenGL's
timestamps; the default Vulkan backend is unmeasured, said with each number) and VRAM at the working resolutions; the
shape-space wrap errors; the face rig's control count; the cost of hm08's helper geometry; HD slider memory; the
materials across the USD trip.

## 5 · The verdict

Per part, in EEVEE: **equal** = Aaron's value within the measure's repeatability band, two-sided; **above** only
by the user's eye on the contact sheet, never by a bigger number (gate run 1's orange-peel skin had more detail than
Aaron and read worse); a band over 15% means the window straddles a feature and is moved (skin itself varies 8-9% within
1.5% of the frame on the cheek, measured 2026-11-07). A part short of the bar is diagnosed one factor at a
time (`--cc5-inputs`, scratch factor renders) before it is fixed. **The gate passes when no part is below Aaron in
the live view (EEVEE)**, and the same holds on four or more characters.

The report (`docs/gate/<date>/report.md`: the sheets, the numbers, the inputs table, the user's words verbatim) is the
proof; TASKS records the verdict.

## 6 · After the gate

The passing views become golden fixtures under Blender's render-test method (`render_report.py`, `oiiotool --fail`):
a change that drops a part below its gate render fails. The gate's numbers become the baseline every later step holds.

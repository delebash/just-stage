# The gate's first measured baseline (2026-11-07)

THE ONE PRIORITY's first proof (face mid-scale relief) and the body views, on today's code: the clean inputs of
`../2026-11-06/report.md` (its inputs table holds; since then the oiliness link and no pores on lips or lining, commit
0e95ddc), measured with the standard measures of `tools/gate/measure.py` (`../../standards/quality-gate.md` §4).
Renders `.dev/gate/parts/2026-11-07a` (`tools/gate/parts_gate.py render`, views eye, cheek, face, front, torso, hand,
foot; ours = the library's Average man in the Scan man A skin; HD Aaron from the user's export).

## How to read the numbers

Per window: CIE L* a* b*; detail as the RMS of L* per band of real size on the skin (micro 0.06-0.3 mm, pores 0.3-1.5,
folds 1.5-7, form 7-30), each window's form removed first; ours as a ratio of Aaron's, "=" within that measure's band
on Aaron (the window moved 1.5% of the frame, ~1 mm), "<" or ">" outside it. Windows were set by looking at their
outlines (`windows_<engine>_<view>_<who>.png`): the cheek above the stubble, the forehead above both brows.

## EEVEE (the live view)

| View / window | Ours L* a* b* | Aaron's | micro | pores | folds | form |
|---|---|---|---|---|---|---|
| cheek / cheek | 75.5 11.1 13.8 | 73.3 13.0 12.6 | 0.75 < (9%) | 0.86 < (8%) | 0.72 < (9%) | 0.91 = (16%) |
| eye / forehead | 77.2 10.4 13.1 | 71.8 12.5 12.1 | - | 0.92 = (13%) | 0.83 = (18%) | - (window too small) |
| face / face | 54.2 13.8 16.9 | 47.0 16.1 16.0 | - | 1.45 > (8%) | 0.94 < (5%) | 0.81 < (3%) |
| torso / chest | 64.6 13.4 19.3 | 57.9 14.3 21.7 | - | - | 0.85 < (2%) | 0.68 < (17%) |
| foot / top of foot | 67.8 12.4 17.8 | 54.4 16.4 21.7 | - | 0.47 < (32%) | 0.25 < (17%) | 0.29 < (19%) |
| hand / back of hand | (window moved below the knuckles; re-measured with Cycles) | | | | | |

**Read:**
- **Face skin: below Aaron at the cheek** - microrelief, pores and folds each beyond the band (0.72-0.86). This replaces
  the "cheek equal" of 2026-11-06 (pore / fold 1.135 / 0.884 vs 1.154 / 0.894), which was measured before four relief
  fixes and with the old band measure. The forehead's pores and folds are equal within their bands.
- **The face window's pores above (1.45)** - the window takes in our stubble and brows (our stubble's chin share 0.099
  against his 0.061, commit 3c04b4a): to diagnose before it counts.
- **Tone: ours paler and less red** everywhere (L* +2 to +13, a* -1 to -4) - Aaron's tone is his; the gate's man may
  take Aaron's tone as he took his hair colour, so only the content differs (to do, as a factor).
- **Body: below** - the torso's folds and form (a narrower, smoother man than Aaron's sculpted physique), and the feet
  far below (25-47%: flat, as run 11 saw).
- **Hands, by eye** (`windows_eevee_hand_*.png`): ours flat and pale; Aaron's tendons, veins and knuckle creases.

## Cycles (the film, the live view's oracle)

| View / window | Ours L* a* b* | Aaron's | micro | pores | folds | form |
|---|---|---|---|---|---|---|
| cheek / cheek | 74.7 11.9 14.2 | 72.7 14.3 13.3 | 0.44 < (7%) | 0.55 < (6%) | 0.51 < (8%) | 0.74 < (13%) |
| eye / forehead | 76.4 11.1 13.6 | 73.7 13.1 12.5 | - | 0.68 < (13%) | 0.61 < (17%) | - |
| face / face | (Aaron's window cover 0.875 - his face view frames lower; window to move) | | | | | |
| hand / back of hand | 76.5 10.4 14.1 | 67.1 15.7 17.9 | - | 0.29 < (15%) | 0.35 < (20%) | 0.53 < (18%) |
| foot / top of foot | 68.0 12.9 18.0 | 54.7 16.8 21.2 | - | 0.29 < (28%) | 0.17 < (15%) | 0.20 < (20%) |
| torso / chest | 64.0 14.1 19.5 | 57.6 15.2 21.6 | - | - | 0.53 < (2%) | 0.57 < (16%) |

**Read:** in the film, ours is about half of Aaron's detail at the cheek and 0.6-0.7 at the forehead - the face proof
is **not proved in either renderer**, and the gap is larger in Cycles. Aaron's own detail reads ~1.6x stronger in
Cycles than in EEVEE (cheek pores 2.69 against 1.73), ours the same in both (1.47 / 1.49). Why is not yet known - a
hypothesis to test one factor at a time: his maps (normal + micro normal) gain from Cycles' many samples per pixel
where EEVEE's texture filtering softens them, and our bump-node relief behaves differently. Hands and feet: a third of his or less.

## Next

The cheek's gap one factor at a time (`tools/gate/factors.py`: relief0, pores0, micro0, colourpores0, colourflat), then
the fix, re-measured in both renderers; Cycles' numbers beside these; the hand donor (Ten24's sample, on disk).

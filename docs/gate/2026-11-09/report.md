# The full gate on our own content (2026-11-09 / 10)

The plan's last step (`../../plans/2026-11-06-the-plan.md`, "the multi-character run and the full gate"), on the
product as it stands after the own-content proof (`../../plans/2026-11-08-own-content-proof.md`): the library's
Average man (the Scan man A skin - six scans' colour, the colour relief of 11-09, Ten24's pores, the layered
microrelief; the hair library's scalp; strand brows, lashes and stubble) at every view of
`../../standards/quality-gate.md` §3, beside HD Aaron rendered in the same run on the same stage, measured with §4's
measures. Renders `.dev/gate/parts/2026-11-09gate` (`tools/gate/parts_gate.py render`, EEVEE, 2048 x 2048); sheets
`<scratchpad>/gate/row_<view>.png`; the table `<scratchpad>/gate_table.txt` (scratchpad: the job's,
`F:/ClaudeCode/tmp/claude/bff537e12af9b769/5a1c3314-77f3-4a60-8d1a-9d80b40bc2f8/scratchpad`).

The bar (the user, 2026-11-08): "if a human cant visually tell the difference on closeup than it is good enough"; the
gate passes when no part is below HD Aaron in the live view, on four or more characters (quality-gate §5). **The
verdict is the user's** - this report holds the evidence and my reading of it.

## The question of 2026-11-09: can free resources reach it?

The user: "never stop until you have proven or disproven we can do this with free resources". **No part is blocked
by a missing free asset.** The two parts called "can't" at 18:1x were both disproven the same night:

- **The face's mid-scale relief** - in the product (commits d8008af, 532cf98; verified unit 45, tools 60, Blender
  209): the scans' own colour (HSRD-100, CC BY 4.0) holds the wrinkles their meshes lost; Sapiens2's normal model reads
  them back at build time (`tools/face_test/colour_relief.py`, NOT STANDARD).
- **The live-view hair** - on trial (`factors vfpoly*B4*0.2*strands`): VincentFreelance's free cut (CC BY 4.0) on
  Polytricity's free 4K strand strips (CC BY 4.0) in our hair model reads as hair; its short sides as the cut's cap
  shaded as clipped hair. Into the product it changes Q-HAIR-7 - the user's decision.

## Every view, EEVEE, ours against HD Aaron (by eye at full size; numbers where §4 measures the view)

| View | Reading | Numbers (ours / his; "=" within his own spread) |
|---|---|---|
| cheek | **matches** - pores, fine relief and colour read alike | micro 1.07 =, pores 0.94 =, folds 0.93 =, form 0.96 = |
| nose | close - real skin; our nostril crease a little deeper | - |
| forehead | close - real creases; his skin a crisper fine net of pits | pores 0.51 <, folds 0.62 < |
| chin, lips | close - our stubble sparser and browner than his salt-and-pepper; our lips a little pinker and smoother | - |
| lip corner | close - the lip a more saturated pink | - |
| eye | **below** - our upper lid low over the iris, the lower rim a wide pale ledge (the lid's shape: the plan's escalation, Q-BASE-4, open) | sclera L* 70 / 74, not brighter |
| eye_blink | **close since 2026-11-10 01:3x** - the closed lid reads as skin (the blink fades in a soft colour, object-space pores, the eye tint lifted - `maps._closed_lid_skin`); smoother than his, no lid creases | open eye pixel-equal |
| face, front, three-quarter, profile | below - the face reads made beside his: the lids (above), the hair (the library's strands: a soft grey helmet in the live view), the lips' colour | - |
| hair_back | **below** in the product (the strands' live-view haze); the free card trial reads as hair (not in the product) | - |
| ear | close - our concha a shallow dish against his pit to the canal: **hm08's topology** (a real ear's shape wrapped on - HUTUBS, 11-10 - changes the outline, not the pit) | - |
| torso, full | close in skin; his build is athletic (a setting, not the skin) | torso folds 0.95, form 0.69 |
| hand | **matches in detail at his tone** - veins and tendons; paler (a setting) | at melanin 0.03: 0.65 / 0.74 / 1.06; at 0.08 (L* 60, his 68): 1.41 / 1.37 / 1.88 - his brightness between |
| nails | close | - |
| foot | **matches in detail at his tone** - tendons and veins; paler (a setting) | at melanin 0.03: 0.58 / 0.62 / 0.68; at 0.08 (L* 47, his 54): 1.15 = / 1.06 = / 1.07 = |
| smile | close - the corners and cheeks lift; his eyes narrow more | - |
| mouth open, talk | close - the "aa" pairing was unequal (ours jawOpen 0.4 against his full V_Open); at 0.8 (11-10, the gate's pairing now) the opening matches his and the inner mouth reads as a mouth | - |

Paler hands and feet - measured 2026-11-10 00:31 (`.dev/gate/parts/2026-11-10handtone`, `factors skintone*`, one
factor): the same skin at melanin 0.08 brings the foot's detail within his spread and the hand's above it - at his
own brightness both sit at his level. The gap at melanin 0.03 is the Average man's lighter tone (L* in the bands
falls with a lighter albedo), not the detail.

## Four or more characters

The Average man and five more library characters - the Average woman (Scan woman A), the Young woman (Scan woman
B), the Older man (Scan man C, dark), the Heavy woman (Scan woman C, dark) and the Muscular man (dark) - at the face,
three-quarter, eye and cheek views (sheets `<scratchpad>/gate/chars_<view>.png`; every character wears the gate's
short taper - the gate's own setup, so their hair is not judged here). **The skin holds on every one** - real
pores and creases, colour across the tones with no patches where the scans end, the women smoother, the dark skins
within ~3 delta-E of measured skin (ISSA, 11-09). **The eye's fault is on every one** - the low upper lid and the
pale lower ledge: the shared head's shape, not one skin's. No CC5 woman or dark-skinned CC5 character to compare
(HD Ariana, Q-GATE-3).

## What is left, and whose it is

**The user's decisions:**
1. **The hair into the product** - it changes Q-HAIR-7 ("cards from MakeHuman's CC0 card meshes and the 85 CC0 card
   alphas"). My recommendation: replace it with the free cut plus Polytricity's strips - the only free cards that read
   as hair so far.
2. **The eye's lid shape and the ear's concha** - both hm08's topology (the lid's ledge, 11-09; the ear's missing
   pit, 11-10: a real ear wrapped on keeps the dish); the plan's escalation (the head alone on a new topology) sits on
   Q-BASE-4, OPEN: the design and the spec disagree on the fallback.

**Work (mine, no decision):** the forehead's fine net (a better microrelief generator - a scanned one at his
resolution is paid). Done since: the closed lid (11-10 01:3x), HUTUBS's 58 ears in the mixer (Q-EAR-1, 03:40).

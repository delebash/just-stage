# Character realism — the rec list after the 2026-10-30 research

The five research files (every search logged in each): `2026-10-30-research-ai-texturing.md`,
`-ai-photo-to-head.md`, `-skin-detail-shading.md`, `-hair-eyes-teeth.md`, `-all-functions.md`. Ranked by how good the
method is; licence, memory and platform are labels. "Our code from the published method" is NOT STANDARD by the family
rule — each such piece names the tool it would otherwise be and why that tool can't run here.

## Facts re-checked by this session (2026-10-30, GitHub / Hugging Face APIs and licence files)

| What | Licence (code / weights) | Last update | Checked |
|---|---|---|---|
| `thedeoxen/refcontrol-FLUX.2-klein-4B-reference-depth-lora` (reference + depth control) | — / Apache-2.0; base `FLUX.2-klein-base-4B` Apache-2.0, not gated | 2026-05-28, 12 likes | HF API |
| `huanngzh/MV-Adapter` | Apache-2.0 / Apache-2.0 (base SD2.1/SDXL OpenRAIL++) | 2025-06-13 | GitHub + HF API |
| `creador/mv-adapter-sd21-onnx` (community ONNX conversion) | — / OpenRAIL++ | 2026-10-29, 0 downloads | HF API |
| `huawei-bayerlab/marigold-v2` (light removal) | Apache-2.0 | 2026-10-05 | GitHub API |
| `prs-eth/marigold-iid-appearance-v1-1` | — / OpenRAIL++ | 2025-05-20 | HF API |
| `LinzhouLi/RealDenseFace` (photo → face shape) | MIT / MIT card (training data includes Ava-256, CC BY-NC) | 2026-10-29, 0 downloads | HF API |
| `nmoehrle/mvs-texturing` (seam levelling) | BSD-3 (its LICENSE text; GitHub shows "NOASSERTION") | 2026-03-11 | licence file |
| `microsoft/MoGe` (relief/normals) | MIT (its LICENSE text) | 2026-10-24 | licence file |
| `ByteDance-Seed/SeedVR` (SeedVR2 upscaling) | Apache-2.0 | 2026-01-27 | GitHub API |
| `USC-ICT/ICT-FaceKit` (eye occlusion, tearline, caruncle meshes) | MIT | 2020-12-01 | GitHub API |
| `yxuhan/OpenDelight` (face light removal) | GPL-3.0 | 2026-05-08, 31 ★ | GitHub API |
| `digital-salon/Digital-Salon` (text → hair) | MIT | 2025-07-14 | GitHub API |

Not measured on this machine yet: every model's memory on the 8 GB card, the refcontrol LoRA on the klein 4B we run
(it was trained on klein *base* 4B), how any of these look on our head.

## The recs, in build order

1. **Skin from AI pictures — paint each view with a reference AND our head's depth.** The refcontrol LoRA makes FLUX.2
   klein keep one face (the reference: the approved front view) while following each view's depth picture of OUR head
   — the drift is stopped where it starts, not warped away after. Each next view also gets the paint already projected
   (ConsistenTex's idea, ECCV 2024). Runs on our engine (stable-diffusion.cpp takes LoRAs).
   *Fallback:* MV-Adapter's SD2.1 model (paints all views together, Apache; 512 px — base colour only).
   *Attack:* trained on klein base, untested on our distilled 4B — the first measurement says yes or no before
   anything is built on it. The 9B variants are better liked (81 likes) but 9B may not fit 8 GB.
2. **Seams — one view per face of the mesh, colours levelled across seams, then blended** (Waechter et al. 2014, the
   method in `mvs-texturing`, BSD-3). NOT STANDARD: our NumPy code from the published method (the tool is C++ for
   photogrammetry meshes); it replaces the face test's blending.
3. **Take the light out of each painted view before projecting.** First the no-model way: fit the light from our
   mesh's known normals and divide it out, with a baked crease-shadow map. Marigold V2's albedo (Apache) if that isn't
   enough. *Attack:* Marigold V2 is a LoRA on Qwen-Image-Edit (17 GB in PyTorch; on our engine unknown) — so the
   no-model way leads.
4. **Shape — make our head the painted person.** RealDenseFace (MIT) reads, per face pixel, which point of the head it
   shows — thousands of matches instead of 478 points — and the solve frees pose and camera with the identity (why our
   fit failed). FLAME 2023 Open (CC-BY-4.0) wrapped onto GNM once with our wrap tool carries it to our head. NOT
   STANDARD: its CUDA solver rewritten in NumPy. *Labels:* its training data includes Ava-256 (non-commercial); its
   encoder needs "Built with DINOv3". *Attack:* brand new (0 downloads); memory unmeasured — measured before use.
5. **Skin shading the professional way.** Roughness and cavity maps instead of one roughness; two specular lobes;
   relief from real height, not brightness (the face test's `detail.py` way goes); pores from training-free sources
   — Disney's micro-wrinkle method (SGP 2023), tiles from the CC-BY 3.0 Lee Perry-Smith scan; true displacement baked
   with Multires (Blender 5.3; adaptive subdivision no longer experimental); Cycles for final renders (EEVEE lacks
   Random Walk skin scattering). Relief from pictures where needed: MoGe-2 (MIT, official ONNX) or StableNormal (Apache).
6. **Eyes.** ICT-FaceKit's (MIT) eye occlusion, tearline and caruncle meshes as templates fitted to our eyes; the iris
   ~3.6 mm behind the cornea (Navarro's eye optics); a procedural iris.
   *Correction 2026-10-31 (the user: "your rec on all"; the text above is kept as approved):* ICT-FaceKit ships no
   caruncle mesh - its inner-corner piece is "eye blend" (24 vertices); MetaHuman's is `cartilage`. The corner's
   pink comes from the painting projected onto our skin (`2026-10-31-audit-eyes.md` §6).
7. **Hair.** Real hair colours (melanin values per colour, per-strand variation — today's defaults are all red
   pigment), Cycles hair, 100K+ scalp strands for renders, brows and lashes at real counts (lashes 90–160 upper);
   later, Digital Salon's (MIT) text → groom search and DiffLocks' published Blender recipe for a CC0 groom library
   of our own.
8. **Sharpness.** SeedVR2 (Apache; its README: 8 GB with GGUF Q4) to upscale the skin textures; Real-ESRGAN inside
   stable-diffusion.cpp as the fallback.

Later steps, found and logged for when we reach them (not now): motion — NVIDIA's Kimodo and GEM-X on SOMA (NVIDIA
Open Model License; C++/GGML ports, Apache); rigging — SkinTokens; expressions — transfer from MPFB2's Faceunits or
ICT-FaceKit (no model); clothing — NGL-Prompter's method; Blender 5.2's XPBD cloth and hair, 5.3's EEVEE Material
Lighting nodes.

## Decisions for the user

1. **OpenRAIL weights** (the SD2.1 base under MV-Adapter, Marigold IID): rec — allowed as labelled fallbacks only;
   rec 1 doesn't need them.
2. **RealDenseFace's weights were trained on non-commercial data** (Ava-256): rec — use it, labelled, as rec 4 says;
   the attack: if that's unacceptable, the fallback is a landmark fit with pose and camera freed (training-free, weaker).
3. **CC Blender Tools** (GPL-3, ships Reallusion's texture files) as a reference: rec — no; the clean-room rule
   (AGENTS.md) bars Reallusion content, and nothing above needs it.
4. **A small LoRA of our own:** rec — not now; rec 1's LoRA exists. If a skin or iris LoRA is needed later, an SDXL
   LoRA fits 8 GB (kohya: "8GB GPU memory (10GB recommended)"); klein 4B is at the edge (SimpleTuner ~8 GB at int8).

## First step on a go

Measure before building: download the refcontrol LoRA, run it on our engine with our head's depth and the approved
front view, render one view — does the face hold and follow the depth? Then RealDenseFace's memory on this card.

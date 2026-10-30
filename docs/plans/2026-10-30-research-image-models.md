# The image model that paints each view — FLUX 3 Image Klein and Krea 2 beside FLUX.2 klein (2026-10-30)

The user, verbatim, while the refcontrol measurement ran: "dont we use flux.3 is there an updated version?"; "what is
the addon name i want to research it"; "does flux 3 not do this already?" (pasting a summary of FLUX 3 Image Klein's
multi-reference identity keeping, layout boxes and pixel restoration); "what about krea 2 and krea 2 turbo"; "user do
report flux 3 may acutall not be as good as flux2". What we run today: FLUX.2 klein 4B (Apache-2.0), house-paint's row.
Labels, never filters: licence, memory, platform. *[page]* = read at the page; *[API]* = Hugging Face's API;
*[snippet]* = a search result's text only.

## The add-on we are measuring

- `thedeoxen/refcontrol-FLUX.2-klein-4B-reference-depth-lora` — a LoRA (a 92 MB add-on file that teaches the model one
  extra job): image 1 a depth picture, image 2 the person, trigger word `refcontrol`; weight 0.8–1.0; "best when the
  depth map's object scale is close to the reference's" *[snippet of its card]*. The same author's set *[API, 30-day
  downloads / likes]*: FLUX.2 klein 9B reference-depth (4,633 / 81), -pose (8,956 / 67), -canny, -normal, -lineart;
  the 4B depth (2,015 / 12); FLUX.1 Kontext versions; and a pose ControlNet for Krea 2 (15,386 / 123).

## FLUX 3 Image Klein (Black Forest Labs, 2026-10-15)

- 5.6B image model; text encoder Qwen3-VL-4B-Instruct on top. Distilled: 16 steps, no guidance; Base: 50 steps, CFG 4,
  for fine-tuning and LoRAs. "text-to-image, editing with up to 10 reference images, and layout control with bounding
  boxes, through one model"; up to 4K. A separate 9B prompt upsampler (Apache-2.0): "Do not use the model without it"
  — trained on the captions it writes. Peak memory on a B200 at 1024²: 31 GB bf16, 26 GB fp8, 25 GB nvfp4; for 8 GB
  cards it points to "the int8 files in ComfyUI"; "This code has no int8 path". Code Apache-2.0, weights the FLUX
  Kommunity License (gated). **Depth, pose or structure control: not mentioned anywhere in the README.** — GitHub
  `black-forest-labs/flux-3-image-klein` README *[page]*.
- Bounding boxes "are not a hard mask" (its model card, quoted by eesel) — they place things roughly, they don't follow
  a shape.
- Quality: BFL claims +91 Elo text-to-image and +70 editing over FLUX.2 klein 9B. Testers, collected by eesel.ai (last
  edited 2026-10-18): distorted faces, hands and bodies in text-to-image ("VERY poor"; failed "a human test" no newer
  model had failed); editing praised ("really solid"); verdict "a strong editor and a weak generator of people"; BFL's
  answer two days in: prompt upsampling and 2K. On 8 GB: "the INT8 build runs on GeForce RTX cards with as little as
  8 GB", the upsampler adding ~28 GB; RTX 4070 1 MP in 8.9 s. Licence: free for "gross annualized revenue under
  US$5,000,000" with output filtering *[page, eesel; the licence file itself gated, unread]*. A LoRA trained on Base
  loads into the distilled model at ~0.75 *[page, eesel]*.
- Artificial Analysis' open-weights board (read 2026-10-29, RESEARCH §7): FLUX 3 Image Klein 1043, FLUX.2 klein 9B 929,
  4B 837 — text-to-image preference votes, not faces held to a shape.
- On this PC (just-core RESEARCH, JustDirect's measurements 2026-10-26/27): "FLUX.3 klein Q8_0 planned as one 7.7 GB
  segment and failed on 8 GB without a `--max-vram` budget" in stable-diffusion.cpp. stable-diffusion.cpp runs FLUX.3
  Klein (its README; `leejet/flux-3-image-klein-GGUF` exists *[API]*).
- Add-ons for it *[API search]*: no depth or reference-depth LoRA found (`flux-3-image-klein-depth`: none;
  `flux-3-klein-lora`: an "angles" LoRA by akhaliq, a Halloween LoRA, an NF4 file for LoRA training).

## Krea 2 Raw and Krea 2 Turbo (Krea, 2026-06-22)

- 12B diffusion transformer ("13B params" in HF's metadata); text encoder Qwen3-VL 4B; Wan 2.1 VAE. Raw: 28–50 steps
  with CFG, for fine-tuning; Turbo: distilled, "--steps 8 --cfg 0.0 --mu 1.15 --width 2048 --height 2048". "Krea 2 is
  a text-to-image diffusion model" — no editing, reference images or control in the card. Gated. — HF
  `krea/Krea-2-Turbo` card *[page]*. Memory: 8 GB+ int8, 16 GB+ fp8, 24 GB+ bf16 *[page, comfyui-wiki]*.
- Licence: Krea 2 Community License — commercial use free under US$1,000,000 trailing-twelve-month revenue, an
  enterprise licence above it or for hosting an API *[snippet of krea.ai/krea-2-licensing, not fetched]*; a 50-seat
  limit in secondary posts, not in the agreement text seen.
- stable-diffusion.cpp runs it: `docs/krea2.md` (Raw and Turbo, safetensors and GGUF, `--llm` Qwen3-VL-4B,
  `--vae wan_2.1_vae`, `--offload-to-cpu`) *[page]*.
- Add-ons *[API, pages]*: `conradlocke/krea2-identity-edit` (918 likes; one photo of a person placed in a new scene,
  "Extremely improved likeness"; needs its own ComfyUI nodes; no depth or pose; V2 "free for personal and
  non-commercial use"); `thedeoxen/Krea-2-pose-controlnet` (Apache-2.0; a pose skeleton → the figure, appearance from
  the prompt, "not a reference + pose fusion model"); `Patil/Krea-2-depth-controlnet` (168 likes, 0 downloads — card
  not read); `inlineresearch/skin-lora-krea-2-raw` (a skin LoRA, its author's own test).
- Skin: reviews say Raw close-ups show pores and fine hairs (aiindigo); Kittl rates its skin realism below its other
  strengths; no controlled skin comparison with FLUX found *[snippets]*.

## Search log (WebSearch, standard mode)

1. "FLUX.3 Image Klein release" → braindetox, eesel, magica, runware, goenhance, poyo, tensor.art, orcarouter: launch
   2026-10-15, 5.6B, distilled 16 / base 50 steps, 10 references, boxes, 4K, Qwen3-VL-4B, FLUX Kommunity licence.
2. "FLUX 3 klein worse than FLUX.2 klein reddit" → eesel.ai reviews (several languages), orcarouter "vs flux 3"; no
   Reddit thread in the results; BFL's Elo claim; testers mixed.
3. "Krea 2 Turbo open weights" → aiweekly, comfyui-wiki, docs.comfy.org, civarchive, openrouter: weights and code
   2026-06-22; Turbo 8 steps, CFG 0, shift 1.15; licence reports conflict.
4. "FLUX.3 klein depth control LoRA reference image" → thedeoxen's refcontrol 9B depth and pose LoRAs, BFL's FLUX 3
   wiki, a krita-ai-diffusion discussion, the diffusers FLUX docs; no FLUX 3 depth LoRA.
5. "Krea 2 photorealism skin texture review vs FLUX" → a Krea 2 Raw skin LoRA, Kittl's review, gradually.ai arena pages
   (Krea 2 Large vs FLUX.2 pro / flex), aiindigo; no controlled skin test.
6. "stable-diffusion.cpp Krea 2 support" → leejet's `docs/krea2.md`, discussion #2151.
7. "Krea 2 Community License commercial use terms" → krea.ai's community and enterprise licence pages; the $1M cap.

Fetched: eesel.ai/blog/flux-3-klein; comfyui-wiki.com/models/krea/krea-2; stable-diffusion.cpp `docs/krea2.md`;
huggingface.co/krea/Krea-2-Turbo; github.com/black-forest-labs/flux-3-image-klein;
huggingface.co/conradlocke/krea2-identity-edit; huggingface.co/thedeoxen/Krea-2-pose-controlnet. HF API searches:
author thedeoxen; flux-3-image-klein; krea-2; krea-2-depth; krea2-depth; krea-2-controlnet; krea2-controlnet;
flux-3-image-klein-depth; flux-3-klein-lora; refcontrol.

## Gaps in this search

Not read: the FLUX Kommunity and Krea 2 licence files (gated / not fetched); Reddit itself (no thread surfaced); the
Patil Krea 2 depth ControlNet card. Not measured here: FLUX 3 Image Klein or Krea 2 on this card, or how either holds a
face to our head's shape.

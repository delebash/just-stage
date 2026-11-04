# Research — raising EEVEE's live-view quality for digital humans toward Unreal (2026-11-04)

> A research agent on the user's "any other way to make quality as good for live view as unreal, any plugins you can
> use or create your own from those examples?". Marks: [page] page read, [src] Blender source read, [API], [snip]
> search snippet, [meas] measured here (a background Blender listed properties; the card was busy, so nothing was
> rendered and no frame times were measured).

## 1 · Facts

**Settings we never changed (factory values, [meas]):** viewport samples 16; ray-tracing resolution 1/2 and Fast GI
resolution 1/2; Fast GI 2 rays x 8 steps; screen-trace precision 0.25; `trace_max_roughness` 0.5; anisotropic filtering
2x; overscan off. Surfaces rougher than `trace_max_roughness` get Fast GI instead of traced reflections [page] - our
skin's base roughness is √0.35 ≈ 0.59, so **its specular is never ray-traced** (the coat at 0.44 is).

**World light in EEVEE is indirect, in Cycles direct** (manual) [page]. A volume probe around the character baked for
visibility only (`capture_world` off, the world stays live) occludes the world under the chin, in the mouth, in the
ears and between the lips [API, page]; a GPU bake, redone after a shape or hair change. Light linking exists in EEVEE
since 4.3 [page]: a catch light on the cornea and tearline only (the face test's Cycles scene has one; the app none).

**Skin:** EEVEE's subsurface is screen-space Burley after Golubev (SIGGRAPH 2018) [src `eevee_subsurface.bsl.hh`] -
the same class as Unreal's screen-space Burley mode; Penner's pre-integrated skin (2011) and Jimenez's separable SSS
are weaker or the same class. A pull request noted EEVEE's transmittance energy higher than Cycles' [snip] -> a fitted
EEVEE-only scale, as the hair colour was. EEVEE has at most 3 closure bins (transmission / SSS takes bin 0, reflections
alternate between the other two) [src `eevee_nodetree_lib.bsl.hh`]: SSS plus two specular lobes stays clean, a fourth
closure turns stochastic. Unreal's dual specular defaults: lobes at 0.75x and 1.3x roughness, mixed 0.85 [snip].

**Eyes:** iris refraction by parallax - the view ray refracted at the cornea (IOR 1.376), intersected with the iris
plane at its depth, the iris UV offset, the limbus darkened at grazing angles - is the real-time standard: Jimenez (GDC
2013), Unreal's Eye shading model, Unity HDRP's Eye [page], Animal Logic's first approach (SIGGRAPH 2024) [page]; CC
Blender Tools makes Parallax its default EEVEE eye (docs only, page). Breaks past ~70° [snip]. An iris caustic per light
(refract L at the cornea, N·L on a concave iris normal) is Unity's "Eye Cinematic With Caustic" [page]. Our iris has no
lens depth today.

**Hair:** Unreal's real-time hair: a Marschner-family model with dual scattering, Deep Opacity Maps and voxelization for
transmittance [snip] - confirms rec 1. The image-light gap is EEVEE's indirect world light -> an explicit world
multiple-scatter term. Blender's hair closure (PR #164595) still an open prototype, last updated 2026-10-02 [API].
Blender 5.0's Cylinder curve shape ("better intersection in EEVEE") [page]. Add-ons (Tiny Hair Shader, paid; "EEVEE
Hair Anisotropy Pak", free, anisotropic sheen only) - references.

**Mouth:** a front-to-back darkening on teeth, gums and tongue by distance behind the lips (CC5's teeth shader has "Rear
AO" [snip]; MetaHuman exposes teeth, gum and plaque colours [snip]), on an EEVEE-only output; 5.1's Raycast node is
screen-space only [page].

**Cycles in the viewport, DLSS Ray Reconstruction (Blender 5.3):** 1 sample a frame reused over time with upscaling
[API, PR #153077]; no specular motion vectors (reflections suffer), no object motion in the viewport; the driver
minimum 620+ per the release notes, 590+ per the PR - **this machine has 610.88** [meas]; the DLSS library
(`nvngx_dlssd.dll`) must be in the app's path and the 5.3 beta doesn't ship it [meas]; its licence unread.

**Unreal live links:** Epic's "Send to Unreal" (MIT, pushed 2026-09-09 [API]) talks through Unreal's own
`remote_execution.py` and an RPC layer [API]; "Blender To Unreal Live Link" ($18: meshes, materials, textures; same
machine) [page]; PolyLink (paid, Blender 4.0-4.5) [snip]; Unreal's USD Stage reload often manual [snip]; Omniverse
live sync enterprise-only (forum) [snip].

## 2 · Query log

1 "how to make eevee look like unreal engine" (spam); 2 "blender eevee digital human realtime skin 2025 2026"
(Reallusion's bridge page, skin-shader products, Omniverse); 3 "blender 5 eevee raytracing settings quality light probe
volume character lighting" (the volume-probe manual, 5.0 notes); 4 "EEVEE Next subsurface scattering implementation
screen space Burley thickness shadow map translucency developer" (PR #107407: Golubev 2018); 5 "blender eevee screen
space subsurface scattering vs burley vs random walk skin comparison" (manual only); 6 "Unreal Engine eye shading model
iris normal cornea refraction caustic documentation" (Unreal forum, Unity HDRP Eye); 7 "Jimenez next generation
character rendering GDC 2013 eye refraction separable subsurface scattering slides" (GDC Vault; the 324 MB deck not
opened); 8 "eevee hair shader node group Kajiya-Kay Marschner realistic strands blender 4 5 free" (Tiny Hair Shader,
Anisotropy Pak); 9 "eevee addon realistic skin shader dual specular blender 4.2 5.0 eevee next" (Real Skin Shader V2,
GPL paid; a DAZ-importer threshold tip of 0.2); 10 "blender to unreal engine live link realtime mesh sync addon 2025";
11 "Send to Unreal blender addon Epic Games github license features" (MIT); 12 "realtime skin rendering technique 2025
2026 SIGGRAPH digital human" (nothing new); 13 "Unreal Engine subsurface profile dual specular roughness lobe mix Burley
normalized documentation" (0.75 / 1.3 / 0.85); 14 "realtime eye rendering cornea refraction iris parallax caustic shader
technique" (Animal Logic 2024, François 2009); 15 "real-time hair strands sub-pixel thin hair coverage widen strand
width opacity Frostbite Unreal groom rendering" (papers); 16 "Physically based hair shading in Unreal Karis 2016 multiple
scattering approximation dual scattering real time" (Unreal's 2020 hair blog); 17 "MetaHuman in Blender EEVEE materials
addon Poly Hammer meta-human DNA skin eyes hair shader" (editing tools only); 18 "CC Blender Tools Eevee Next settings
skin eye parallax refractive shader quality comparison Character Creator viewport" (its docs); 19 "MetaHuman eye material
parameters refraction depth scale iris UV radius limbus dark scale documentation"; 20 "MetaHuman teeth material mouth
cavity occlusion darkening gums shader parameters" (teeth properties, CC5 Rear AO); 21 "EEVEE hardware ray tracing
Vulkan ray query roadmap 2026 Blender developers blog" (Workbench shadows only); 22 PR #164595 status (by API); 23
"Omniverse Blender connector live sync deprecated 2025 OpenUSD live layer Unreal connector"; 24 "Unreal Engine USD stage
actor live reload layer file changed Blender USD workflow live"; 25 "eevee next realistic skin portrait settings
subsurface thickness raytracing tips 2025"; 26 "pre-integrated skin shading Penner curvature real-time vs screen space
subsurface quality"; 27 "dual lobe specular skin realtime two GGX lobes roughness 0.75 1.3 lobe mix 0.85 implementation";
28 "best tools for realistic characters in blender eevee 2026 human generator skin hair eyes" (Human Generator); 29
"blender eevee hair cards vs curves strands realistic realtime look comparison" (shop listings). Read: EEVEE release
notes 4.2-5.3, Cycles 5.2-5.3; manual pages (raytracing, limitations, nodes support, materials, world, probes, sampling,
curves); Blender source (SSS shader, closure binning, Principled, hair); Gitea PRs #164595, #153077; GitHub
BlenderTools; the Animal Logic talk, Unity's Eye reference, CC Blender Tools' eye and skin pages. 403: Blender's Python
API site, the developer docs, PR #107407's page, Unreal's hair blog.

## 3 · Not verified

Frame time and VRAM of every option; whether a higher trace threshold helps skin more than it adds noise; the DLSS
driver minimum and whether the option shows on 610.88; the DLSS library's licence; Jimenez's 2013 slides; Unreal's
Eye shading doc page; MetaHuman's teeth internals; how Real Skin Shader V2 and Human Generator look; whether Principled
plus a Glossy takes the two-reflection-bin path.

# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Face test, the skin base's raw material: the scans in use, one place for every step (scan_convert, scan_views,
scan_fit, scan_bake, skin_base). Each: its source file, its colour map per material (the importers keep glTF images
packed, so the files are named here; "*" for any other material, None = flat grey), whether its crown is bald skin
(a parser may call a bald crown hair), and its credit - every scan here is CC Attribution (licences read from
Sketchfab's API, `docs/plans/2026-11-02-research-texture-source.md`); credit them wherever their skin is used.
`sex` and `stubble` as seen at 1:1 (the research file's tables): skin_base.compose takes a character's pores from scans
of its sex first and keeps a stubbled scan's stubble only as far as the character's own stubble setting.
Kept: `docs/plans/2026-11-02-scan-skin-base.md` §3."""

S = "E:/Dev/3D/just-stage/.dev/downloads/scans/"
H = "E:/Dev/3D/just-stage/.dev/downloads/hsrd100/"  # HSRD-100: 16K studio scans of whole bodies (rec 2)
OUT = "E:/Dev/3D/just-stage/.dev/facetest/scans/"

SCANS = {
    "scan02": {
        "source": S + "head_scan_02/x/source/scene_optimized.gltf",
        "textures": {
            "Eyebrow_board": S + "head_scan_02/x/textures/Eyebrow_board_baseColor_5.png",
            "shirt_low": S + "head_scan_02/x/textures/head_scan_02_photogammertry_shirt_9.png",
            "*": S + "head_scan_02/x/textures/head_scan_02_photogammetry_diffuse_3.png",
        },
        "bald": True,
        "sex": "m",
        "stubble": True,
        # its glTF stores V upward, against the glTF spec (V down): read the spec's way, 21.5% of the skin's
        # triangles land on the map's black, flipped 0.6% (measured 2026-11-02; trimesh's reading needed the same)
        "flip_v": True,
        "credit": '"Head scan 02 (Optimized PBR)" by Cratera Games, scan by yaro.pro - '
        "sketchfab.com/3d-models/2f1978b43032415c8fdf911c7acfb1a4 (CC BY 4.0)",
    },
    "lps": {
        "source": S + "lee_perry_smith/x/src7z/head.obj",
        "textures": {"*": S + "lee_perry_smith/x/src7z/lambertian.jpg"},
        "bald": False,
        "sex": "m",
        "stubble": True,
        "credit": '"Infinite, 3D Head Scan" by Lee Perry-Smith, CC BY 3.0, based on a work at www.triplegangers.com '
        '(Sketchfab upload "Head (Lee Perry Smith)" by Paul) - sketchfab.com/3d-models/4d07eb2030db4406bc7eee971d1d3a97',
    },
    "yaro13": {
        "source": S + "yaro13/x/source/5.fbx",
        "textures": {"*": S + "yaro13/x/textures/texture_0_baseColor.png"},
        "bald": False,
        "sex": "m",
        "stubble": True,
        "credit": '"Head scan 13 (photogrammetry)" by yaro.pro - sketchfab.com/3d-models/5e6d2804405449e6b3bd96cd12d8b1ab '
        "(CC BY)",
    },
    "rudavin": {
        "source": S + "rudavin/x/src/Rudavin_portrat_retop.obj",
        "textures": {"*": S + "rudavin/x/src/Rudavin_portrat_retop_u1_v1.jpg"},
        "bald": False,
        "sex": "m",
        "stubble": True,
        "credit": '"Rudavin Sergey 3d portrait" by rudavin - sketchfab.com/3d-models/e1fe86107058409c9fb88b50f5ef80fd (CC BY)',
    },
    "female_wnmb": {
        "source": S + "female_whynotmeebaby/x/src/FEMALE.obj",
        "textures": {"*": S + "female_whynotmeebaby/x/src/FEMALE.jpg"},
        "bald": False,
        "sex": "f",
        "stubble": False,
        "credit": '"Female head scan" by whynotmeebaby - sketchfab.com/3d-models/b157e28076484a3f9f4f41b5e0f70770 (CC BY)',
    },
    "head03a": {
        "source": S + "head03a/x/src/HEAD 03 A.obj",
        "textures": {
            "HEAD_03_A": S + "head03a/x/src/HEAD 03 A.jpg",
            "HEAD_03_A1": S + "head03a/x/src/HEAD 03 A1.jpg",
            "HEAD_03_A2": S + "head03a/x/src/HEAD 03 A2.jpg",
            "*": None,
        },
        "bald": False,
        "sex": "f",
        "stubble": False,
        "credit": '"Head 03 A" by Nikitos & 3130 (@vrcityphoto) - sketchfab.com/3d-models/04a94494d88d48d18c46b82c7ab7c7b8 '
        "(CC BY)",
    },
    "ammamma": {
        "source": S + "ammamma/x/source/raw.glb",
        "textures": {"*": S + "ammamma/x/textures/gltf_embedded_0.jpeg"},
        "bald": False,
        "sex": "f",
        "stubble": False,
        "flip_v": True,  # Polycam's GLB, like scan02's glTF: renders scrambled read the spec's way (2026-11-02)
        "credit": '"Ammamma Head Scan Polycam" by Krishna Prakash - sketchfab.com/3d-models/64fda4f6914d40b89bc07a9f5927357e '
        "(CC BY)",
    },
    "portrait_3130": {
        "source": S + "portrait_3130/x/src/portrait of female model.obj",
        "textures": {"*": S + "portrait_3130/x/src/portrait of female model.1001.jpg"},
        "bald": False,
        "sex": "f",
        "stubble": False,
        "credit": '"portrait of model 2.0" by 3130 - sketchfab.com/3d-models/6832a653f9c647aba01f77b5d774e9ba (CC BY)',
    },
    "d3d_african_woman": {
        "source": S + "d3d_african_woman/x/src/050F_05SET_03SHOT.obj",
        "textures": {"*": S + "d3d_african_woman/x/textures/050F_05SET_03SHOT_Diffuse.jpg"},
        "bald": False,
        "sex": "f",
        "stubble": False,
        "credit": '"FREE DOWNLOAD: Attractive African woman 236" by deep3dstudio - '
        "sketchfab.com/3d-models/f2c29b6947f34237a0bfdc777120ef28 (CC BY)",
    },
    "d3d_african_man": {
        "source": S + "d3d_african_man/x/src/031M_04SET_01SHOT.obj",
        "textures": {"*": S + "d3d_african_man/x/textures/031M_04SET_01SHOT_Diffuse.jpg"},
        "bald": False,
        "sex": "m",
        "stubble": True,
        "credit": '"FREE DOWNLOAD Athletic African man walking 223" by deep3dstudio - '
        "sketchfab.com/3d-models/f9a8e3b108f04e998815593f78f163b1 (CC BY)",
    },
    "rp_carla": {
        "source": S + "rp_carla/x/source/rp_carla_rigged_001_yup_a.fbx",
        "textures": {"*": S + "rp_carla/x/textures/rp_carla_rigged_001_dif.jpeg"},
        "bald": False,
        "sex": "f",
        "stubble": False,
        "credit": '"Carla Rigged 001 - Rigged 3D Business Women" by Renderpeople - '
        "sketchfab.com/3d-models/acf520f450d14dd799f98a6fede3edf5 (CC BY)",
    },
    "hsr0015": {
        # Female, Hispanic, 23, Type 2 - White Skin; expression Neutral
        "source": H + "HSR0015-Body-035/x/HSR0015-Body-035_LOD0.obj",
        "textures": {"*": H + "HSR0015-Body-035/x/HSR0015-Body-035_LOD0_u0_v0_diffuse.png"},
        "up": "Z",  # its OBJ: Z up, metres (measured 2026-11-05)
        "bald": False,
        "sex": "f",
        "stubble": False,
        "credit": '"HSR0015-Body-035" from HSRD-100 by Digital Reality Lab - huggingface.co/datasets/digitalrealitylab/HSRD-100 '
        "(CC BY 4.0)",
    },
    "hsr0023": {
        # Male, Hispanic, 62, Type 2 - White Skin; expression Neutral
        "source": H + "HSR0023-Body-077/x/HSR0023-Body-077_LOD0.obj",
        "textures": {"*": H + "HSR0023-Body-077/x/HSR0023-Body-077_LOD0_u0_v0_diffuse.png"},
        "up": "Z",  # its OBJ: Z up, metres (measured 2026-11-05)
        "bald": False,
        "sex": "m",
        "stubble": False,
        "credit": '"HSR0023-Body-077" from HSRD-100 by Digital Reality Lab - huggingface.co/datasets/digitalrealitylab/HSRD-100 '
        "(CC BY 4.0)",
    },
    "hsr0027": {
        # Female, Caucasian, 41, Type 2 - White Skin; expression Neutral
        "source": H + "HSR0027-Body-068/x/HSR0027-Body-068_LOD0.obj",
        "textures": {"*": H + "HSR0027-Body-068/x/HSR0027-Body-068_LOD0_u0_v0_diffuse.png"},
        "up": "Z",  # its OBJ: Z up, metres (measured 2026-11-05)
        "bald": False,
        "sex": "f",
        "stubble": False,
        "credit": '"HSR0027-Body-068" from HSRD-100 by Digital Reality Lab - huggingface.co/datasets/digitalrealitylab/HSRD-100 '
        "(CC BY 4.0)",
    },
    "hsr0028": {
        # Female, Asian, 21, Type 2 - White Skin; expression Neutral
        "source": H + "HSR0028-Body-093/x/HSR0028-Body-093_LOD0.obj",
        "textures": {"*": H + "HSR0028-Body-093/x/HSR0028-Body-093_LOD0_u0_v0_diffuse.png"},
        "up": "Z",  # its OBJ: Z up, metres (measured 2026-11-05)
        "bald": False,
        "sex": "f",
        "stubble": False,
        "credit": '"HSR0028-Body-093" from HSRD-100 by Digital Reality Lab - huggingface.co/datasets/digitalrealitylab/HSRD-100 '
        "(CC BY 4.0)",
    },
    "hsr0040": {
        # Male, Caucasian, 50, Type 3 - Light Brown Skin; expression Neutral
        "source": H + "HSR0040-Body-086/x/HSR0040-Body-086_LOD0.obj",
        "textures": {"*": H + "HSR0040-Body-086/x/HSR0040-Body-086_LOD0_u0_v0_diffuse.png"},
        "up": "Z",  # its OBJ: Z up, metres (measured 2026-11-05)
        "bald": False,
        "sex": "m",
        "stubble": False,
        "credit": '"HSR0040-Body-086" from HSRD-100 by Digital Reality Lab - huggingface.co/datasets/digitalrealitylab/HSRD-100 '
        "(CC BY 4.0)",
    },
    "hsr0042": {
        # Male, African, 24, Type 5 - Dark Brown Skin; expression Neutral
        "source": H + "HSR0042-Body-018/x/HSR0042-Body-018_LOD0.obj",
        "textures": {"*": H + "HSR0042-Body-018/x/HSR0042-Body-018_LOD0_u0_v0_diffuse.png"},
        "up": "Z",  # its OBJ: Z up, metres (measured 2026-11-05)
        "bald": False,
        "sex": "m",
        "stubble": False,
        "credit": '"HSR0042-Body-018" from HSRD-100 by Digital Reality Lab - huggingface.co/datasets/digitalrealitylab/HSRD-100 '
        "(CC BY 4.0)",
    },
    "hsr0081": {
        # Female, 25, Type 3 - Light Brown Skin; expression Neutral. Its record says "Sex": "Male", "Ethnicity": "Asian",
        # but the same record's "AltID01" is "HSR0081-25-F-H", its alias "Sharon", and the scan is a woman in a skirt and
        # heels with long hair (its colour map, seen 2026-11-09) - the record's sex field is wrong; tagged by the scan
        "source": H + "HSR0081-Body-054/x/HSR0081-Body-054_LOD0.obj",
        "textures": {"*": H + "HSR0081-Body-054/x/HSR0081-Body-054_LOD0_u0_v0_diffuse.png"},
        "up": "Z",  # its OBJ: Z up, metres (measured 2026-11-05)
        "bald": False,
        "sex": "f",
        "stubble": False,
        "credit": '"HSR0081-Body-054" from HSRD-100 by Digital Reality Lab - huggingface.co/datasets/digitalrealitylab/HSRD-100 '
        "(CC BY 4.0)",
    },
    "hsr0102": {
        # Female, African, 22, Type 5 - Dark Brown Skin; expression Neutral
        "source": H + "HSR0102-Body-052/x/HSR0102-Body-052_LOD0.obj",
        "textures": {"*": H + "HSR0102-Body-052/x/HSR0102-Body-052_LOD0_u0_v0_diffuse.png"},
        "up": "Z",  # its OBJ: Z up, metres (measured 2026-11-05)
        "bald": False,
        "sex": "f",
        "stubble": False,
        "credit": '"HSR0102-Body-052" from HSRD-100 by Digital Reality Lab - huggingface.co/datasets/digitalrealitylab/HSRD-100 '
        "(CC BY 4.0)",
    },
    "hsr0112": {
        # Female, Caucasian, 60, Type 2 - White Skin; expression Neutral
        "source": H + "HSR0112-Body-074/x/HSR0112-Body-074_LOD0.obj",
        "textures": {"*": H + "HSR0112-Body-074/x/HSR0112-Body-074_LOD0_u0_v0_diffuse.png"},
        "up": "Z",  # its OBJ: Z up, metres (measured 2026-11-05)
        "bald": False,
        "sex": "f",
        "stubble": False,
        "credit": '"HSR0112-Body-074" from HSRD-100 by Digital Reality Lab - huggingface.co/datasets/digitalrealitylab/HSRD-100 '
        "(CC BY 4.0)",
    },
    "hsr0161": {
        # Male, African, 64, Type 5 - Dark Brown Skin; expression Smile
        "source": H + "HSR0161-Body-002/x/HSR0161-Body-002_LOD0.obj",
        "textures": {"*": H + "HSR0161-Body-002/x/HSR0161-Body-002_LOD0_u0_v0_diffuse.png"},
        "up": "Z",  # its OBJ: Z up, metres (measured 2026-11-05)
        "bald": False,
        "sex": "m",
        "stubble": False,
        "credit": '"HSR0161-Body-002" from HSRD-100 by Digital Reality Lab - huggingface.co/datasets/digitalrealitylab/HSRD-100 '
        "(CC BY 4.0)",
    },
}


def reference(name: str):
    """The head a scan's fit was made on: the copy its fit kept (scan_fit.py), else the current round's export. The
    round's head changes when the face test renders another character (2026-11-05: the clay pictures and the old export
    30 mm apart, so HSR0040's pairs landed off it), so each scan's later steps (scan_bake.py, scan_skin.py) read the head
    it was fitted to."""
    from pathlib import Path

    own = Path(OUT) / name / "head_export.npz"
    return own if own.exists() else Path(OUT) / "head_export.npz"


#: HUTUBS (TU Berlin's HRTF database, CC BY 4.0): 58 heads' 3D meshes, SHAPE ONLY (no colour) - for their ears (the
#: plan's Q-EAR-1: real ears as the mixer's identities - the outline's variety; the concha's pit is hm08's topology,
#: 2026-11-10). Each PLY Z up, X forward, the origin between the ear canals (read 2026-11-10); the subjects' sex is not
#: in the mesh files ("u"); run the route only to the fit (no bake, skin or layers: a layers.npz would put a grey scan
#: into every composition's fill)
HUTUBS = "E:/Dev/3D/just-stage/.dev/downloads/hf_samples/hutubs_meshes/3D head meshes/"
for _ply in sorted(__import__("pathlib").Path(HUTUBS).glob("pp*_3DheadMesh.ply")):
    _pp = _ply.name.split("_")[0]
    SCANS[f"hutubs_{_pp}"] = {
        "source": str(_ply).replace("\\", "/"), "textures": {"*": None}, "up": "Z", "upright": True, "shape_only": True,
        "bald": True,
        "sex": "u", "stubble": False,
        "credit": f'"HUTUBS - Head-related Transfer Function Database of the TU Berlin", {_pp} head mesh (CC BY 4.0)',
    }


def texture_for(scan: dict, material: str):
    """The colour map of one material: by name (Blender may add .001 to repeated names), else the "*" entry."""
    tex = scan["textures"]
    base = material.split(".")[0]
    return tex.get(material, tex.get(base, tex.get("*")))

# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Face test, the skin base's raw material: the scans in use, one place for every step (scan_convert, scan_views,
scan_fit, scan_bake, skin_base). Each: its source file, its colour map per material (the importers keep glTF images
packed, so the files are named here; "*" for any other material, None = flat grey), whether its crown is bald skin
(a parser may call a bald crown hair), and its credit - every scan here is CC Attribution (licences read from
Sketchfab's API, `docs/plans/2026-11-02-research-texture-source.md`); credit them wherever their skin is used.
Kept: `docs/plans/2026-11-02-scan-skin-base.md` §3."""

S = "E:/Dev/3D/just-stage/.dev/downloads/scans/"
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
        "credit": '"Infinite, 3D Head Scan" by Lee Perry-Smith, CC BY 3.0, based on a work at www.triplegangers.com '
        '(Sketchfab upload "Head (Lee Perry Smith)" by Paul) - sketchfab.com/3d-models/4d07eb2030db4406bc7eee971d1d3a97',
    },
    "yaro13": {
        "source": S + "yaro13/x/source/5.fbx",
        "textures": {"*": S + "yaro13/x/textures/texture_0_baseColor.png"},
        "bald": False,
        "credit": '"Head scan 13 (photogrammetry)" by yaro.pro - sketchfab.com/3d-models/5e6d2804405449e6b3bd96cd12d8b1ab '
        "(CC BY)",
    },
    "rudavin": {
        "source": S + "rudavin/x/src/Rudavin_portrat_retop.obj",
        "textures": {"*": S + "rudavin/x/src/Rudavin_portrat_retop_u1_v1.jpg"},
        "bald": False,
        "credit": '"Rudavin Sergey 3d portrait" by rudavin - sketchfab.com/3d-models/e1fe86107058409c9fb88b50f5ef80fd (CC BY)',
    },
    "female_wnmb": {
        "source": S + "female_whynotmeebaby/x/src/FEMALE.obj",
        "textures": {"*": S + "female_whynotmeebaby/x/src/FEMALE.jpg"},
        "bald": False,
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
        "credit": '"Head 03 A" by Nikitos & 3130 (@vrcityphoto) - sketchfab.com/3d-models/04a94494d88d48d18c46b82c7ab7c7b8 '
        "(CC BY)",
    },
    "ammamma": {
        "source": S + "ammamma/x/source/raw.glb",
        "textures": {"*": S + "ammamma/x/textures/gltf_embedded_0.jpeg"},
        "bald": False,
        "flip_v": True,  # Polycam's GLB, like scan02's glTF: renders scrambled read the spec's way (2026-11-02)
        "credit": '"Ammamma Head Scan Polycam" by Krishna Prakash - sketchfab.com/3d-models/64fda4f6914d40b89bc07a9f5927357e '
        "(CC BY)",
    },
    "portrait_3130": {
        "source": S + "portrait_3130/x/src/portrait of female model.obj",
        "textures": {"*": S + "portrait_3130/x/src/portrait of female model.1001.jpg"},
        "bald": False,
        "credit": '"portrait of model 2.0" by 3130 - sketchfab.com/3d-models/6832a653f9c647aba01f77b5d774e9ba (CC BY)',
    },
    "d3d_african_woman": {
        "source": S + "d3d_african_woman/x/src/050F_05SET_03SHOT.obj",
        "textures": {"*": S + "d3d_african_woman/x/textures/050F_05SET_03SHOT_Diffuse.jpg"},
        "bald": False,
        "credit": '"FREE DOWNLOAD: Attractive African woman 236" by deep3dstudio - '
        "sketchfab.com/3d-models/f2c29b6947f34237a0bfdc777120ef28 (CC BY)",
    },
    "d3d_african_man": {
        "source": S + "d3d_african_man/x/src/031M_04SET_01SHOT.obj",
        "textures": {"*": S + "d3d_african_man/x/textures/031M_04SET_01SHOT_Diffuse.jpg"},
        "bald": False,
        "credit": '"FREE DOWNLOAD Athletic African man walking 223" by deep3dstudio - '
        "sketchfab.com/3d-models/f9a8e3b108f04e998815593f78f163b1 (CC BY)",
    },
    "rp_carla": {
        "source": S + "rp_carla/x/source/rp_carla_rigged_001_yup_a.fbx",
        "textures": {"*": S + "rp_carla/x/textures/rp_carla_rigged_001_dif.jpeg"},
        "bald": False,
        "credit": '"Carla Rigged 001 - Rigged 3D Business Women" by Renderpeople - '
        "sketchfab.com/3d-models/acf520f450d14dd799f98a6fede3edf5 (CC BY)",
    },
}


def texture_for(scan: dict, material: str):
    """The colour map of one material: by name (Blender may add .001 to repeated names), else the "*" entry."""
    tex = scan["textures"]
    base = material.split(".")[0]
    return tex.get(material, tex.get(base, tex.get("*")))

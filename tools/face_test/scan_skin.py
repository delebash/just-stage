# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Face test, the skin base's raw material, step 7: which of the baked texels are the scanned person's SKIN - not
hair, brows, eyes, lips, teeth, clothes. NOT STANDARD (approved by name, TASKS "THE SCAN ROUTE" (5)): the industry
paints this mask by hand; this is Pixels2Points' published 2D baseline (Eurographics 2025: multi-view 2D parsing lifted
onto the scan) in our code. The parser: SegFace (AAAI 2025; code and weights MIT; ConvNeXt 512 trained on
CelebAMask-HQ - non-commercial data, a label - mean F1 89.22, its README's best there), run on every scan view
(scan_views.py), its 19 classes as its dataset code prepares them (RGB, 512 bicubic, ImageNet normalisation). The
votes go straight into OUR layout the face test's projection way (core/uv_projection.py): each texel of our wrapped
head (scan_fit.py) projected into each view, counted only where the view's position picture shows that same point
(within 4 mm - not hidden), weighted by how squarely the view sees it. Skin = skin, neck, nose, ears; a bald scan's
"hair" counts as skin (a parser may call a bald crown hair - scan_list's flag).

Writes scans/NAME/skin.png (HeadTile, 2048², the share of skin votes; 0 where no view saw it), colour.png (skin and
lips), normals.npy (our fitted head's normal per texel) and parse_*.png (each view's labels, for checking).
Run (the RealDenseFace environment; processor): .dev/venv-rdf/Scripts/python -I
tools/face_test/scan_skin.py NAME
"""

import importlib.util
import json
import sys
from pathlib import Path

import cv2
import numpy as np
import torch
import torch.nn.functional as F

ROOT = Path("E:/Dev/3D/just-stage")
SCANS = ROOT / ".dev/facetest/scans"
SEGFACE_REPO = ROOT / ".dev/cache/src/SegFace"  # 9416628, MIT
WEIGHTS = ROOT / ".dev/cache/segface/convnext_celeba_512_model_299.pt"  # sha256 3cd535bf... (Hugging Face LFS oid)
CLASSES = ["background", "neck", "skin", "cloth", "l_ear", "r_ear", "l_brow", "r_brow", "l_eye", "r_eye", "nose",
           "mouth", "l_lip", "u_lip", "hair", "eye_g", "hat", "ear_r", "neck_l"]  # its CelebAMaskHQ list (inference.py)
SKIN = ["neck", "skin", "nose", "l_ear", "r_ear"]
#: the colour mask adds the lips (skin_base.split's broad layer: the face's regional colour, lips included)
LIPS = ["l_lip", "u_lip"]
RES = 2048
HIDDEN = 0.004  # m (ours): a texel farther than this from the point the view shows there is hidden from it


def _module(name, path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


scan_list = _module("scan_list", Path(__file__).with_name("scan_list.py"))
up = _module("up", ROOT / "extension/juststage/core/uv_projection.py")


def load_segface():
    sys.path.insert(0, str(SEGFACE_REPO))
    import torchvision  # noqa: E402

    from network.models import segface_celeb  # noqa: E402

    # its start weights (torchvision's ImageNet ConvNeXt) are replaced by the checkpoint: don't download them
    segface_celeb.convnext_base = lambda pretrained=True: torchvision.models.convnext_base(weights=None)
    model = segface_celeb.SegFaceCeleb(512, "convnext_base")
    state = torch.load(WEIGHTS, map_location="cpu", weights_only=True)
    model.load_state_dict(state["state_dict_backbone"])
    return model.eval()


def parse(model, rgb):
    """Per-pixel class probabilities (H x W x 19) for one RGB picture."""
    h, w = rgb.shape[:2]
    x = cv2.resize(rgb, (512, 512), interpolation=cv2.INTER_CUBIC).astype(np.float32) / 255.0
    x = (x - np.array([0.485, 0.456, 0.406], np.float32)) / np.array([0.229, 0.224, 0.225], np.float32)
    x = torch.from_numpy(x).permute(2, 0, 1)[None]
    with torch.no_grad():
        logits = model(x, None, None)
        prob = F.interpolate(logits, size=(h, w), mode="bilinear", align_corners=False).softmax(1)
    return prob[0].permute(1, 2, 0).numpy()


def vertex_normals(v, f):
    fn = np.cross(v[f[:, 1]] - v[f[:, 0]], v[f[:, 2]] - v[f[:, 0]])
    vn = np.zeros_like(v)
    for k in range(3):
        np.add.at(vn, f[:, k], fn)
    return vn / np.maximum(np.linalg.norm(vn, axis=1, keepdims=True), 1e-12)


def colourise(labels):
    rng = np.random.default_rng(7)
    lut = rng.integers(40, 255, (len(CLASSES), 3)).astype(np.uint8)
    lut[0] = 0
    lut[CLASSES.index("skin")] = (150, 180, 230)
    lut[CLASSES.index("hair")] = (20, 60, 120)
    return lut[labels]


def main(name):
    out = SCANS / name
    scan = scan_list.SCANS[name]
    model = load_segface()
    E = np.load(scan_list.reference(name))
    Fz = np.load(out / "fit.npz")
    used, fitted, M = Fz["used"], Fz["fitted"], Fz["placement"]
    remap = -np.ones(len(E["co"]), dtype=np.int64)
    remap[used] = np.arange(len(used))
    tris = remap[E["tris"]]
    normals = vertex_normals(fitted, tris)
    (pts, nrm), covered = up.raster_uv(E["tri_uv"], [fitted[tris].astype(np.float32), normals[tris].astype(np.float32)],
                                       RES)
    p, n = pts[covered].astype(np.float64), nrm[covered].astype(np.float64)
    # into the scan's own frame (its views' cameras): the placement undone
    A, t = M[:3, :3], M[:3, 3]
    scale = float(np.cbrt(np.linalg.det(A)))
    Ainv = np.linalg.inv(A)
    p_s = (p - t) @ Ainv.T
    n_s = n @ (A / scale).T  # a rotation's inverse transpose is itself (scale taken out)
    n_s /= np.maximum(np.linalg.norm(n_s, axis=1, keepdims=True), 1e-12)

    views = json.loads((out / "views.json").read_text())["cams"]
    skin_acc, lips_acc, w_acc = np.zeros(len(p)), np.zeros(len(p)), np.zeros(len(p))
    for label, cam in views.items():
        rgba = cv2.imread(str(out / f"view_{label}.png"), cv2.IMREAD_UNCHANGED)[..., [2, 1, 0, 3]].astype(np.float32)
        a = rgba[..., 3:] / 255.0
        rgb = (rgba[..., :3] * a + 128.0 * (1 - a)).astype(np.uint8)
        prob = parse(model, rgb)
        cv2.imwrite(str(out / f"parse_{label}.png"), colourise(prob.argmax(-1))[..., ::-1])
        skin = prob[..., [CLASSES.index(c) for c in SKIN]].sum(-1)
        if scan.get("bald"):
            skin = skin + prob[..., CLASSES.index("hair")]
        pos = np.load(out / f"pos_{label}.npy")
        Mc = np.asarray(cam["matrix_world"])
        right, upv, back, origin = Mc[:3, 0], Mc[:3, 1], Mc[:3, 2], Mc[:3, 3]
        span, size = cam["ortho_scale"], cam["size"]
        d = p_s - origin
        col = (d @ right / span + 0.5) * size - 0.5
        row = (0.5 - d @ upv / span) * size - 0.5
        inside = (col >= 0) & (col <= size - 1) & (row >= 0) & (row <= size - 1)
        ci, ri = np.clip(np.round(col).astype(int), 0, size - 1), np.clip(np.round(row).astype(int), 0, size - 1)
        shown = pos[ri, ci, :3]
        seen = inside & (pos[ri, ci, 3] > 0.5) & (np.linalg.norm(shown - p_s, axis=1) * scale < HIDDEN)
        w = np.where(seen, np.clip(n_s @ back, 0.0, 1.0) ** 2, 0.0)
        skin_acc += w * up.sample(skin[..., None].astype(np.float32), col, row)[:, 0]
        lips = prob[..., [CLASSES.index(c) for c in LIPS]].sum(-1)
        lips_acc += w * up.sample(lips[..., None].astype(np.float32), col, row)[:, 0]
        w_acc += w
        print(f"{name} {label}: sees {seen.mean():.1%} of our texels")
    share = np.where(w_acc > 0, skin_acc / np.maximum(w_acc, 1e-12), 0.0)
    img = np.zeros((RES, RES), np.uint8)
    img[covered] = np.clip(share * 255, 0, 255).astype(np.uint8)
    cv2.imwrite(str(out / "skin.png"), img)
    colour = np.zeros((RES, RES), np.uint8)
    colour[covered] = np.clip((share + np.where(w_acc > 0, lips_acc / np.maximum(w_acc, 1e-12), 0.0)) * 255, 0, 255)
    cv2.imwrite(str(out / "colour.png"), colour)
    # our fitted head's normals per texel (its own frame, as the bake sees it): skin_base.split's shading fit
    normals = np.zeros((RES, RES, 3), np.float16)
    normals[covered] = n.astype(np.float16)
    np.save(out / "normals.npy", normals)
    print(f"{name}: seen {np.mean(w_acc > 0):.1%} of our texels, skin there {np.mean(share[w_acc > 0] > 0.5):.1%}")


if __name__ == "__main__":
    main(sys.argv[1])

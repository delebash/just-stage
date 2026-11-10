# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Face test, the skin base's raw material, step 1: a downloaded scan (FBX, OBJ, glTF / GLB) read by Blender's own
importers - which bring every format to Blender's frame (Z up, metres as the file states them) - and written as plain
arrays for the fit outside Blender: world vertex positions, triangles, each triangle's corner UVs (v up, Blender's),
its material, and each material's image file as the importer found it.

Run: blender -b --factory-startup --python tools/face_test/scan_convert.py -- NAME   (a key of scan_list.SCANS;
writes .dev/facetest/scans/NAME/src.npz)
"""

import importlib.util
import json
import sys
from pathlib import Path

import bpy
import numpy as np

_spec = importlib.util.spec_from_file_location("scan_list", str(Path(__file__).with_name("scan_list.py")))
scan_list = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(scan_list)


def load(path: Path, up: str = "Y"):
    """`up`: the file's own up axis where it isn't the format's convention (HSRD-100's OBJs are Z up)."""
    ext = path.suffix.lower()
    if ext == ".fbx":
        bpy.ops.import_scene.fbx(filepath=str(path))
    elif ext == ".obj" and up == "Z":
        bpy.ops.wm.obj_import(filepath=str(path), forward_axis="Y", up_axis="Z")
    elif ext == ".obj":
        bpy.ops.wm.obj_import(filepath=str(path))
    elif ext in (".glb", ".gltf"):
        bpy.ops.import_scene.gltf(filepath=str(path))
    elif ext == ".ply":  # HUTUBS's heads (Z up, X forward - the scan route's upright step finds the face)
        bpy.ops.wm.ply_import(filepath=str(path), forward_axis="Y", up_axis=up)
    else:
        raise SystemExit(f"unsupported {ext}")


def image_of(material):
    """The first image texture feeding the material (the base colour, on these scans' one-image materials)."""
    if material is None or not material.use_nodes:
        return ""
    for node in material.node_tree.nodes:
        if node.type == "TEX_IMAGE" and node.image is not None:
            return bpy.path.abspath(node.image.filepath) or node.image.name
    return ""


def main(argv):
    src = Path(scan_list.SCANS[argv[0]]["source"])
    out = Path(scan_list.OUT) / argv[0] / "src.npz"
    out.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    load(src, scan_list.SCANS[argv[0]].get("up", "Y"))
    dg = bpy.context.evaluated_depsgraph_get()
    cos, tris, uvs, mats, names = [], [], [], [], []
    mat_index = {}
    offset = 0
    for ob in bpy.context.scene.objects:
        if ob.type != "MESH":
            continue
        ev = ob.evaluated_get(dg)
        mesh = ev.to_mesh()
        mesh.calc_loop_triangles()
        nt = len(mesh.loop_triangles)
        if nt and not mesh.uv_layers and scan_list.SCANS[argv[0]].get("shape_only"):
            mesh.uv_layers.new(name="none")  # a shape-only scan (no colour): every UV 0, the views flat grey
        if nt == 0 or not mesh.uv_layers:
            print(f"skipped {ob.name}: {nt} triangles, {len(mesh.uv_layers)} UV layers")
            ev.to_mesh_clear()
            continue
        nv = len(mesh.vertices)
        co = np.empty(nv * 3, np.float32)
        mesh.vertices.foreach_get("co", co)
        mw = np.array(ob.matrix_world)
        co = co.reshape(-1, 3) @ mw[:3, :3].T.astype(np.float32) + mw[:3, 3].astype(np.float32)
        verts = np.empty(nt * 3, np.int64)
        loops = np.empty(nt * 3, np.int64)
        mi = np.empty(nt, np.int64)
        mesh.loop_triangles.foreach_get("vertices", verts)
        mesh.loop_triangles.foreach_get("loops", loops)
        mesh.loop_triangles.foreach_get("material_index", mi)
        uv = np.empty(len(mesh.loops) * 2, np.float32)
        layer = mesh.uv_layers.active or mesh.uv_layers[0]
        layer.data.foreach_get("uv", uv)
        uv = uv.reshape(-1, 2)
        slot_global = []
        for slot in ob.material_slots or [None]:
            m = slot.material if slot is not None else None
            key = m.name if m is not None else ""
            if key not in mat_index:
                mat_index[key] = len(names)
                names.append({"name": key, "image": image_of(m)})
            slot_global.append(mat_index[key])
        cos.append(co)
        tris.append(verts.reshape(-1, 3) + offset)
        uvs.append(uv[loops].reshape(-1, 3, 2))
        mats.append(np.asarray(slot_global)[np.clip(mi, 0, len(slot_global) - 1)])
        offset += nv
        print(f"{ob.name}: {nv} vertices, {nt} triangles, UV layer {layer.name}")
        ev.to_mesh_clear()
    co = np.concatenate(cos)
    tri_uv = np.concatenate(uvs)
    if scan_list.SCANS[argv[0]].get("flip_v"):  # a file that breaks its format's V convention (scan_list says which)
        tri_uv[..., 1] = 1.0 - tri_uv[..., 1]
    np.savez(out, co=co, tris=np.concatenate(tris).astype(np.int32), tri_uv=tri_uv,
             tri_mat=np.concatenate(mats).astype(np.int16), materials=json.dumps(names))
    lo, hi = co.min(0), co.max(0)
    print(f"wrote {out}: {len(co)} vertices, {offset and sum(len(t) for t in tris)} triangles; bounds {lo} .. {hi}; "
          f"materials {names}")


if __name__ == "__main__":
    main(sys.argv[sys.argv.index("--") + 1:])

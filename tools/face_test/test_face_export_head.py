"""Export the round scene's head as the projection sees it (evaluated mesh, triangles, HeadTile UVs) and the eyes'
centres, for fitting a scanned head onto it outside Blender."""

import bpy
import numpy as np

DIR = "E:/Dev/3D/just-stage/.dev/facetest/"
FADE_FROM = 1.30


def test_export_head():
    bpy.ops.wm.open_mainfile(filepath=DIR + "round.blend")
    body = bpy.data.objects["Face"]
    dg = bpy.context.evaluated_depsgraph_get()
    ev = body.evaluated_get(dg)
    mesh = ev.to_mesh()
    mesh.calc_loop_triangles()
    nt = len(mesh.loop_triangles)
    loops = np.empty(nt * 3, dtype=np.int64)
    verts = np.empty(nt * 3, dtype=np.int64)
    mesh.loop_triangles.foreach_get("loops", loops)
    mesh.loop_triangles.foreach_get("vertices", verts)
    loops, verts = loops.reshape(-1, 3), verts.reshape(-1, 3)
    co = np.empty(len(mesh.vertices) * 3, dtype=np.float32)
    mesh.vertices.foreach_get("co", co)
    co = co.reshape(-1, 3)
    uvs = np.empty(len(mesh.loops) * 2, dtype=np.float32)
    mesh.uv_layers["HeadTile"].data.foreach_get("uv", uvs)
    uvs = uvs.reshape(-1, 2)
    ev.to_mesh_clear()
    mw = np.array(body.matrix_world)
    co = co @ mw[:3, :3].T + mw[:3, 3]
    head = (co[verts][:, :, 2] > FADE_FROM).all(axis=1)
    eyes = {}
    for n in ("Face.eyeLeft", "Face.eyeRight"):
        e = bpy.data.objects[n]
        m = np.array(e.matrix_world)
        p = np.array([v.co for v in e.data.vertices]) @ m[:3, :3].T + m[:3, 3]
        eyes[n] = (p.min(axis=0) + p.max(axis=0)) / 2
    np.savez(
        "E:/Dev/3D/just-stage/.dev/facetest/scans/head_export.npz",
        co=co,
        tris=verts[head],
        tri_uv=uvs[loops[head]],
        eye_left=eyes["Face.eyeLeft"],
        eye_right=eyes["Face.eyeRight"],
    )
    print("exported", int(head.sum()), "head triangles of", nt, "; eyes", eyes)

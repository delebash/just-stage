# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The gate's body rig (the plan's §18a row 17, a LOCAL TEST in the gate): our character posed on the product's own
skeleton (`modules/rig/skeleton.py`, `juststage.rig.add_skeleton`: the spec's 82 UE5-named bones on MPFB2's CC0
placement and weights - until 2026-11-08 this file placed MPFB2's 53-bone game-engine rig itself), and both men posed
alike - each limb aimed at one world direction - for the gate's posed views (`parts_gate.POSES`): do our mesh and
weights pose like CC5's HD Aaron, as exported to Blender (his 90 deform bones with twist and share bones, no body
correctives)? The body correctives (body.dna) are Q-RIG-7."""

from __future__ import annotations

import importlib

import bpy
import numpy as np
from mathutils import Matrix, Vector

#: the gate's bone roles in each rig (ours the spec's UE5 names, his CC5's) - the right side, as the gate's views
ROLES = {
    "ours": {"upperarm": "upperarm_r", "lowerarm": "lowerarm_r", "hand": "hand_r", "thigh": "thigh_r",
             "calf": "calf_r", "foot": "foot_r", "spine": "spine_02",
             "twist_near": "lowerarm_twist_02_r", "twist_far": "lowerarm_twist_01_r"},
    "cc5": {"upperarm": "CC_Base_R_Upperarm", "lowerarm": "CC_Base_R_Forearm", "hand": "CC_Base_R_Hand",
            "thigh": "CC_Base_R_Thigh", "calf": "CC_Base_R_Calf", "foot": "CC_Base_R_Foot", "spine": "CC_Base_Spine02",
            "twist_near": "CC_Base_R_ForearmTwist01", "twist_far": "CC_Base_R_ForearmTwist02"},
}  # fmt: skip
#: a limb's direction is joint to joint - its bone's head to the next joint's: a CC5 bone's tail, set on FBX import by
#: convention, doesn't lie along the limb (aimed by head-to-tail, his forearm, calf and thigh barely turned,
#: 2026-11-08); MPFB2's tails sit on the next joint, so ours is unchanged
NEXT = {"upperarm": "lowerarm", "lowerarm": "hand", "thigh": "calf", "calf": "foot"}


def _ext(name: str):
    return importlib.import_module(f"bl_ext.system.juststage.{name}")


def build(body: bpy.types.Object) -> bpy.types.Object:
    """Our character's skeleton - the one it has, or the product's command run on it; returns the armature object."""
    skeleton = _ext("modules.rig.skeleton")
    arm = skeleton.skeleton_of(body)
    if arm is None:
        made = _ext("api").run("juststage.rig.add_skeleton", character=body.juststage.character_id)
        arm = bpy.data.objects[made.object]
    print(f"BODY RIG: {len(arm.data.bones)} bones ({arm.name})", flush=True)
    return arm


def rest(arm: bpy.types.Object) -> None:
    for pb in arm.pose.bones:
        pb.matrix_basis = Matrix.Identity(4)
    bpy.context.view_layer.update()


def turn(arm: bpy.types.Object, bone: str, axis, degrees: float) -> None:
    """`bone` turned `degrees` about a world `axis` through its head (its children follow)."""
    pb = arm.pose.bones[bone]
    to_arm = arm.matrix_world.inverted()
    head = pb.head.copy()  # armature space
    a = (to_arm.to_3x3() @ Vector(axis)).normalized()
    r = Matrix.Translation(head) @ Matrix.Rotation(np.radians(degrees), 4, a) @ Matrix.Translation(-head)
    pb.matrix = r @ pb.matrix
    bpy.context.view_layer.update()


def direction(arm: bpy.types.Object, bone: str) -> np.ndarray:
    """A posed bone's world direction, head to tail."""
    pb = arm.pose.bones[bone]
    d = arm.matrix_world.to_3x3() @ (pb.tail - pb.head)
    return np.array(d.normalized())


def limb(arm: bpy.types.Object, roles: dict, role: str) -> np.ndarray:
    """A posed limb's world direction, joint to joint (`NEXT`); a role with no next joint, its bone's head to tail."""
    if role not in NEXT:
        return direction(arm, roles[role])
    d = np.array(joint(arm, roles[NEXT[role]]) - joint(arm, roles[role]))
    return d / np.linalg.norm(d)


def joint(arm: bpy.types.Object, bone: str) -> Vector:
    """A posed bone's head in world space."""
    return arm.matrix_world @ arm.pose.bones[bone].head


def _place(arm: bpy.types.Object, body: bpy.types.Object, group: str, near: str, far: str) -> float:
    """Where a bone's weights sit along a limb, from bone `near`'s head (0) to bone `far`'s (1): the weighted centroid
    of its vertex group, all at rest - the shaped body (shape keys mixed: ours is shaped by them) against the bones'
    rest heads (a posed limb against rest vertices read nonsense, 2026-11-08)."""
    co = _ext("modules.body.build").shaped_coords(body)
    co = co @ np.array(body.matrix_world)[:3, :3].T + np.array(body.matrix_world)[:3, 3]
    a, b = (np.array(arm.matrix_world @ arm.data.bones[n].head_local) for n in (near, far))
    vg = body.vertex_groups[group]
    index, weight = [], []
    for v in body.data.vertices:
        for g in v.groups:
            if g.group == vg.index and g.weight > 0:
                index.append(v.index)
                weight.append(g.weight)
    w = np.asarray(weight)
    c = (co[index] * w[:, None]).sum(0) / w.sum()
    return float((c - a) @ (b - a) / ((b - a) @ (b - a)))


def twist(arm: bpy.types.Object, body: bpy.types.Object, roles: dict, degrees: float) -> dict:
    """The hand turned `degrees` about the forearm (elbow to wrist) and each forearm twist bone by the share of it its
    weights' place along the forearm gives - one rule for both rigs (ours: two twist bones at the thirds, children of
    the forearm; his: one at the elbow and its child half way). Our body.dna's twist layer will turn ours; his own
    rig drives his in CC5. Returns each twist bone's share."""
    elbow, wrist = np.array(joint(arm, roles["lowerarm"])), np.array(joint(arm, roles["hand"]))
    axis = (wrist - elbow) / np.linalg.norm(wrist - elbow)
    shares = {}
    for key in ("twist_near", "twist_far"):
        shares[roles[key]] = min(max(_place(arm, body, roles[key], roles["lowerarm"], roles["hand"]), 0.0), 1.0)
    near, far = roles["twist_near"], roles["twist_far"]
    turn(arm, near, axis, shares[near] * degrees)
    inherited = shares[near] * degrees if arm.pose.bones[far].parent.name == near else 0.0
    turn(arm, far, axis, shares[far] * degrees - inherited)
    turn(arm, roles["hand"], axis, degrees)
    return shares

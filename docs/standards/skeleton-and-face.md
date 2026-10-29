# Skeleton, face and correctives — the standards and every mapping table

> **Status: APPROVED recs, written 2026-10-29** (the review's items 1, 2, 3, 9, 10, 17, 22, 26 — TASKS; review file
> [`../plans/2026-10-29-spec-review-opus.md`](../plans/2026-10-29-spec-review-opus.md)). R9, R18. Facts: RESEARCH §2,
> §5, §8; the bone lists measured from the user's Unreal files are in RESEARCH §8 and
> `../plans/2026-10-29-spec-evidence/`.

## 1 · The body skeleton: the UE5 skeleton, by its own names

**Structure and names are Epic's UE5 Mannequin skeleton**, measured from `SKM_Manny_Simple.uasset` (RESEARCH §8): 80
deform bones — the published count of 89 minus 9 non-deform helpers. CC5 aligned its skeleton to it and renames to it
on export (§2); Daz's bridges map Genesis onto it (§8); MetaHuman's body uses the same names (§8). JustStage uses the
names **verbatim inside Blender** — Blender's naming page lists `_ . -` and space separators with "lower or upper case
'L', 'R', 'left' or 'right'", so `thigh_l`/`thigh_r` mirror and flip. A character reaches Unreal with no renaming.
Standard: Epic's skeleton (§8); [Blender bone naming](https://docs.blender.org/manual/en/5.3/animation/armatures/bones/editing/naming.html).

**Built on MakeHuman's own UE-named rig** (item 3): MPFB2's `rig.game_engine.json` has 53 bones in UE4-Mannequin names
(`pelvis`, `spine_01–03`, `neck_01`, `clavicle_l`, `upperarm_l`, `lowerarm_l`, `hand_l`, fingers `_01–_03`, `thigh_l`,
`calf_l`, `foot_l`, `ball_l`) with `weights.game_engine.json` (§5). JustStage's rig is that rig extended by the 27 bones
UE5 adds (`spine_04/05`, `neck_02`, twists, metacarpals), in the same format — MPFB2's rig JSON v110
([`rig.md`](https://github.com/makehumancommunity/mpfb2/blob/master/docs/fileformats/rig.md)) — as
`data/rigs/ue5.json` with `data/rigs/weights.ue5.json`. **Every bone's head and tail is placed by MPFB2's `CUBE`
strategy**: the mean of a named joint cube's vertices (e.g. `"cube_name": "joint-l-foot-1"`), which every morph moves —
so the skeleton follows the body as sliders change it (item 2). Added bones get their own joint-cube rules and weights.

### 1.1 Deform bones

| Chain | Bones | Count | Source |
|---|---|---|---|
| Root and centre | `root`, `pelvis`, `spine_01`–`spine_05`, `neck_01`, `neck_02`, `head` | 10 | Manny |
| Arm (per side, `_l`/`_r`) | `clavicle`, `upperarm`, `upperarm_twist_01`, `upperarm_twist_02`, `lowerarm`, `lowerarm_twist_01`, `lowerarm_twist_02`, `hand` | 8 × 2 | Manny |
| Hand (per side) | `thumb_01`–`thumb_03`; `index_metacarpal`, `index_01`–`index_03`; `middle_metacarpal`, `middle_01`–`_03`; `ring_metacarpal`, `ring_01`–`_03`; `pinky_metacarpal`, `pinky_01`–`_03` | 19 × 2 | Manny |
| Leg (per side) | `thigh`, `thigh_twist_01`, `thigh_twist_02`, `calf`, `calf_twist_01`, `calf_twist_02`, `foot`, `ball` | 8 × 2 | Manny |
| Secondary (per side) | `breast` | 1 × 2 | ours, in Epic's style (MPFB2 ships `game_engine_with_breast`; Manny has none) |

Face joints are the DNA face rig's, by MetaHuman's names (§2.3) — `FACIAL_C_FacialRoot`, `FACIAL_L_Eye`, `FACIAL_R_Eye`,
`FACIAL_C_Jaw`, `FACIAL_C_TeethUpper`, `FACIAL_C_TeethLower`, `FACIAL_C_Tongue1`–`4` and the rest — mirrored into the
body armature where Blender's animation tools need to key them.

Rules: `root` sits at the origin on the floor and carries root motion; `pelvis` is the retarget pelvis; the rest pose
is the A-pose of [`character-data-model.md`](character-data-model.md) §1.1; every deform bone is in the `DEF` bone
collection; control rigs (Rigify-generated or our own) add `MCH-`/`CTRL-` bones that are never exported. Manny's 9
non-deform helpers (`ik_foot_root`, `ik_foot_l/r`, `ik_hand_root`, `ik_hand_gun`, `ik_hand_l/r`, `interaction`,
`center_of_mass`) are added by the Unreal export preset. Corrective bones (§3) use the names of `SK_Mannequin`'s 72
corrective bones where they do the same job.

**Creatures** (item 22) have their own skeletons: Mesh2Motion's CC0 rigs (birds, dragons, spiders, kaiju, foxes,
horses, fish, snakes — each with CC0 animations, item 28) imported as armature templates and fitted to the creature's
mesh, or Rigify's creature metarigs (basic quadruped, bird, cat, horse, shark, wolf — on disk in Blender 5.3,
`rigify/metarigs/`), with Blender's automatic weights; none of the tables below applies to them
([`character-data-model.md`](character-data-model.md) §1.0). Mesh2Motion's code (a TypeScript web app) is a method
reference for fitting a skeleton into a mesh, not code we reuse.

### 1.2 The humanoid role map

Every deform bone maps to at most one **humanoid role**; roles use the VRM 1.0 vocabulary (55 bones, 15 required),
which Godot's `SkeletonProfileHumanoid` shares and Unity's `HumanBodyBones` shares except at the thumb (§8). Required:
`hips`, `spine`, `head`, both `upperLeg`, `lowerLeg`, `foot`, `upperArm`, `lowerArm`, `hand`. Rules quoted:
"Humanoid bones must be unique in VRM"; "upperChest can exist only when chest exists"; scale "MUST have positive values".

| JustStage (UE5 name) | VRM 1.0 role | Unity `HumanBodyBones` | Godot profile |
|---|---|---|---|
| `pelvis` | `hips` | `Hips` | `Hips` |
| `spine_01` | `spine` | `Spine` | `Spine` |
| `spine_03` | `chest` | `Chest` | `Chest` |
| `spine_05` | `upperChest` | `UpperChest` | `UpperChest` |
| `neck_01` | `neck` | `Neck` | `Neck` |
| `head` | `head` | `Head` | `Head` |
| `FACIAL_L_Eye` / `FACIAL_R_Eye` | `leftEye` / `rightEye` | `LeftEye` / `RightEye` | `LeftEye` / `RightEye` |
| `FACIAL_C_Jaw` | `jaw` | `Jaw` | `Jaw` |
| `clavicle_l` | `leftShoulder` | `LeftShoulder` | `LeftShoulder` |
| `upperarm_l` | `leftUpperArm` | `LeftUpperArm` | `LeftUpperArm` |
| `lowerarm_l` | `leftLowerArm` | `LeftLowerArm` | `LeftLowerArm` |
| `hand_l` | `leftHand` | `LeftHand` | `LeftHand` |
| `thumb_01_l` / `_02` / `_03` | `leftThumbMetacarpal` / `Proximal` / `Distal` | `LeftThumbProximal` / `Intermediate` / `Distal` | `LeftThumbMetacarpal` / `Proximal` / `Distal` |
| `index_01_l` / `_02` / `_03` | `leftIndexProximal` / `Intermediate` / `Distal` | same | same |
| `middle_*`, `ring_*`, `pinky_*` | `leftMiddle*`, `leftRing*`, `leftLittle*` | `LeftMiddle*`, `LeftRing*`, `LeftLittle*` | same as VRM, PascalCase |
| `thigh_l` | `leftUpperLeg` | `LeftUpperLeg` | `LeftUpperLeg` |
| `calf_l` | `leftLowerLeg` | `LeftLowerLeg` | `LeftLowerLeg` |
| `foot_l` | `leftFoot` | `LeftFoot` | `LeftFoot` |
| `ball_l` | `leftToes` | `LeftToes` | `LeftToes` |
| `spine_02`, `spine_04`, `neck_02`, twists, metacarpals (other than the thumb's), `breast`, other face joints | — (non-humanoid nodes; VRM allows them between humanoid bones) | — | — |

Sources: [VRM humanoid](https://github.com/vrm-c/vrm-specification/blob/master/specification/VRMC_vrm-1.0/humanoid.md),
[Unity HumanBodyBones](https://docs.unity.com/en-us/engine/current/script-reference/unityengine/humanbodybones),
[Godot SkeletonProfileHumanoid](https://docs.godotengine.org/en/stable/classes/class_skeletonprofilehumanoid.html).
Unity's `Proximal` = VRM's `Metacarpal` for the thumb is the standards note's inference (§8); the Unity preset test
proves it on import.

### 1.3 Unreal (UE5 Mannequin and MetaHuman body)

Identical names, so the Unreal preset renames nothing. Measured (RESEARCH §8; `ue5-mannequin-bones.json`):
`SKM_Manny_Simple` has exactly **89** names — the 80 deform bones plus the 9 helpers; the full `SK_Mannequin` has
**161** — the same 89 plus 72 corrective bones (`*_correctiveRoot_*`, `*_twistCor_0N_*`, `thigh_fwd/bck/in/out`,
`calf_knee/kneeBack`, `upperarm_fwd/bck/in/out/bicep/tricep`, `lowerarm_fwd/bck/in/out`, `wrist_inner/outer`,
`ankle_fwd/bck`, `clavicle_pec/out/scap`, `spine_04_latissimus`, `weapon`).

The Unreal plugin keeps **its own skeleton asset** and lists `SK_Mannequin` and the MetaHuman body skeleton as
**compatible skeletons**, so Epic's, Fab's and MetaHuman body animations play on JustStage characters without
retargeting (Unreal's Compatible Skeletons — the Skeletons page and the Python API's `Skeleton` class, §8; item 12).
The user's own `SK_Mannequin` is never modified. Proportions differ per character — Unreal's translation retargeting
settings handle that, as across MetaHuman body types.

### 1.4 HumanIK, Mixamo, Daz and CC — the name tables (`data/skeletons/<source>.json`)

| JustStage (UE5 name) | HumanIK (MotionBuilder 2026) | Mixamo (`mixamorig:` + name) | Daz Genesis 9 | Daz Genesis 8 / 8.1 | CC3+ / CC4 (`CC_Base_` prefix) |
|---|---|---|---|---|---|
| `pelvis` | `Hips` | `Hips` | `hip` | `hip` | `Hip` (CC's `Pelvis` is a child of `Hip` carrying the legs; no UE5 bone) |
| `spine_01` | `Spine` | `Spine` | `spine1` | `abdomenLower` | `Waist` |
| `spine_02` | `Spine1` | — | `spine2` | `abdomenUpper` | — |
| `spine_03` | `Spine2` | `Spine1` | `spine3` | `chestLower` | `Spine01` |
| `spine_04` | `Spine3` | — | — | — | — |
| `spine_05` | `Spine4` | `Spine2` | `spine4` | `chestUpper` | `Spine02` |
| `neck_01` / `neck_02` | `Neck` / `Neck1` | `Neck` / — | `neck1` / `neck2` | `neckLower` / `neckUpper` | `NeckTwist01` / `NeckTwist02` |
| `head` | `Head` | `Head` | `head` | `head` | `Head` |
| `clavicle_l` | `LeftShoulder` | `LeftShoulder` | `l_shoulder` | `lCollar` | `L_Clavicle` |
| `upperarm_l` | `LeftArm` | `LeftArm` | `l_upperarm` | `lShldrBend` | `L_Upperarm` |
| `upperarm_twist_01_l` / `_02` | `LeftArmRoll` (leaf roll bones) | — | `l_upperarmtwist1` / `2` | `lShldrTwist` / — | `L_UpperarmTwist01` / `02` |
| `lowerarm_l` | `LeftForeArm` | `LeftForeArm` | `l_forearm` | `lForearmBend` | `L_Forearm` |
| `lowerarm_twist_01_l` / `_02` | `LeftForeArmRoll` | — | `l_forearmtwist1` / `2` | `lForearmTwist` / — | `L_ForearmTwist01` / `02` |
| `hand_l` | `LeftHand` | `LeftHand` | `l_hand` | `lHand` | `L_Hand` |
| `thumb_01_l`–`_03` | `LeftHandThumb1`–`3` | `LeftHandThumb1`–`3` | `l_thumb1`–`3` | `lThumb1`–`3` | `L_Thumb1`–`3` |
| `index_metacarpal_l` | `LeftInHandIndex` | — | `l_indexmetacarpal` | `lCarpal1` | — |
| `index_01_l`–`_03` | `LeftHandIndex1`–`3` | `LeftHandIndex1`–`3` | `l_index1`–`3` | `lIndex1`–`3` | `L_Index1`–`3` |
| `middle_metacarpal_l`, `middle_01`–`_03` | `LeftInHandMiddle`, `LeftHandMiddle1`–`3` | `LeftHandMiddle1`–`3` | `l_midmetacarpal`, `l_mid1`–`3` | `lCarpal2`, `lMid1`–`3` | `L_Mid1`–`3` |
| `ring_metacarpal_l`, `ring_01`–`_03` | `LeftInHandRing`, `LeftHandRing1`–`3` | `LeftHandRing1`–`3` | `l_ringmetacarpal`, `l_ring1`–`3` | `lCarpal3`, `lRing1`–`3` | `L_Ring1`–`3` |
| `pinky_metacarpal_l`, `pinky_01`–`_03` | `LeftInHandPinky`, `LeftHandPinky1`–`3` | `LeftHandPinky1`–`3` | `l_pinkymetacarpal`, `l_pinky1`–`3` | `lCarpal4`, `lPinky1`–`3` | `L_Pinky1`–`3` |
| `thigh_l` | `LeftUpLeg` | `LeftUpLeg` | `l_thigh` | `lThighBend` | `L_Thigh` |
| `thigh_twist_01_l` / `_02` | `LeftUpLegRoll` | — | `l_thightwist1` / `2` | `lThighTwist` / — | `L_ThighTwist01` / `02` |
| `calf_l` | `LeftLeg` | `LeftLeg` | `l_shin` | `lShin` | `L_Calf` |
| `calf_twist_01_l` / `_02` | `LeftLegRoll` | — | — | — | `L_CalfTwist01` / `02` |
| `foot_l` | `LeftFoot` | `LeftFoot` | `l_foot` | `lFoot` | `L_Foot` |
| `ball_l` | `LeftToeBase` | `LeftToeBase` | `l_toes` (`l_metatarsal` between foot and toes) | `lToe` | `L_ToeBase` |
| `breast_l` | — | — | `l_pectoral` | `lPectoral` | `L_Breast` |
| `FACIAL_L_Eye` | — | — | (face bones; not in the bridge maps) | — | `L_Eye` |
| `FACIAL_C_Jaw`, `FACIAL_C_TeethUpper`, `FACIAL_C_TeethLower`, `FACIAL_C_Tongue1`–`3` | — | — | — | — | `JawRoot`, `UpperJaw`, `Teeth01`, `Teeth02`, `Tongue01`–`03` (under `FacialBone`) |

**Spine rule for sources with fewer spine bones:** one-to-one by humanoid role (§1.2) — `spine` → `spine_01`, `chest` →
`spine_03`, `upperChest` → `spine_05`. Mixamo: three-vrm's map (MIT) gives `mixamorigSpine` → spine, `Spine1` → chest,
`Spine2` → upperChest (§8). CC3+/CC4: Reallusion's own Blender tools (GPL, names only) put Rigify's `chest` control on
the bone that is `CC_Base_Spine01` (`rigify_mapping_data.py`: `spine.001` ↔ `CC_Base_Waist`, `spine.002` ↔
`CC_Base_Spine01`, `spine.003` ↔ `CC_Base_Spine02`, and `["ORG-spine.002", …, "chest", …]`), so `Waist` → spine,
`Spine01` → chest, `Spine02` → upperChest. (Reallusion's `GAME_BASE_BONE_MAPPING` puts the same three on UE4's
`spine_01`–`spine_03`, because UE4 has three spine bones; UE5 has five.)

Sources: HumanIK — the MotionBuilder 2026 help (§8); Mixamo — three-vrm's `mixamoVRMRigMap.js` (§8); Daz —
`g9_to_unreal_manny.json`, `g8_to_unreal.json` (byte-equal to Daz's source, evidence folder); CC — Reallusion's
`soupday/cc_blender_tools` (§2, §8). CC5 exports to Unreal already renamed to UE5 names (§2), so the CC5 importer takes
those files as they are and uses this column for `CC_Base_` files; the ten bones CC5 added are mapped from an actual
CC5 export at step 6. Right side: `_l` → `_r`, `Left` → `Right`, `l_` → `r_`, `l` → `r`, `L_` → `R_`.

The tables are JSON (`data/skeletons/<source>.json`) — the format Daz's bridge maps and MPFB2's rig files use; name
maps are not scene description (item 17).

### 1.5 Retargeting

- Imports **characterise** (CC's word; Unreal's IK Rig: a T/A retarget pose plus the role map) through a per-source
  **profile** (`data/profiles/<source>.json`: the column above, the source's rest pose, axes and units), with Godot's
  `BoneMapper` keyword behaviour (MIT, S9) as the fallback guess for unknown rigs.
- Export presets write the target's names, rest pose (T-pose for VRM, Unity, Mixamo; the source's own for Unreal),
  axes and units ([`interchange.md`](interchange.md) §1). Standard: CC5's "Target Tool Preset" pattern (§2).

## 2 · The face

### 2.1 The guaranteed interchange set: ARKit 52

Every JustStage human face has these 52 shape keys by exactly these names (Apple's
`ARFaceAnchor.BlendShapeLocation`; each 0.0–1.0; left and right are the face's own sides):

- Left eye (7): `eyeBlinkLeft`, `eyeLookDownLeft`, `eyeLookInLeft`, `eyeLookOutLeft`, `eyeLookUpLeft`, `eyeSquintLeft`, `eyeWideLeft`
- Right eye (7): `eyeBlinkRight`, `eyeLookDownRight`, `eyeLookInRight`, `eyeLookOutRight`, `eyeLookUpRight`, `eyeSquintRight`, `eyeWideRight`
- Mouth and jaw (27): `jawForward`, `jawLeft`, `jawRight`, `jawOpen`, `mouthClose`, `mouthFunnel`, `mouthPucker`, `mouthLeft`, `mouthRight`, `mouthSmileLeft`, `mouthSmileRight`, `mouthFrownLeft`, `mouthFrownRight`, `mouthDimpleLeft`, `mouthDimpleRight`, `mouthStretchLeft`, `mouthStretchRight`, `mouthRollLower`, `mouthRollUpper`, `mouthShrugLower`, `mouthShrugUpper`, `mouthPressLeft`, `mouthPressRight`, `mouthLowerDownLeft`, `mouthLowerDownRight`, `mouthUpperUpLeft`, `mouthUpperUpRight`
- Brows, cheeks, nose (10): `browDownLeft`, `browDownRight`, `browInnerUp`, `browOuterUpLeft`, `browOuterUpRight`, `cheekPuff`, `cheekSquintLeft`, `cheekSquintRight`, `noseSneerLeft`, `noseSneerRight`
- Tongue (1): `tongueOut`

**The first set is MakeHuman's** (item 3): the CC0 "Faceunits 01" pack (ARKit-style face units for hm08) and MPFB2's
`faceservice.py` `ARKIT_FACEUNITS` (the 52 names) — improved shapes replace them under the same names if the gate
(R3) judges them below the bar. Expressions are MPFB2's expression JSON (`format_version`, `name`, `face_units` keyed
by ARKit names, licence fields — [`expression.md`](https://github.com/makehumancommunity/mpfb2/blob/master/docs/fileformats/expression.md)).
Importers accept subsets: MediaPipe's 51 (no `tongueOut`), VRM's 18 presets, CC5's Standard profile. Standard:
[Apple ARKit](https://developer.apple.com/documentation/arkit/arfaceanchor/blendshapelocation).

### 2.2 Visemes

15 visemes by Meta's language-independent names, from MakeHuman's CC0 **"Visemes 02"** pack (MPFB2's `META_VISEMES`:
`viseme_aa`, `viseme_CH`, `viseme_DD`, `viseme_E`, `viseme_FF`, `viseme_I`, `viseme_kk`, `viseme_nn`, `viseme_O`,
`viseme_PP`, `viseme_RR`, `viseme_sil`, `viseme_SS`, `viseme_TH`, `viseme_U`); Microsoft's 22 from **"Visemes 01"**
(`MICROSOFT_VISEMES`) for Azure-style speech output (§5). CC5's 15 (`V_`-prefixed — §2) are mapped from CC5's manual
page at step 6; VRM's five (`aa`, `ih`, `ou`, `ee`, `oh`) are derived on export.
Standard: [Meta viseme reference](https://developers.meta.com/vr/documentation/unreal/audio-ovrlipsync-viseme-reference/).

### 2.3 The rig: DNA + RigLogic, by MetaHuman's names (N4, item 10 — APPROVED 2026-10-29)

- The face rig is a **DNA file** (`rig/face.dna`) with the four DNA layers (descriptor, definition, behaviour,
  geometry — §8), evaluated by **OpenRigLogic** (MIT; C++ with SWIG Python bindings for both DNA and RigLogic — §8):
  GUI controls → raw controls → corrective expressions, joint transforms, blend-shape weights and animated-map
  (wrinkle) weights. Standard: [OpenRigLogic](https://github.com/EpicGames/OpenRigLogic); its trademark file bars Epic's
  marks in our product name only — our rig is "based on OpenRigLogic".
- **Names are MetaHuman's** (the user: "your rec on all 1-6 … go" — item 10, an exception to AGENTS.md's clean-room
  rule, names only): the GUI controls by the names in MetaHuman's archetype `SKM_Face.dna` in the user's UE 5.8 (about
  420 channels, e.g. `CTRL_C_jaw`, `CTRL_L_mouth_cornerPull`, `CTRL_L_brow_lateral`, `CTRL_C_mouth_stickyU`,
  `CTRL_C_tongue_roll`), the face joints by its 373 `FACIAL_*` names where our rig has the same joint (§1.1), and the
  face meshes by its names where the part matches (`eyeLeft`, `eyeRight`, `eyeshell`, `eyelashes`, `eyeEdge`, `teeth`,
  `saliva`; MetaHuman's `head` region is part of our one body mesh). So MetaHuman Animator's curves and MetaHuman's
  tools drive a JustStage face with no mapping table. Every shape, joint position and weight stays ours. The control
  list lives in the DNA's definition layer, not in a file of ours (item 17).
- **ARKit 52 stays the guaranteed interchange set** (N4, approved: "fine that seems at least based on well known
  standard"): the 52 exist as plain shape keys beside the rig, and Live Link Face, MediaPipe and VMC drive them.
- **Wrinkles:** the DNA's animated maps — their weights come out of RigLogic and drive the material's `wrinkle.<i>`
  channels ([`character-data-model.md`](character-data-model.md) §3.1); built in step 4.
- **LODs:** the DNA carries per-LOD joint, blend-shape and map lists (MetaHuman's pattern, 8 head LODs — §8);
  JustStage generates LOD0–3 at first (step 4) and reserves 4–7.
- **Creatures** have no face rig and no ARKit set; their expressions are plain shape keys (item 22).

### 2.4 Interchange

| Target | What goes out | Standard |
|---|---|---|
| USD package | `UsdSkelBlendShape` for every shape key (with `normalOffsets` and in-betweens where used — §8); `rig/face.dna` and `rig/body.dna` beside it; animation resolved to joints and blend-shape weights in `UsdSkelAnimation` | UsdSkel |
| Unreal (plugin) | the DNA files → the plugin builds the RigLogic-driven skeletal mesh (MetaHuman's own runtime path); face animation as curves by the GUI control names; ARKit curves for Live Link Face | OpenRigLogic, Live Link |
| glTF / VRM | the 52 as morph targets with `extras.targetNames`; VRM `expressions` presets derived; visemes mapped to VRM's five; rig results baked into morph-weight animation | glTF 2.0, VRM 1.0 |
| FBX | the 52 (and, on request, every control's resolved shape) as blend shapes; rig results baked; the DNA files beside it, named in the sidecar | FBX via Blender's exporter |
| CC5 | the 52 by CC5's Standard-profile names (mapping at step 6 from CC5's slider table page) | — |

## 3 · Body correctives: the DNA's RBF and twist-swing layers (item 1; N5 replaced)

Correctives are the extra shapes and helper-joint moves that stop elbows, knees and shoulders collapsing when a joint
bends. **They live in a body DNA file, `rig/body.dna`, beside the face DNA** — MetaHuman's own split (head and body are
separate DNA files — RESEARCH §7):

- **Layers:** OpenRigLogic's `include/dna/layers/RBFBehaviorReader.h` (RBF poses → joint outputs, blend-shape channels
  and animated maps; solver types additive and interpolative; quaternion and twist-axis distances) and
  `TwistSwingBehaviorReader.h` (twist and swing setups → output joints with blend weights); written with
  `RBFBehaviorWriter` and `TwistSwingBehaviorWriter`; evaluated by `src/riglogic/rbf/` and
  `src/riglogic/joints/cpu/twistswing/` (§8). MetaHuman's archetype `body_head_combined.dna` in the user's UE 5.8 holds
  one RBF solver per body joint (`calf_l_UERBFSolver`, `clavicle_l_UERBFSolver`, `index_l_01_UERBFSolver`, …).
- **In Blender:** the extension evaluates `body.dna` with OpenRigLogic's Python bindings each time the pose changes and
  sets the corrective shape keys and corrective bones (named as `SK_Mannequin`'s, §1.1) — never hand-made drivers. The
  bindings are built per OS for Blender 5.3's Python 3.13 and shipped as the extension's `wheels`; OpenRigLogic
  publishes no wheels (§8).
- **In Unreal:** RigLogic evaluates the body DNA natively, as for a MetaHuman — the plugin builds no Control Rig node set.
- **Elsewhere** (glTF, FBX, other engines): the corrective shapes travel as ordinary blend shapes; the rule that turns
  them on from joint angles can't, so its result is baked into each animation as morph-weight curves (glTF animates
  morph weights; Daz's bridge rebuilds its `JointLinks` into an Unreal Anim Blueprint for the same reason — S9). CC5
  has no body correctives to send (§2).
- Deformation tools behind the shapes (Dem Bones BSD-3, complementary dynamics MIT, Jolt skinned soft bodies MIT —
  S10) are authoring choices, not format.

## 4 · Capture inputs (live) — item 26

Live capture is a stream, not a job, so it runs **inside Blender** (item 25's exception), in the Animate workspace
(R21's "later"), except R18's webcam face preview:

| Source | How it arrives | Names | Standard |
|---|---|---|---|
| Webcam (face and body) | MediaPipe in Blender's Python (Apache-2.0; 1.2.0 wheels for Windows, Apple-silicon Macs and Linux — none for Intel Macs, labelled there), the way BlendArMocap (GPL-3.0) "Run[s] Mediapipe within Blender" | ARKit 51 + pose landmarks → the role map | [MediaPipe](https://developers.google.com/edge/mediapipe/solutions/vision/face_landmarker) |
| Phone face (Epic's Live Link Face, iPhone; iPad and Android since UE 5.7) | its network stream, received as the open receiver `shun126/livelinkface_arkit_receiver` does (GPL-3.0; its code reused) | ARKit 52 | Epic's app; Epic publishes no wire format, so an app update can break it — VMC is the published door beside it |
| Every other device and app (SlimeVR, XR Animator, VSeeFace, Waidayo, …) | VMC protocol (OSC over UDP, ports 39539/39540) | `/VMC/Ext/Bone/Pos` with Unity `HumanBodyBones` names (→ role map), `/VMC/Ext/Blend/Val` with ARKit names | [VMC](https://protocol.vmc.info/english) (MIT) |
| Recorded takes | BVH, FBX, and Live Link Face's CSV recordings — imported as Blender actions | per profile | files |
| Unreal | Live Link, MetaHuman Animator (incl. 5.8's experimental one-camera body and face capture), Live Link devices — **now**, through the plugin, per R13 | ARKit curves, MetaHuman control names, our bone names | Unreal |

Live streams are not commands; they feed the pose and the face directly
([`commands-and-api.md`](commands-and-api.md) §5). Takes are recorded as Blender actions (slotted Actions — §8).

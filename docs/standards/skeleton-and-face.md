# Skeleton, face and correctives — the standards and every mapping table

> **Status: DRAFT, 2026-10-29 — for the user's approval** (see [`README.md`](README.md)). R9, R18. Facts: RESEARCH §2,
> §5, §8 and the S8/S9 notes; the bone maps and the UE5 Mannequin bone lists measured or fetched by this session on
> 2026-10-29 are in RESEARCH §8 and `../plans/2026-10-29-spec-evidence/`.

## 1 · The body skeleton: the UE5 skeleton, by its own names

**Structure and names are Epic's UE5 Mannequin skeleton**, measured from `SKM_Manny_Simple.uasset` in the user's UE 5.7
projects (RESEARCH §8): 80 deform bones — the published count of 89 minus 9 non-deform helpers. CC5 aligned its skeleton
to it ("ten additional bones … aligning CC bones with UE 5's key structures", §2) and renames to it on export; Daz's
bridges map Genesis onto it (§8); MetaHuman's body uses the same names (Epic's DNA page, §8 pass 2). JustStage uses the
names **verbatim inside Blender too** — Blender's symmetry tools accept them: its naming page lists the separators
`_ . -` and space with "lower or upper case 'L', 'R', 'left' or 'right'" ("hand.l to hand.r"), so `thigh_l`/`thigh_r`
mirror and flip (read 2026-10-29). A character therefore reaches Unreal with no renaming, which is the CC5 pipeline
feature users praise (§2).
Standard: Epic's skeleton as the converged commercial skeleton (§8); [Blender bone naming](https://docs.blender.org/manual/en/latest/animation/armatures/bones/editing/naming.html).
Bone names are a public interface documented by Epic and reproduced by Daz, CC and Mixamo guides; OpenRigLogic's
trademark notice covers product names only (§4).

### 1.1 Deform bones (90)

| Chain | Bones | Count | Source |
|---|---|---|---|
| Root and centre | `root`, `pelvis`, `spine_01`–`spine_05`, `neck_01`, `neck_02`, `head` | 10 | Manny |
| Arm (per side, `_l`/`_r`) | `clavicle`, `upperarm`, `upperarm_twist_01`, `upperarm_twist_02`, `lowerarm`, `lowerarm_twist_01`, `lowerarm_twist_02`, `hand` | 8 × 2 | Manny |
| Hand (per side) | `thumb_01`–`thumb_03`; `index_metacarpal`, `index_01`–`index_03`; `middle_metacarpal`, `middle_01`–`_03`; `ring_metacarpal`, `ring_01`–`_03`; `pinky_metacarpal`, `pinky_01`–`_03` | 19 × 2 | Manny |
| Leg (per side) | `thigh`, `thigh_twist_01`, `thigh_twist_02`, `calf`, `calf_twist_01`, `calf_twist_02`, `foot`, `ball` | 8 × 2 | Manny |
| Secondary (per side) | `breast` | 1 × 2 | ours, in Epic's style (CC has `L_Breast`; Manny has none) |
| Face anchors | `eye_l`, `eye_r`, `jaw`, `teeth_upper`, `teeth_lower`, `tongue_01`–`tongue_03` | 8 | ours; Manny has no face bones |

Rules: `root` sits at the origin on the floor and carries root motion; `pelvis` is the retarget pelvis; the rest pose
is the A-pose of [`character-data-model.md`](character-data-model.md) §1.1; every bone is in the `DEF` bone collection;
control rigs (Rigify-generated or our own) add `MCH-`/`CTRL-` bones that are never exported. Manny's 9 non-deform
helpers (`ik_foot_root`, `ik_foot_l/r`, `ik_hand_root`, `ik_hand_gun`, `ik_hand_l/r`, `interaction`, `center_of_mass`)
are not in the armature; the Unreal export preset adds them. Face volume joints (MetaHuman has 713 head joints at LOD0 —
§8 pass 2) are the face rig's, owned by the DNA file (§2). Individual toes (CC3+ has five per side — §2 pass 2) may be
added later as a `secondary` group.

### 1.2 The humanoid role map

Every deform bone maps to at most one **humanoid role**; roles use the VRM 1.0 vocabulary (55 bones, 15 required), which
Godot's `SkeletonProfileHumanoid` shares and Unity's `HumanBodyBones` shares except at the thumb (§8). The spec's bones,
verbatim from `humanoid.md` (fetched 2026-10-29): torso `hips`, `spine`, `chest`, `upperChest`, `neck`; head `head`,
`leftEye`, `rightEye`, `jaw`; legs `upperLeg`, `lowerLeg`, `foot`, `toes` per side; arms `shoulder`, `upperArm`,
`lowerArm`, `hand` per side; fingers `thumbMetacarpal`, `thumbProximal`, `thumbDistal`,
`{index,middle,ring,little}{Proximal,Intermediate,Distal}` per side. Required: `hips`, `spine`, `head`, both `upperLeg`,
`lowerLeg`, `foot`, `upperArm`, `lowerArm`, `hand`. Rules quoted: "Humanoid bones must be unique in VRM"; "upperChest can
exist only when chest exists"; scale "MUST have positive values".

| JustStage (UE5 name) | VRM 1.0 role | Unity `HumanBodyBones` | Godot profile |
|---|---|---|---|
| `pelvis` | `hips` | `Hips` | `Hips` |
| `spine_01` | `spine` | `Spine` | `Spine` |
| `spine_03` | `chest` | `Chest` | `Chest` |
| `spine_05` | `upperChest` | `UpperChest` | `UpperChest` |
| `neck_01` | `neck` | `Neck` | `Neck` |
| `head` | `head` | `Head` | `Head` |
| `eye_l` / `eye_r` | `leftEye` / `rightEye` | `LeftEye` / `RightEye` | `LeftEye` / `RightEye` |
| `jaw` | `jaw` | `Jaw` | `Jaw` |
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
| `spine_02`, `spine_04`, `neck_02`, twists, metacarpals (other than the thumb's), `breast`, teeth, tongue | — (non-humanoid nodes; VRM allows them between humanoid bones) | — | — |

Sources: [VRM humanoid](https://github.com/vrm-c/vrm-specification/blob/master/specification/VRMC_vrm-1.0/humanoid.md),
[Unity HumanBodyBones](https://docs.unity.com/en-us/engine/current/script-reference/unityengine/humanbodybones),
[Godot SkeletonProfileHumanoid](https://docs.godotengine.org/en/stable/classes/class_skeletonprofilehumanoid.html).
Unity's `Proximal` = VRM's `Metacarpal` for the thumb is the standards note's inference (§8); the Unity preset test
proves it on import.

### 1.3 Unreal (UE5 Mannequin and MetaHuman body)

Identical names, so the Unreal preset renames nothing. Measured 2026-10-29 (RESEARCH §8;
`../plans/2026-10-29-spec-evidence/ue5-mannequin-bones.json`): `SKM_Manny_Simple` has exactly **89** names — the 80
deform bones of §1.1 plus the 9 helpers; the full `SK_Mannequin` (5.7) has **161** — the same 89 plus 72 corrective
bones (`*_correctiveRoot_*`, `*_twistCor_0N_*`, `thigh_fwd/bck/in/out`, `thigh_fwd_lwr/bck_lwr`, `calf_knee/kneeBack`,
`upperarm_fwd/bck/in/out/bicep/tricep`, `lowerarm_fwd/bck/in/out`, `wrist_inner/outer`, `ankle_fwd/bck`,
`clavicle_pec/out/scap`, `spine_04_latissimus`, `weapon`). Neither has `metatarsal_*` or `pectoral_*` (Daz's bridge adds
those on its side). Epic's DNA page names the 30 body joints a face DNA must match (§8 pass 2); they are in the 161.

What the Unreal preset adds or maps: the 9 helpers (the IK bones constrained to `foot_*`/`hand_*`); `breast_l/r` kept as
extra bones or dropped (preset option); the face anchors become the DNA's facial joints by the DNA definition. The 72
corrective bones are Epic's RBF and twist setups; JustStage's own correctives (§3) export as corrective bones under our
names, and the "Send to Unreal as a MetaHuman" option (R12) lets Epic's pipeline build Epic's.

### 1.4 HumanIK, Mixamo, Daz and CC

| JustStage (UE5 name) | HumanIK (MotionBuilder 2026) | Mixamo (`mixamorig:` + HumanIK name) | Daz Genesis 9 | Daz Genesis 8 / 8.1 | CC3+ / CC4 (`CC_Base_` prefix) |
|---|---|---|---|---|---|
| `pelvis` | `Hips` | `mixamorig:Hips` | `hip` | `hip` | `Hip` (CC also has `Pelvis`, `Waist`) |
| `spine_01` | `Spine` | `Spine` | `spine1` | `abdomenLower` | `Spine01` |
| `spine_02` | `Spine1` | `Spine1` | `spine2` | `abdomenUpper` | `Spine02` |
| `spine_03` | `Spine2` | `Spine2` | `spine3` | `chestLower` | — |
| `spine_04` | `Spine3` | — | — | — | — |
| `spine_05` | `Spine4` | — | `spine4` | `chestUpper` | — |
| `neck_01` / `neck_02` | `Neck` / `Neck1` | `Neck` / — | `neck1` / `neck2` | `neckLower` / `neckUpper` | `NeckTwist01` / `NeckTwist02` |
| `head` | `Head` | `Head` | `head` | `head` | `Head` |
| `clavicle_l` | `LeftShoulder` | `LeftShoulder` | `l_shoulder` | `lCollar` | `L_Clavicle` |
| `upperarm_l` | `LeftArm` | `LeftArm` | `l_upperarm` | `lShldrBend` | `L_Upperarm` |
| `upperarm_twist_01_l` / `_02` | `LeftArmRoll` (leaf roll bones, up to five per limb) | — | `l_upperarmtwist1` / `2` | `lShldrTwist` / — | `L_UpperarmTwist01` / `02` |
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
| `eye_l` | — | — | (face bones; not in the bridge maps) | — | `L_Eye` |
| `jaw`, `teeth_upper`, `teeth_lower`, `tongue_01`–`_03` | — | — | — | — | `JawRoot`, `UpperJaw`, `Teeth01`, `Teeth02`, `Tongue01`–`03` (under `FacialBone`) |

Sources: HumanIK — the MotionBuilder 2026 help (15 required nodes, Spine1–9, Neck1–9, roll bones, InHand joints — §8
pass 2); Mixamo — three-vrm's `mixamoVRMRigMap.js` (HumanIK names with the `mixamorig` prefix; Thumb1 is the
metacarpal — §8 pass 2), Mixamo's own page is unreachable (403); Daz — `g9_to_unreal_manny.json`, `g8_to_unreal.json`
(fetched 2026-10-29; Daz's own target names are the UE5 names in the first column); CC — the 101-name reconstruction
from Reallusion's GPL add-on's string constants (§2 pass 2; names only). CC5 exports to Unreal already renamed to UE5
names (§2), so the CC5 importer takes those files as they are and uses this column for `CC_Base_` files; the ten bones
CC5 added are unpublished and get mapped from an actual CC5 export at step 6.

Right side: `_l` → `_r`, `Left` → `Right`, `l_` → `r_`, `l` → `r`, `L_` → `R_`.

### 1.5 Retargeting

- Imports **characterise** (CC's word, Unreal's IK Rig: a T/A retarget pose plus the role map) through a per-source
  **profile** (`data/profiles/<source>.usda`: the column above as a name map, the source's rest pose, axes and units),
  with Godot's `BoneMapper` keyword behaviour (MIT, S9 §3) as the fallback guess for unknown rigs.
- Export presets write the target's names, rest pose (T-pose for VRM, Unity, Mixamo; the source's own for Unreal),
  axes and units ([`interchange.md`](interchange.md) §1). Standard: CC5's "Target Tool Preset" pattern (§2); Unreal's
  retargeter matches chains by fuzzy name (§8).

## 2 · The face

### 2.1 The guaranteed interchange set: ARKit 52

Every JustStage face has these 52 shape keys by exactly these names (Apple's `ARFaceAnchor.BlendShapeLocation`,
fetched 2026-10-29; each 0.0–1.0; left and right are the face's own sides):

- Left eye (7): `eyeBlinkLeft`, `eyeLookDownLeft`, `eyeLookInLeft`, `eyeLookOutLeft`, `eyeLookUpLeft`, `eyeSquintLeft`, `eyeWideLeft`
- Right eye (7): `eyeBlinkRight`, `eyeLookDownRight`, `eyeLookInRight`, `eyeLookOutRight`, `eyeLookUpRight`, `eyeSquintRight`, `eyeWideRight`
- Mouth and jaw (27): `jawForward`, `jawLeft`, `jawRight`, `jawOpen`, `mouthClose`, `mouthFunnel`, `mouthPucker`, `mouthLeft`, `mouthRight`, `mouthSmileLeft`, `mouthSmileRight`, `mouthFrownLeft`, `mouthFrownRight`, `mouthDimpleLeft`, `mouthDimpleRight`, `mouthStretchLeft`, `mouthStretchRight`, `mouthRollLower`, `mouthRollUpper`, `mouthShrugLower`, `mouthShrugUpper`, `mouthPressLeft`, `mouthPressRight`, `mouthLowerDownLeft`, `mouthLowerDownRight`, `mouthUpperUpLeft`, `mouthUpperUpRight`
- Brows, cheeks, nose (10): `browDownLeft`, `browDownRight`, `browInnerUp`, `browOuterUpLeft`, `browOuterUpRight`, `cheekPuff`, `cheekSquintLeft`, `cheekSquintRight`, `noseSneerLeft`, `noseSneerRight`
- Tongue (1): `tongueOut`

Importers accept subsets: MediaPipe's 51 (no `tongueOut`, §8), VRM's 18 presets (§8), CC5's Standard profile (its
ARKit-compatible tier, §2). Standard: [Apple ARKit](https://developer.apple.com/documentation/arkit/arfaceanchor/blendshapelocation);
capture: [MediaPipe Face Landmarker](https://developers.google.com/edge/mediapipe/solutions/vision/face_landmarker) (Apache-2.0).

### 2.2 Visemes

15 visemes by Meta's language-independent names: `sil`, `PP`, `FF`, `TH`, `DD`, `kk`, `CH`, `SS`, `nn`, `RR`, `aa`,
`E`, `ih`, `oh`, `ou` (S10 §3c; carried today by `XR_META_face_tracking_visemes`). CC5 also has 15 (8 lip + 7 tongue
pairs, `V_`-prefixed — §2); the CC5 ↔ Meta mapping is filled from CC5's manual page at step 6 and recorded here. VRM's
five (`aa`, `ih`, `ou`, `ee`, `oh`) are derived on export.
Standard: [Meta viseme reference](https://developers.meta.com/vr/documentation/unreal/audio-ovrlipsync-viseme-reference/).

### 2.3 The rig: DNA + RigLogic, the control vocabulary (N4, approved 2026-10-29)

- The face rig is a **DNA file** (`rig/face.dna`) with the four DNA layers (descriptor, definition, behaviour,
  geometry — §8), evaluated by **OpenRigLogic** (MIT; C++ with Python bindings): GUI controls → raw controls →
  corrective (PSD) expressions, joint transforms, blend-shape weights and animated-map (wrinkle) weights. Standard:
  [OpenRigLogic](https://github.com/EpicGames/OpenRigLogic); the trademark file bars Epic's marks in our product name
  only (§4) — our rig is "based on OpenRigLogic".
- **Control vocabulary (N4 — the user: "fine that seems at least based on well known standard").** The GUI controls
  are the ARKit 52 names, plus JustStage's own controls for what ARKit lacks, named in the same camelCase style with
  the same left/right rule (e.g. `mouthStickyUpperLeft`, `lipCornerDepressLeft`, `eyeLidTightenRight`,
  `noseWrinkleLeft`, `browLateralLeft`, `tongueUp`, `tongueLeft`, `cheekRaiseLeft`, `jawChew`). The target size is CC5
  HD's class (262 expression + 128 corrective sliders — §2 pass 2), reached by the gate's rig-generation work (R5, S10
  §3g); the list is a data file (`data/face/controls.usda`) and the table here grows with it. Mapping tables to
  MetaHuman Animator curves (from the user's own MHA exports) and to CC5's HD sliders (from CC5's public slider table)
  are built at step 6.
- **Face joints** (eyes, jaw, teeth, tongue, and the volume joints the generated rig needs) are DNA joints; the eight
  anchors in §1.1 are mirrored into the body armature so Blender's animation tools can key them.
- **Wrinkle layers** are DNA animated maps: their weights come out of RigLogic and drive the material's
  `wrinkle.<i>` channels ([`character-data-model.md`](character-data-model.md) §3.1).
- **LODs:** the DNA carries per-LOD joint, blend-shape and map lists (MetaHuman's pattern, 8 head LODs — §8 pass 2);
  JustStage generates LOD0–3 at first (step 4) and reserves 4–7.

### 2.4 Interchange

| Target | What goes out | Standard |
|---|---|---|
| USD package | `UsdSkelBlendShape` for every shape key (with `normalOffsets` and in-betweens where used — §8 pass 2); the DNA file beside it; control curves in `UsdSkelAnimation.blendShapeWeights` for the ARKit 52, the rest as `JustStageLipsyncAPI`/`JustStageTakeAPI` attributes on the animation prim | UsdSkel |
| Unreal (plugin) | the DNA file → the plugin builds the RigLogic-driven skeletal mesh (MetaHuman's own runtime path); ARKit curves for Live Link Face | OpenRigLogic, Live Link |
| glTF / VRM | the 52 as morph targets with `extras.targetNames`; VRM `expressions` presets derived; visemes mapped to VRM's five | glTF 2.0, VRM 1.0 |
| FBX | the 52 (and, on request, every control's resolved shape) as blend shapes; `jawOpen` folds teeth and tongue (CC5's "mouth-open as morph" behaviour, §2) | FBX via Blender's exporter |
| CC5 | the 52 by CC5's Standard-profile names (mapping table at step 6 from CC5's slider table page) | — |

## 3 · Body correctives (N5, approved 2026-10-29) — on USD's applied-schema mechanism

No open format carries joint-driven correctives (S9: Daz JCMs, MetaHuman RBF, CC HD correctives cross only in
sidecars). **N5 — the user: "ok".** The *fields* are JustStage's; the *carrier* is a USD applied API schema,
`JustStageCorrectiveAPI`, on prims under `/Character/Rig/Correctives/` (the standard mechanism — the JSON of the first
draft was replaced on 2026-10-29). The nearest precedents are Daz's `JointLinks` (bone, axis, angle→value keys) and
MetaHuman's RBF solvers (key poses → corrective bones), both vendor-private.

```usda
def "elbow_flex_l" (prepend apiSchemas = ["JustStageCorrectiveAPI_1"])
{
    token juststage:driver:kind = "swingTwist"          # swingTwist | rbf
    rel   juststage:driver:bone = </Character/Skel/Skeleton>   # + token juststage:driver:joint = "lowerarm_l"
    token juststage:driver:space = "parent"
    token juststage:driver:channel = "swingX"           # swingX | swingY | twist
    float2[] juststage:driver:keys = [(0, 0), (90, 0.6), (140, 1.0)]   # degrees → weight, linear between keys
    rel   juststage:targets:blendShapes = </Character/Skel/Body/corrective_elbow_flex_l>
    float[] juststage:targets:blendShapeScales = [1.0]
    rel   juststage:targets:joints = </Character/Skel/Skeleton>        # + token[] joint names, offsets, rotations, scales
    int   juststage:lodMax = 1
}
# kind "rbf": a "poses" child prim per key pose (joint rotations as quatf[]), token kernel = "gaussian", float radius = 30
```

In Blender these become generated drivers (never hand-made); on export they become: Unreal — a Control Rig / Anim
Blueprint node set the plugin builds (DazToUnreal's `JointLinks` → `_JCMAnim` pattern, S9), or RBF pose assets;
glTF/VRM — baked out (no equivalent; the sidecar keeps the record); FBX — the sidecar. Deformation tools behind the
shapes (Dem Bones BSD-3, complementary dynamics MIT, Jolt skinned soft bodies MIT — S10 §3h) are implementation
choices, not schema.

## 4 · Capture inputs (live)

| Source | Protocol | Names | Standard |
|---|---|---|---|
| Webcam | MediaPipe Face Landmarker in-process (Apache-2.0) | ARKit 51 | MediaPipe |
| iPhone / other apps | VMC protocol (OSC over UDP, ports 39539/39540) | `/VMC/Ext/Bone/Pos` with Unity `HumanBodyBones` names (→ role map), `/VMC/Ext/Blend/Val` with ARKit names | [VMC](https://protocol.vmc.info/english) (MIT) |
| Unreal | Live Link, through the JustStage Unreal plugin (Live Link is Unreal's receive side, not a wire spec — §8 pass 2) | ARKit curves, our bones (the same names) | Unreal Live Link |

Live streams are not commands; they feed the pose and the face controls directly ([`commands-and-api.md`](commands-and-api.md) §5).

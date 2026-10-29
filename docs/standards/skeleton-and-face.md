# Skeleton, face and correctives — the standards and every mapping table

> **Status: DRAFT, 2026-10-29 — for the user's approval** (see [`README.md`](README.md)). R9, R18. Facts: RESEARCH §2,
> §5, §8 and the S8/S9 notes; the bone maps fetched by this session on 2026-10-29 are recorded in RESEARCH §8.

## 1 · The body skeleton (`js_humanoid`, version 1)

**Structure:** the UE5 / MetaHuman body hierarchy (pelvis, five spine bones, two neck bones, clavicles, two twist bones
per limb segment, finger metacarpals, three finger segments, foot and ball), which CC5 aligned to ("ten additional
bones … aligning CC bones with UE 5's key structures", §2) and Daz's bridges map onto (§8). **Names:** JustStage's
own, in Blender's symmetry convention (`.L` / `.R` suffixes, `.001` chain numbers — the form Rigify's human metarig
uses, §8 pass 2), so Blender's mirror and symmetrize tools work on our rig without renaming.
Standard: [Blender bone naming](https://docs.blender.org/manual/en/latest/animation/armatures/bones/editing/naming.html);
the structure follows the converged commercial skeleton (§8: "The commercial side has converged on Epic's skeleton").

### 1.1 Deform bones (90)

| Chain | Bones | Count |
|---|---|---|
| Root and centre | `root`, `pelvis`, `spine.001`–`spine.005`, `neck.001`, `neck.002`, `head` | 10 |
| Arm (per side) | `clavicle`, `upper_arm`, `upper_arm_twist.001`, `upper_arm_twist.002`, `lower_arm`, `lower_arm_twist.001`, `lower_arm_twist.002`, `hand` | 8 × 2 |
| Hand (per side) | `thumb.001`–`thumb.003`; `index_metacarpal`, `index.001`–`index.003`; `middle_metacarpal`, `middle.001`–`.003`; `ring_metacarpal`, `ring.001`–`.003`; `pinky_metacarpal`, `pinky.001`–`.003` | 19 × 2 |
| Leg (per side) | `thigh`, `thigh_twist.001`, `thigh_twist.002`, `calf`, `calf_twist.001`, `calf_twist.002`, `foot`, `ball` | 8 × 2 |
| Secondary (per side) | `breast` | 1 × 2 |
| Face anchors | `eye.L`, `eye.R`, `jaw`, `teeth_upper`, `teeth_lower`, `tongue.001`–`tongue.003` | 8 |

Rules: `root` sits at the origin on the floor and carries root motion; `pelvis` is the retarget pelvis; bones point
+Y along their length (Blender's and Godot's convention, §8 pass 2); the rest pose is the A-pose of
[`character-data-model.md`](character-data-model.md) §1.1; every bone is in the `DEF` bone collection; control rigs
(Rigify-generated or our own) add `MCH-`/`CTRL-` bones that are never exported. Face volume joints (MetaHuman has 70
and 713 head joints at LOD0 — §8 pass 2) are **not** in the humanoid list: they are the face rig's joints, owned by
the DNA file (§2), generated with it, and exported with it.

Toes beyond `ball` and the IK helper bones Unreal uses (`ik_foot_root`, `ik_foot_l/r`, `ik_hand_root`, `ik_hand_gun`,
`ik_hand_l/r`) are not deform bones; the Unreal export preset adds the IK bones (§1.3). Individual toes may be added
in a later version as a `secondary` group (CC3+ has five toe bones per side — §2 pass 2).

### 1.2 The humanoid role map

Every deform bone above maps to at most one **humanoid role**; roles use the VRM 1.0 vocabulary (55 bones, 15
required), which Godot's `SkeletonProfileHumanoid` shares and Unity's `HumanBodyBones` shares except at the thumb
(§8). The spec's bones, verbatim from `humanoid.md` (fetched 2026-10-29): torso `hips`, `spine`, `chest`, `upperChest`,
`neck`; head `head`, `leftEye`, `rightEye`, `jaw`; legs `upperLeg`, `lowerLeg`, `foot`, `toes` per side; arms
`shoulder`, `upperArm`, `lowerArm`, `hand` per side; fingers `thumbMetacarpal`, `thumbProximal`, `thumbDistal`,
`{index,middle,ring,little}{Proximal,Intermediate,Distal}` per side. Required: `hips`, `spine`, `head`, both
`upperLeg`, `lowerLeg`, `foot`, `upperArm`, `lowerArm`, `hand`. Rules quoted: "Humanoid bones must be unique in VRM";
"upperChest can exist only when chest exists"; scale "MUST have positive values".

| JustStage | VRM 1.0 role | Unity `HumanBodyBones` | Godot profile |
|---|---|---|---|
| `pelvis` | `hips` | `Hips` | `Hips` |
| `spine.001` | `spine` | `Spine` | `Spine` |
| `spine.003` | `chest` | `Chest` | `Chest` |
| `spine.005` | `upperChest` | `UpperChest` | `UpperChest` |
| `neck.001` | `neck` | `Neck` | `Neck` |
| `head` | `head` | `Head` | `Head` |
| `eye.L` / `eye.R` | `leftEye` / `rightEye` | `LeftEye` / `RightEye` | `LeftEye` / `RightEye` |
| `jaw` | `jaw` | `Jaw` | `Jaw` |
| `clavicle.L` | `leftShoulder` | `LeftShoulder` | `LeftShoulder` |
| `upper_arm.L` | `leftUpperArm` | `LeftUpperArm` | `LeftUpperArm` |
| `lower_arm.L` | `leftLowerArm` | `LeftLowerArm` | `LeftLowerArm` |
| `hand.L` | `leftHand` | `LeftHand` | `LeftHand` |
| `thumb.001.L` / `.002` / `.003` | `leftThumbMetacarpal` / `Proximal` / `Distal` | `LeftThumbProximal` / `Intermediate` / `Distal` | `LeftThumbMetacarpal` / `Proximal` / `Distal` |
| `index.001.L` / `.002` / `.003` | `leftIndexProximal` / `Intermediate` / `Distal` | same | same |
| `middle.*`, `ring.*`, `pinky.*` | `leftMiddle*`, `leftRing*`, `leftLittle*` | `LeftMiddle*`, `LeftRing*`, `LeftLittle*` | same as VRM, PascalCase |
| `thigh.L` | `leftUpperLeg` | `LeftUpperLeg` | `LeftUpperLeg` |
| `calf.L` | `leftLowerLeg` | `LeftLowerLeg` | `LeftLowerLeg` |
| `foot.L` | `leftFoot` | `LeftFoot` | `LeftFoot` |
| `ball.L` | `leftToes` | `LeftToes` | `LeftToes` |
| `spine.002`, `spine.004`, `neck.002`, twists, metacarpals (other than the thumb's), `breast`, teeth, tongue | — (non-humanoid nodes; VRM allows them between humanoid bones) | — | — |

Sources: [VRM humanoid](https://github.com/vrm-c/vrm-specification/blob/master/specification/VRMC_vrm-1.0/humanoid.md),
[Unity HumanBodyBones](https://docs.unity.com/en-us/engine/current/script-reference/unityengine/humanbodybones),
[Godot SkeletonProfileHumanoid](https://docs.godotengine.org/en/stable/classes/class_skeletonprofilehumanoid.html).
Unity's `Proximal` = VRM's `Metacarpal` for the thumb is the standards note's inference (§8); the Unity preset test
proves it on import.

### 1.3 Unreal (UE5 Mannequin and MetaHuman body)

Measured 2026-10-29 on this machine (RESEARCH §8; the lists are in
`../plans/2026-10-29-spec-evidence/ue5-mannequin-bones.json`): the bone names read from `SKM_Manny_Simple.uasset` and
`SK_Mannequin.uasset` in the user's UE 5.7 projects. Manny Simple has exactly **89** names (the published UE5 Mannequin
count): 80 deform bones plus 9 helpers (`ik_foot_root`, `ik_foot_l/r`, `ik_hand_root`, `ik_hand_gun`, `ik_hand_l/r`,
`interaction`, `center_of_mass`). The full `SK_Mannequin` has **161**: the same 89 plus 72 corrective bones
(`*_correctiveRoot_*`, `*_twistCor_0N_*`, `thigh_fwd/bck/in/out`, `thigh_fwd_lwr/bck_lwr`, `calf_knee/kneeBack`,
`upperarm_fwd/bck/in/out/bicep/tricep`, `lowerarm_fwd/bck/in/out`, `wrist_inner/outer`, `ankle_fwd/bck`,
`clavicle_pec/out/scap`, `spine_04_latissimus`, `weapon`). Neither has `metatarsal_*` or `pectoral_*` (Daz's bridge adds
those on its side). Epic's MetaHuman DNA page names the 30 body joints a face DNA must match (§8 pass 2); they are in the
161.

| JustStage | UE5 name | Note |
|---|---|---|
| `root` | `root` | |
| `pelvis` | `pelvis` | |
| `spine.001`–`spine.005` | `spine_01`–`spine_05` | Daz's G9 map skips `spine_04` (G9 has four spine bones); ours has all five |
| `neck.001`, `neck.002` | `neck_01`, `neck_02` | |
| `head` | `head` | |
| `clavicle.L` | `clavicle_l` | |
| `upper_arm.L` | `upperarm_l` | |
| `upper_arm_twist.001.L` / `.002` | `upperarm_twist_01_l` / `_02_l` | |
| `lower_arm.L` | `lowerarm_l` | |
| `lower_arm_twist.001.L` / `.002` | `lowerarm_twist_01_l` / `_02_l` | |
| `hand.L` | `hand_l` | |
| `thumb.001.L`–`.003` | `thumb_01_l`–`thumb_03_l` | |
| `index_metacarpal.L`, `index.001.L`–`.003` | `index_metacarpal_l`, `index_01_l`–`index_03_l` | same pattern for `middle`, `ring`, `pinky` |
| `thigh.L` | `thigh_l` | |
| `thigh_twist.001.L` / `.002` | `thigh_twist_01_l` / `_02_l` | |
| `calf.L` | `calf_l` | |
| `calf_twist.001.L` / `.002` | `calf_twist_01_l` / `_02_l` | measured: present on both Manny assets |
| `foot.L` | `foot_l` | |
| `ball.L` | `ball_l` | Manny has no `metatarsal_*` (Daz's map targets its own addition) |
| `breast.L` | — | Manny has no `pectoral_*`; the Unreal preset exports `breast_l/r` as extra bones when the character has them, or drops them (preset option) |
| `eye.L`, `jaw`, teeth, tongue | — | MetaHuman's face joints come from the DNA; the export preset names ours from the DNA definition |
| (added on export) | `ik_foot_root`, `ik_foot_l/r`, `ik_hand_root`, `ik_hand_gun`, `ik_hand_l/r`, `interaction`, `center_of_mass` | the 9 non-deform helpers in `SKM_Manny_Simple` (measured); created by the preset, the IK bones constrained to `foot`/`hand` |

The 72 corrective bones of the full `SK_Mannequin` (and MetaHuman's body) are driven by Epic's RBF and twist setups;
JustStage's own correctives (§3) export as corrective bones under our names, and the "Send to Unreal as a MetaHuman"
option (R12) lets Epic's pipeline build Epic's.

### 1.4 HumanIK, Mixamo, Daz and CC

| JustStage | HumanIK (MotionBuilder 2026) | Mixamo (`mixamorig:` + HumanIK name) | Daz Genesis 9 | Daz Genesis 8 / 8.1 | CC3+ / CC4 (`CC_Base_` prefix) |
|---|---|---|---|---|---|
| `pelvis` | `Hips` | `mixamorig:Hips` | `hip` | `hip` | `Hip` (CC also has `Pelvis`, `Waist`) |
| `spine.001` | `Spine` | `Spine` | `spine1` | `abdomenLower` | `Spine01` |
| `spine.002` | `Spine1` | `Spine1` | `spine2` | `abdomenUpper` | `Spine02` |
| `spine.003` | `Spine2` | `Spine2` | `spine3` | `chestLower` | — |
| `spine.004` | `Spine3` | — | — | — | — |
| `spine.005` | `Spine4` | — | `spine4` | `chestUpper` | — |
| `neck.001` / `neck.002` | `Neck` / `Neck1` | `Neck` / — | `neck1` / `neck2` | `neckLower` / `neckUpper` | `NeckTwist01` / `NeckTwist02` |
| `head` | `Head` | `Head` | `head` | `head` | `Head` |
| `clavicle.L` | `LeftShoulder` | `LeftShoulder` | `l_shoulder` | `lCollar` | `L_Clavicle` |
| `upper_arm.L` | `LeftArm` | `LeftArm` | `l_upperarm` | `lShldrBend` | `L_Upperarm` |
| `upper_arm_twist.001.L` / `.002` | `LeftArmRoll` (leaf roll bones, up to five per limb) | — | `l_upperarmtwist1` / `2` | `lShldrTwist` / — | `L_UpperarmTwist01` / `02` |
| `lower_arm.L` | `LeftForeArm` | `LeftForeArm` | `l_forearm` | `lForearmBend` | `L_Forearm` |
| `lower_arm_twist.001.L` / `.002` | `LeftForeArmRoll` | — | `l_forearmtwist1` / `2` | `lForearmTwist` / — | `L_ForearmTwist01` / `02` |
| `hand.L` | `LeftHand` | `LeftHand` | `l_hand` | `lHand` | `L_Hand` |
| `thumb.001.L`–`.003` | `LeftHandThumb1`–`3` | `LeftHandThumb1`–`3` | `l_thumb1`–`3` | `lThumb1`–`3` | `L_Thumb1`–`3` |
| `index_metacarpal.L` | `LeftInHandIndex` | — | `l_indexmetacarpal` | `lCarpal1` | — |
| `index.001.L`–`.003` | `LeftHandIndex1`–`3` | `LeftHandIndex1`–`3` | `l_index1`–`3` | `lIndex1`–`3` | `L_Index1`–`3` |
| `middle_metacarpal.L`, `middle.*` | `LeftInHandMiddle`, `LeftHandMiddle1`–`3` | `LeftHandMiddle1`–`3` | `l_midmetacarpal`, `l_mid1`–`3` | `lCarpal2`, `lMid1`–`3` | `L_Mid1`–`3` |
| `ring_metacarpal.L`, `ring.*` | `LeftInHandRing`, `LeftHandRing1`–`3` | `LeftHandRing1`–`3` | `l_ringmetacarpal`, `l_ring1`–`3` | `lCarpal3`, `lRing1`–`3` | `L_Ring1`–`3` |
| `pinky_metacarpal.L`, `pinky.*` | `LeftInHandPinky`, `LeftHandPinky1`–`3` | `LeftHandPinky1`–`3` | `l_pinkymetacarpal`, `l_pinky1`–`3` | `lCarpal4`, `lPinky1`–`3` | `L_Pinky1`–`3` |
| `thigh.L` | `LeftUpLeg` | `LeftUpLeg` | `l_thigh` | `lThighBend` | `L_Thigh` |
| `thigh_twist.001.L` / `.002` | `LeftUpLegRoll` | — | `l_thightwist1` / `2` | `lThighTwist` / — | `L_ThighTwist01` / `02` |
| `calf.L` | `LeftLeg` | `LeftLeg` | `l_shin` | `lShin` | `L_Calf` |
| `calf_twist.001.L` / `.002` | `LeftLegRoll` | — | — | — | `L_CalfTwist01` / `02` |
| `foot.L` | `LeftFoot` | `LeftFoot` | `l_foot` | `lFoot` | `L_Foot` |
| `ball.L` | `LeftToeBase` | `LeftToeBase` | `l_toes` (`l_metatarsal` between foot and toes) | `lToe` | `L_ToeBase` |
| `breast.L` | — | — | `l_pectoral` | `lPectoral` | `L_Breast` |
| `eye.L` | — | — | (face bones; not in the bridge maps) | — | `L_Eye` |
| `jaw`, `teeth_upper`, `teeth_lower`, `tongue.001`–`.003` | — | — | — | — | `JawRoot`, `UpperJaw`, `Teeth01`, `Teeth02`, `Tongue01`–`03` (under `FacialBone`) |

Sources: HumanIK — the MotionBuilder 2026 help (15 required nodes, Spine1–9, Neck1–9, roll bones, InHand joints —
§8 pass 2); Mixamo — three-vrm's `mixamoVRMRigMap.js` (HumanIK names with the `mixamorig` prefix; Thumb1 is the
metacarpal — §8 pass 2), Mixamo's own page is unreachable (403); Daz — `g9_to_unreal_manny.json`,
`g8_to_unreal.json` (fetched 2026-10-29); CC — the 101-name reconstruction from Reallusion's GPL add-on's string
constants (§2 pass 2; names only). CC5 exports to Unreal already renamed to UE5 names (§2), so the CC5 importer uses
the UE5 column when the file carries UE names and this column for `CC_Base_` files; the ten bones CC5 added are
unpublished and get mapped from an actual CC5 export at step 6.

Right side: replace `.L` with `.R`, `Left` with `Right`, `l_` with `r_`, `l` with `r`, `L_` with `R_`.

### 1.5 Retargeting

- Imports **characterise** (CC's word, Unreal's IK Rig: a T/A retarget pose plus the role map) through a per-source
  **profile** (`data/profiles/<source>.json`: the column above as a name map, the source's rest pose, axes and units),
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

### 2.3 The rig: DNA + RigLogic, our control vocabulary

- The face rig is a **DNA file** (`rig/face.dna`) with the four DNA layers (descriptor, definition, behaviour,
  geometry — §8), evaluated by **OpenRigLogic** (MIT; C++ with Python bindings): GUI controls → raw controls →
  corrective (PSD) expressions, joint transforms, blend-shape weights and animated-map (wrinkle) weights. Standard:
  [OpenRigLogic](https://github.com/EpicGames/OpenRigLogic); the trademark file bars Epic's marks in our product name
  only (§4) — our rig is "based on OpenRigLogic".
- **Control vocabulary — NOT STANDARD (extends ARKit 52).** The GUI controls are the ARKit 52 names, plus JustStage's
  own controls for what ARKit lacks, named in the same camelCase style with the same left/right rule (e.g.
  `mouthStickyUpperLeft`, `lipCornerDepressLeft`, `eyeLidTightenRight`, `noseWrinkleLeft`, `browLateralLeft`,
  `tongueUp`, `tongueLeft`, `cheekRaiseLeft`, `jawChew`). The target size is CC5 HD's class (262 expression + 128
  corrective sliders — §2 pass 2), reached by the gate's rig-generation work (R5, S10 §3g); the list is a data file
  (`data/face/controls.json`) and the table here grows with it. Standard options: ARKit 52 alone (too coarse for a
  hero face — §8's attack), FACS action units (the manual is paid and the AU list's openness unverified — §8), or
  MetaHuman's control names (Epic's content, not public as a list — §8 pass 2, and clean-room). Trade-off: a vocabulary
  of our own needs mapping tables to MetaHuman Animator curves (built at import from the user's own MHA exports) and
  to CC5's HD sliders (from CC5's public slider table); in return every capture source (iPhone, MediaPipe, VRM, CC5
  Standard) drives it through the guaranteed 52. Waits for the user's word.
- **Face joints** (eyes, jaw, teeth, tongue, and the volume joints the generated rig needs) are DNA joints; the
  eight anchors in §1.1 are mirrored into the body armature so Blender's animation tools can key them.
- **Wrinkle layers** are DNA animated maps: their weights come out of RigLogic and drive the material's
  `wrinkle.<i>` channels ([`character-data-model.md`](character-data-model.md) §3.1).
- **LODs:** the DNA carries per-LOD joint, blend-shape and map lists (MetaHuman's pattern, 8 head LODs — §8 pass 2);
  JustStage generates LOD0–3 at first (step 4) and reserves 4–7.

### 2.4 Interchange

| Target | What goes out | Standard |
|---|---|---|
| USD package | `UsdSkelBlendShape` for every shape key (with `normalOffsets` and in-betweens where used — §8 pass 2); the DNA file beside it; control curves in `UsdSkelAnimation.blendShapeWeights` only for the ARKit 52, the rest in the companion | UsdSkel |
| Unreal (plugin) | the DNA file → the plugin builds the RigLogic-driven skeletal mesh (MetaHuman's own runtime path); ARKit curves for Live Link Face | OpenRigLogic, Live Link |
| glTF / VRM | the 52 as morph targets with `extras.targetNames`; VRM `expressions` presets derived; visemes mapped to VRM's five | glTF 2.0, VRM 1.0 |
| FBX | the 52 (and, on request, every control's resolved shape) as blend shapes; `jawOpen` folds teeth and tongue (CC5's "mouth-open as morph" behaviour, §2) | FBX via ufbx-write |
| CC5 | the 52 by CC5's Standard-profile names (mapping table at step 6 from CC5's slider table page) | — |

## 3 · Body correctives — the JSON schema

No open format carries joint-driven correctives (S9: Daz JCMs, MetaHuman RBF, CC HD correctives cross only in
sidecars). **NOT STANDARD — JustStage's `correctives` schema.** Standard option: none exists; the nearest are Daz's
`JointLinks` (bone, axis, angle→value keys) and MetaHuman's RBF solvers (key poses → corrective bones), both
vendor-private. Trade-off: a schema of our own, against shipping characters whose elbows and shoulders collapse
(hm08's known LBS weakness, §5 pass 2; CC5's lack of JCMs is a top complaint, §2). Waits for the user's word.

```jsonc
// character.juststage.json → "correctives": [ … ]
{
  "id": "elbow_flex.L",
  "driver": {
    "kind": "swing_twist",              // or "rbf"
    "bone": "lower_arm.L",
    "space": "parent",
    "channel": "swing_x",               // swing_x | swing_y | twist
    "keys": [[0, 0], [90, 0.6], [140, 1.0]]   // degrees → weight, linear between keys
  },
  "targets": [
    { "shape_key": "corrective.elbow_flex.L", "scale": 1.0 },
    { "bone": "elbow_fix.L", "offset": [0, 0.01, 0], "rotation": [0, 0, 0], "scale": 1.0 }
  ],
  "lod_max": 1
}
// kind "rbf": "poses": [{ "name", "rotations": {bone: quat}, "targets": [...] }], "kernel": "gaussian", "radius": 30
```

In Blender these become generated drivers (never hand-made); on export they become: Unreal — a Control Rig / Anim
Blueprint node set the plugin builds (DazToUnreal's `JointLinks` → `_JCMAnim` pattern, S9), or RBF pose assets;
glTF/VRM — baked out (no equivalent; `extensions.org.juststage.correctives` keeps the record); FBX — the companion
JSON. Deformation tools behind the shapes (Dem Bones BSD-3, complementary dynamics MIT, Jolt skinned soft bodies MIT —
S10 §3h) are implementation choices, not schema.

## 4 · Capture inputs (live)

| Source | Protocol | Names | Standard |
|---|---|---|---|
| Webcam | MediaPipe Face Landmarker in-process (Apache-2.0) | ARKit 51 | MediaPipe |
| iPhone / other apps | VMC protocol (OSC over UDP, ports 39539/39540) | `/VMC/Ext/Bone/Pos` with Unity `HumanBodyBones` names (→ role map), `/VMC/Ext/Blend/Val` with ARKit names | [VMC](https://protocol.vmc.info/english) (MIT) |
| Unreal | Live Link, through the JustStage Unreal plugin (Live Link is Unreal's receive side, not a wire spec — §8 pass 2) | ARKit curves, our bones under the UE5 preset names | Unreal Live Link |

Live streams are not commands; they feed the pose and the face controls directly ([`commands-and-api.md`](commands-and-api.md) §5).

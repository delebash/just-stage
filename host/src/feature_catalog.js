// SPDX-License-Identifier: MIT
// The app's AI features — what AI Settings → "Routing by feature" lists (app-structure §8), handed
// to installLlm. Each feature's ACTION points at an engine preset (seed_presets.js
// DEFAULT_FEATURE_PRESETS) that owns the provider, the model and every tunable; its prompt row is
// seed_feature_prompts.js. A feature is registered the day it calls the engine — a routing row
// for a feature that can't route is a lie (§11).
//
// `label` and `hint` are the words the user meets (the copy law, §11): outcomes, never internal
// terms. They are database seed data, English for now (§11: vue-i18n can't reach seeded rows yet).

import { FeatureCatalogEntry } from "@delebash/core/llm";

export const FEATURE_CATALOG = [
  // JustStage's skin generator, its first image step (JustStage's docs/standards/ai-engines.md §1, R5): a close-up of
  // skin — pores, fine lines — that the Blender extension makes seamless and lays over the character's skin as its
  // micro detail (POST /v1/ai/image/jobs from Blender).
  FeatureCatalogEntry({
    key: "juststage.skin_detail",
    label: "Make skin detail",
    hint: "Draws a close-up of skin — pores and fine lines — that JustStage lays over a character's skin.",
    group: "Skin",
    kind: "image",
  }),
];

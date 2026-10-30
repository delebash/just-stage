// SPDX-License-Identifier: MIT
// A setting still at an earlier default takes today's; one its owner edited is never touched — and a default can't
// change without its old fingerprint being kept (database/seed.js PREVIOUS_DEFAULTS, the kit's upgradeSettings).
import { defaultsFingerprints, fingerprint, upgradeSettings as upgradeToToday } from "@delebash/core/platform";
import { afterEach, expect, test } from "vitest";
import { openAppDatabase } from "../src/database/index.js";
import { PREVIOUS_DEFAULTS, SETTING_DEFAULTS, seedSettings, upgradeSettings } from "../src/database/seed.js";
import { getSetting, setSetting } from "../src/database/settings.js";
import { tmpDir } from "./helpers.js";

const open = [];
afterEach(() => {
  for (const db of open.splice(0)) db.close(); // Windows can't delete an open file
});

// Today's default of EVERY setting. A change here means a default changed: add the OLD fingerprint to
// PREVIOUS_DEFAULTS (so installs still holding it get the new one), then update this line.
const TODAY = {
  "windows.checkSeconds": "4e07408562bedb8b",
};

test("today's defaults are the ones this test knows, and none of them is listed as earlier", () => {
  expect(defaultsFingerprints(SETTING_DEFAULTS)).toEqual(TODAY);
  for (const [key, print] of Object.entries(TODAY)) expect(PREVIOUS_DEFAULTS[key] ?? []).not.toContain(print);
});

test("a setting still at an earlier default takes today's; an edited one, and today's, are left alone", () => {
  const db = openAppDatabase(tmpDir());
  open.push(db);
  seedSettings(db);
  expect(upgradeSettings(db)).toEqual([]); // a fresh install holds today's
  // as an install made before a change would: an earlier check interval — then one the owner set
  const previous = { "windows.checkSeconds": [fingerprint(2)] };
  setSetting(db, "windows.checkSeconds", 2);
  expect(upgradeToToday(db, { defaults: SETTING_DEFAULTS, previous, getSetting, setSetting })).toEqual(["windows.checkSeconds"]);
  expect(getSetting(db, "windows.checkSeconds")).toBe(3);
  setSetting(db, "windows.checkSeconds", 7);
  expect(upgradeToToday(db, { defaults: SETTING_DEFAULTS, previous, getSetting, setSetting })).toEqual([]);
  expect(getSetting(db, "windows.checkSeconds")).toBe(7);
});

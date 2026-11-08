# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The one test runner inside Blender (docs/standards/testing.md §2): pytest on Blender's own Python.

Run by `python tools/dev.py test [pytest args]`, which starts Blender headless on JustStage's own folders. It passes
`-q` itself: don't add another - at `-qq` pytest prints no "N passed" line (the 2026-11-07/08 suite logs had none).
Windows' faulthandler prints "Windows fatal exception: access violation" at `os.environ` writes (pytest's
`PYTEST_CURRENT_TEST`) during some runs - handled exceptions inside Blender's process: every test after one ran on
and passed (2026-11-08, 16 and 42 dumps in two green runs); a real crash ends the run.
"""

import os
import sys

import addon_utils

ROOT = os.environ["JUSTSTAGE_ROOT"]
sys.path.insert(0, os.environ["JUSTSTAGE_PYDEPS"])

import pytest  # noqa: E402

ADDON = "bl_ext.system.juststage"

addon_utils.enable(ADDON, default_set=True, handle_error=None)
if ADDON not in {m.__name__ for m in addon_utils.modules()} or not addon_utils.check(ADDON)[1]:
    print(f"run.py: {ADDON} did not load", file=sys.stderr)
    sys.exit(2)

args = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
sys.exit(pytest.main([os.path.join(ROOT, "tests", "blender"), "-p", "no:cacheprovider", "-q", *args]))

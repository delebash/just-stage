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

# the manifest's wheels installed before enabling (Blender's own call: "needed so wheels can be setup before the add-on
# is enabled" - addon_utils.extensions_refresh; --factory-startup enables nothing at startup, so nothing synced them)
addon_utils.extensions_refresh(addon_modules_pending=[ADDON])
addon_utils.enable(ADDON, default_set=True, handle_error=None)
if ADDON not in {m.__name__ for m in addon_utils.modules()} or not addon_utils.check(ADDON)[1]:
    print(f"run.py: {ADDON} did not load", file=sys.stderr)
    sys.exit(2)

args = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
#: the whole folder only when no test path is given (pytest's own `testpaths` rule) - it was always added, so a file
#: given to narrow a run ran the whole suite (2026-11-08)
given = [a for a in args if not a.startswith("-") and os.path.exists(os.path.join(ROOT, a.split("::")[0]))]
default = [] if given else [os.path.join(ROOT, "tests", "blender")]
sys.exit(pytest.main([*default, "-p", "no:cacheprovider", "-q", *args]))

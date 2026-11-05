# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Claude Code's SessionStart hook (`.claude/settings.json`): puts `docs/dev/RESUME.md` into the session at every
start - after a compaction too - with the order to read what it lists before any tool call (the user, 2026-11-05:
"fix it keep things current do not really on compaction")."""

import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("CLAUDE_PROJECT_DIR") or Path(__file__).resolve().parents[1])


def main() -> None:
    try:
        source = json.loads(sys.stdin.read() or "{}").get("source", "")
    except json.JSONDecodeError:
        source = ""
    resume = (ROOT / "docs" / "dev" / "RESUME.md").read_text(encoding="utf-8")
    order = (
        f"Session start ({source or 'unknown'}). THE ONE PRIORITY (RESUME.md's first section): prove CC5 quality on every "
        "part for any character, riskiest first - nothing else. Before any tool call, read docs/dev/RESUME.md's 'Always' list and "
        "every file it lists for the active job, in full where marked; a compaction summary is checked against those "
        "files, never trusted instead of them. The file, as it stands now:\n\n"
    )
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": order + resume}}))


if __name__ == "__main__":
    main()

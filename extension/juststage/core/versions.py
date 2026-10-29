# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Version ranges such as ">=1.0,<2" — what a plugin's `api` field states (docs/standards/plugins.md §2)."""

from __future__ import annotations

import operator
import re

_CLAUSE = re.compile(r"^\s*(>=|<=|==|>|<)\s*(\d+(?:\.\d+){0,2})\s*$")
_OPS = {">=": operator.ge, "<=": operator.le, "==": operator.eq, ">": operator.gt, "<": operator.lt}


def parse(version: str) -> tuple[int, int, int]:
    parts = [int(p) for p in version.split(".")]
    if not 1 <= len(parts) <= 3:
        raise ValueError(f"not a version: {version!r}")
    return tuple(parts + [0] * (3 - len(parts)))  # type: ignore[return-value]


def satisfies(version: str, spec: str) -> bool:
    """Whether `version` meets every comma-separated clause of `spec`; a malformed spec raises ValueError."""
    v = parse(version)
    clauses = [c for c in spec.split(",") if c.strip()]
    if not clauses:
        raise ValueError("an empty version range")
    for clause in clauses:
        m = _CLAUSE.match(clause)
        if not m:
            raise ValueError(f"not a version clause: {clause!r}")
        op, bound = m.groups()
        if not _OPS[op](v, parse(bound)):
            return False
    return True

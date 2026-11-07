# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The gate's measures as a table, ours (and each factor render) beside Aaron:

    .dev/venv-tools/Scripts/python -I tools/gate/measure_table.py OUT_DIR [--engine eevee|cycles]

Reads `measures_<engine>.json` (`tools/gate/measure.py`). Per window: L* a* b*, the detail bands (micro / pore / fold /
form, RMS L*), the ridges (dark / light) and the worst repeatability spread; then each of ours as a ratio of Aaron's,
marked = (within that measure's repeatability band on Aaron, two-sided - quality-gate.md §5), < or >, the
band in brackets, "!" where it is over 5% (that measure goes back)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def _fmt(v):
    return "-" if v is None else (f"{v:.3f}" if isinstance(v, float) else str(v))


def table(report: dict) -> str:
    rows = []
    for view, wins in report.items():
        for win, whos in wins.items():
            ref = whos.get("cc5", {})
            rep = ref.get("repeatability", {})
            rows.append(f"\n{view} / {win}   (each ratio's band in brackets: Aaron's own spread for that measure)")
            for who in sorted(whos, key=lambda w: (w != "cc5", w)):
                m = whos[who]
                if "lab" not in m:
                    rows.append(f"  {who:22} no numbers (cover {m.get('cover')})")
                    continue
                b, r = m["bands"], m["ridges"]
                line = (f"  {who:22} Lab {m['lab'][0]:5.1f} {m['lab'][1]:5.1f} {m['lab'][2]:5.1f} | bands "
                        + " ".join(f"{k} {_fmt(v)}" for k, v in b.items())
                        + f" | ridges {_fmt(r['dark'])} / {_fmt(r['light'])}")
                if who != "cc5" and "lab" in ref:
                    marks = []
                    for k, v in b.items():
                        rv = ref["bands"].get(k)
                        if v is None or not rv:
                            continue
                        ratio = v / rv
                        band = rep.get(f"bands.{k}", 0.05)
                        mark = "=" if abs(ratio - 1) <= band else ("<" if ratio < 1 else ">")
                        marks.append(f"{k} {ratio:.2f}{mark}[{band:.0%}]" + ("!" if band > 0.05 else ""))
                    line += "\n" + " " * 26 + "vs Aaron: " + " ".join(marks)
                rows.append(line)
    return "\n".join(rows)


def main() -> None:
    p = argparse.ArgumentParser(prog="measure_table.py")
    p.add_argument("out_dir", type=Path)
    p.add_argument("--engine", choices=("eevee", "cycles"), default="eevee")
    a = p.parse_args()
    print(table(json.loads((a.out_dir / f"measures_{a.engine}.json").read_text())))


if __name__ == "__main__":
    main()

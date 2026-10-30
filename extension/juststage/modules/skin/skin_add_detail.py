# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""`juststage.skin.add_detail` — the skin's fine detail (pores, the crosshatch of skin lines) from a close-up drawn by
the `juststage.skin_detail` feature of JustStage's server (docs/standards/ai-engines.md): made seamless, tiled at
`size_mm` of real skin, as a bump on the character's skin material (run `juststage.skin.set_tone` first).

An AI job command: `start` submits the picture, `finish` applies it; the UI runs them around a Blender timer (its
progress and Cancel in the AI panel), `main` runs both for scripts and headless runs."""

from typing import NamedTuple


class Params(NamedTuple):
    character: str
    seed: int = 1
    size_mm: float = 20.0
    strength: float = 0.5


class Result(NamedTuple):
    image: str
    model: str


COMMAND = dict(
    id="juststage.skin.add_detail",
    label="Skin detail (AI)",
    menu="Character > Skin",
    permission="skin",
    undo=True,
    headless=True,
    since="2026-10-29",
)

FEATURE = "juststage.skin_detail"
SIZE = 1024  # the close-up's pixels a side; its flat middle 60% becomes the tile


def _material(params: Params):
    from ... import character
    from ...core.commands import CommandError

    obj = character.find(params.character)
    material = obj.juststage.skin_material
    if material is None:
        raise CommandError(f"{obj.name} has no skin material yet; run juststage.skin.set_tone first")
    return obj, material


def start(params: Params) -> str:
    from ... import engines, paths
    from ...core.commands import CommandError
    from . import detail

    if not 1.0 <= params.size_mm <= 200.0:
        raise CommandError(f"size_mm: expected 1–200, got {params.size_mm}")
    if not 0.0 <= params.strength <= 2.0:
        raise CommandError(f"strength: expected 0–2, got {params.strength}")
    _material(params)
    try:
        engines.ensure_running(paths.user_dir("server"))
        return engines.submit_image(FEATURE, detail.PROMPT, SIZE, SIZE, params.seed)["id"]
    except engines.EngineError as e:
        raise CommandError(str(e)) from None


def finish(params: Params, png: bytes) -> Result:
    from ... import engines
    from ...core.commands import CommandError
    from . import detail

    obj, material = _material(params)
    try:
        model = engines.feature_model(FEATURE)
        server = engines.health() or {}
    except engines.EngineError as e:
        raise CommandError(str(e)) from None
    provenance = {
        "feature": FEATURE,
        "model": model,
        "seed": params.seed,
        "prompt": detail.PROMPT,
        "server": f"{server.get('product', '')} {server.get('version', '')}".strip(),
    }
    image = detail.apply(material, obj.name, detail.height_from_png(png), params.size_mm, params.strength, provenance)
    return Result(image=image.name, model=model)


def main(params: Params) -> Result:
    from ... import engines
    from ...core.commands import CommandError

    job_id = start(params)
    try:
        png = engines.wait_result(job_id, COMMAND["label"])
    except engines.EngineError as e:
        raise CommandError(str(e)) from None
    return finish(params, png)

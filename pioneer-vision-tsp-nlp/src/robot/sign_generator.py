"""Generate PNG textures for the CoppeliaSim traffic-sign and traffic-light
plates so users can quickly populate a scene without external assets.

Outputs are saved under ``proiect/data/signs/`` as 512x512 PNGs:

  stop.png, yield.png, no_entry.png,
  speed_limit_30.png, speed_limit_50.png, speed_limit_80.png,
  mandatory_forward.png, mandatory_left.png, mandatory_right.png,
  traffic_light_red.png, traffic_light_yellow.png, traffic_light_green.png

In CoppeliaSim:
  * Add a thin rectangular ``Cuboid`` (e.g. 0.4 x 0.4 x 0.005) at the desired pose.
  * Apply the corresponding PNG via *Object Properties -> Texture -> Load*.
  * Disable lighting/shading on the texture for crisp colors (Object Common
    Properties -> ``Visible`` only, no respondable, no dynamic).
"""
from __future__ import annotations

from pathlib import Path
from typing import Tuple

import numpy as np
from PIL import Image, ImageDraw, ImageFont

SIZE = 1024
ASSETS = Path(__file__).resolve().parents[2] / "data" / "signs"


def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for name in ("arialbd.ttf", "DejaVuSans-Bold.ttf", "arial.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            continue
    return ImageFont.load_default()


def _save(img: Image.Image, name: str) -> Path:
    ASSETS.mkdir(parents=True, exist_ok=True)
    path = ASSETS / name
    img.save(path)
    return path


def _regular_polygon(n: int, radius: int, center: Tuple[int, int], rotation_deg: float = 0):
    cx, cy = center
    angles = np.deg2rad(np.linspace(0, 360, n, endpoint=False) + rotation_deg - 90)
    return [(int(cx + radius * np.cos(a)), int(cy + radius * np.sin(a))) for a in angles]


def make_stop() -> Path:
    img = Image.new("RGB", (SIZE, SIZE), "white")
    d = ImageDraw.Draw(img)
    pts = _regular_polygon(8, SIZE // 2 - 40, (SIZE // 2, SIZE // 2), rotation_deg=22.5)
    d.polygon(pts, fill="#cc0000", outline="white")
    pts_in = _regular_polygon(8, SIZE // 2 - 100, (SIZE // 2, SIZE // 2), rotation_deg=22.5)
    d.polygon(pts_in, outline="white")
    font = _font(300)
    text = "STOP"
    bbox = d.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    d.text(((SIZE - tw) // 2, (SIZE - th) // 2 - 12), text, fill="white", font=font)
    return _save(img, "stop.png")


def make_yield() -> Path:
    img = Image.new("RGB", (SIZE, SIZE), "white")
    d = ImageDraw.Draw(img)
    pts = [(80, 120), (SIZE - 80, 120), (SIZE // 2, SIZE - 80)]
    d.polygon(pts, fill="#cc0000")
    inner = [(180, 220), (SIZE - 180, 220), (SIZE // 2, SIZE - 180)]
    d.polygon(inner, fill="white")
    return _save(img, "yield.png")


def make_no_entry() -> Path:
    img = Image.new("RGB", (SIZE, SIZE), "white")
    d = ImageDraw.Draw(img)
    r = SIZE // 2 - 40
    d.ellipse((SIZE // 2 - r, SIZE // 2 - r, SIZE // 2 + r, SIZE // 2 + r), fill="#cc0000")
    bar_h = 120
    d.rectangle((160, SIZE // 2 - bar_h // 2, SIZE - 160, SIZE // 2 + bar_h // 2), fill="white")
    return _save(img, "no_entry.png")


def _speed_limit(value: int) -> Path:
    img = Image.new("RGB", (SIZE, SIZE), "white")
    d = ImageDraw.Draw(img)
    r = SIZE // 2 - 40
    d.ellipse((SIZE // 2 - r, SIZE // 2 - r, SIZE // 2 + r, SIZE // 2 + r), fill="#cc0000")
    r2 = r - 100
    d.ellipse((SIZE // 2 - r2, SIZE // 2 - r2, SIZE // 2 + r2, SIZE // 2 + r2), fill="white")
    font = _font(400)
    text = str(value)
    bbox = d.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    d.text(((SIZE - tw) // 2, (SIZE - th) // 2 - 40), text, fill="black", font=font)
    return _save(img, f"speed_limit_{value}.png")


def make_speed_limit_30() -> Path: return _speed_limit(30)
def make_speed_limit_50() -> Path: return _speed_limit(50)
def make_speed_limit_80() -> Path: return _speed_limit(80)


def _mandatory(direction: str, arrow_pts) -> Path:
    img = Image.new("RGB", (SIZE, SIZE), "white")
    d = ImageDraw.Draw(img)
    r = SIZE // 2 - 40
    d.ellipse((SIZE // 2 - r, SIZE // 2 - r, SIZE // 2 + r, SIZE // 2 + r), fill="#0044cc")
    d.polygon(arrow_pts, fill="white")
    return _save(img, f"mandatory_{direction}.png")


def make_mandatory_forward() -> Path:
    # Body short and below center, big triangular head pointing UP.
    cx, cy = SIZE // 2, SIZE // 2
    pts = [
        (cx - 80, cy + 120), (cx + 80, cy + 120),    # body bottom edge
        (cx + 80, cy + 20),                          # body top-right
        (cx + 240, cy + 20),                         # head right wing
        (cx, cy - 300),                              # head tip (UP)
        (cx - 240, cy + 20),                         # head left wing
        (cx - 80, cy + 20),                          # body top-left
    ]
    return _mandatory("forward", pts)


def make_mandatory_left() -> Path:
    cx, cy = SIZE // 2, SIZE // 2
    pts = [
        (cx + 120, cy - 80), (cx + 120, cy + 80),
        (cx + 20, cy + 80),
        (cx + 20, cy + 240),
        (cx - 300, cy),
        (cx + 20, cy - 240),
        (cx + 20, cy - 80),
    ]
    return _mandatory("left", pts)


def make_mandatory_right() -> Path:
    cx, cy = SIZE // 2, SIZE // 2
    pts = [
        (cx - 120, cy - 80), (cx - 120, cy + 80),
        (cx - 20, cy + 80),
        (cx - 20, cy + 240),
        (cx + 300, cy),
        (cx - 20, cy - 240),
        (cx - 20, cy - 80),
    ]
    return _mandatory("right", pts)


def _traffic_light(color_name: str, color_hex: str, lit_index: int) -> Path:
    img = Image.new("RGB", (SIZE, SIZE), "white")
    d = ImageDraw.Draw(img)
    body = (SIZE // 2 - 180, 60, SIZE // 2 + 180, SIZE - 60)
    d.rounded_rectangle(body, radius=80, fill="#0a0a0a")
    lamp_radius = 120
    centers = [(SIZE // 2, 260), (SIZE // 2, SIZE // 2), (SIZE // 2, SIZE - 260)]
    # Off-lamps are intentionally near-black so HSV color filters reject them.
    colors_off = ["#1a1010", "#181712", "#101a10"]
    colors_on = ["#ff2424", "#ffdb33", "#22dd33"]
    for i, (cx, cy) in enumerate(centers):
        c = colors_on[i] if i == lit_index else colors_off[i]
        d.ellipse((cx - lamp_radius, cy - lamp_radius, cx + lamp_radius, cy + lamp_radius), fill=c)
    return _save(img, f"traffic_light_{color_name}.png")


def make_traffic_light_red() -> Path: return _traffic_light("red", "#ff2222", 0)
def make_traffic_light_yellow() -> Path: return _traffic_light("yellow", "#ffdd33", 1)
def make_traffic_light_green() -> Path: return _traffic_light("green", "#33dd33", 2)


ALL = [
    make_stop, make_yield, make_no_entry,
    make_speed_limit_30, make_speed_limit_50, make_speed_limit_80,
    make_mandatory_forward, make_mandatory_left, make_mandatory_right,
    make_traffic_light_red, make_traffic_light_yellow, make_traffic_light_green,
]


def generate_all() -> list[Path]:
    """Generate every bundled texture and return the list of saved paths."""
    return [fn() for fn in ALL]


if __name__ == "__main__":
    paths = generate_all()
    print(f"Wrote {len(paths)} textures to {ASSETS}")
    for p in paths:
        print(f"  - {p.name}")

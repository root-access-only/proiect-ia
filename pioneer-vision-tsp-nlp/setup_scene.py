"""Configurare automată scenă CoppeliaSim — fără căi hardcodate.

Conectează-se la CoppeliaSim (presupune că ai scena deschisă și pornit play),
și execută:
  1. Dezactivează scriptul Lua default al robotului Pioneer (Braitenberg-ul propriu).
  2. Generează texturile dacă lipsesc.
  3. Creează 12 cuboizi-semne, aplică texturi (cu căi calculate la runtime din
     locația acestui script), îi face non-respondable / non-dynamic.
  4. Plasează semnele în fața robotului, alternativ stânga/dreapta, la 5 m
     distanță, orientate cu fața spre traseu.
  5. Repoziționează vision sensor-ul pe robot (în caz că ai uitat).

Rulare:
    python setup_scene.py

Funcționează identic pe orice mașină — nu modifică nimic pe disc, doar trimite
comenzi prin ZMQ Remote API.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
SIGNS_DIR = PROJECT_ROOT / "data" / "signs"

SIGN_ORDER = [
    "speed_limit_50",
    "yield",
    "speed_limit_30",
    "stop",
    "mandatory_forward",
    "speed_limit_80",
    "mandatory_right",
    "mandatory_left",
    "traffic_light_green",
    "traffic_light_yellow",
    "traffic_light_red",
    "no_entry",
]


def ensure_textures() -> None:
    """Regenerează texturile dacă lipsesc."""
    needed = [SIGNS_DIR / f"{name}.png" for name in SIGN_ORDER]
    if not all(p.exists() for p in needed):
        print("Lipsesc texturi, le generez...")
        from src.robot import sign_generator
        sign_generator.generate_all()
    else:
        print(f"Texturile sunt deja prezente in {SIGNS_DIR}")


def connect():
    """Stabileste conexiunea ZMQ cu CoppeliaSim."""
    try:
        from coppeliasim_zmqremoteapi_client import RemoteAPIClient
    except ImportError:
        print("EROARE: instaleaza dependentele intai:  pip install -r requirements.txt")
        sys.exit(1)
    client = RemoteAPIClient()
    sim = client.require("sim")
    print("Conectat la CoppeliaSim.")
    return sim


def disable_pioneer_script(sim) -> None:
    """Dezactivează scriptul Lua atașat lui Pioneer P3-DX."""
    try:
        robot = sim.getObject("/PioneerP3DX")
    except Exception:
        print("ATENTIE: /PioneerP3DX nu a fost gasit in scena.")
        return
    try:
        script = sim.getScript(sim.scripttype_childscript, robot)
        if script != -1:
            sim.setObjectInt32Param(script, sim.scriptintparam_enabled, 0)
            print("Script Pioneer dezactivat.")
            return
    except Exception:
        pass
    print("Script Pioneer nu a fost gasit (deja sters?).")


def reset_vision_sensor(sim) -> None:
    """Reasează vision sensor-ul pe robot, în față și sus."""
    try:
        robot = sim.getObject("/PioneerP3DX")
        vs = sim.getObject("/PioneerP3DX/visionSensor")
    except Exception:
        print("ATENTIE: vision sensor lipseste. Adauga-l manual ca child al lui Pioneer.")
        return
    sim.setObjectPosition(vs, robot, [0.20, 0.0, 0.20])
    sim.setObjectOrientation(vs, robot, [-1.5707963, 0.0, -1.5707963])
    print("Vision sensor repozitionat.")


def remove_existing_signs(sim) -> None:
    """Sterge semnele dintr-o rulare anterioara."""
    for name in SIGN_ORDER:
        try:
            h = sim.getObject(f"/sign_{name}", {"noError": True})
            if h != -1:
                sim.removeObject(h)
        except Exception:
            pass


def create_sign(sim, name: str) -> int:
    """Creează un cuboid-semn cu textura aplicată."""
    h = sim.createPrimitiveShape(sim.primitiveshape_cuboid, [0.6, 0.02, 0.6], 0)
    sim.setObjectAlias(h, f"sign_{name}")
    texture_path = str(SIGNS_DIR / f"{name}.png").replace("\\", "/")
    tex_shape, tex_id = sim.createTexture(texture_path, 0)
    sim.setShapeTexture(
        h, tex_id, sim.texturemap_plane, 15, [0.6, 0.6], [0, 0, 0], [1.5707963, 0, 0]
    )
    sim.removeObject(tex_shape)
    sim.setObjectInt32Param(h, sim.shapeintparam_respondable, 0)
    sim.setObjectInt32Param(h, sim.shapeintparam_static, 1)
    return h


def place_signs_in_front_of_robot(
    sim, spacing: float = 5.0, lateral: float = 2.5
) -> None:
    """Plasează semnele în fața robotului, alternativ stânga/dreapta."""
    import math

    try:
        robot = sim.getObject("/PioneerP3DX")
    except Exception:
        print("ATENTIE: /PioneerP3DX nu a fost gasit; semnele se plaseaza la origine.")
        rx, ry = 0.0, 0.0
        g = 0.0
    else:
        rp = sim.getObjectPosition(robot, sim.handle_world)
        ro = sim.getObjectOrientation(robot, sim.handle_world)
        rx, ry = rp[0], rp[1]
        g = ro[2]

    cg, sg = math.cos(g), math.sin(g)
    for i, name in enumerate(SIGN_ORDER, start=1):
        d = i * spacing
        side = lateral if (i % 2 == 0) else -lateral
        x = rx + cg * d - sg * side
        y = ry + sg * d + cg * side
        h = create_sign(sim, name)
        sim.setObjectPosition(h, sim.handle_world, [x, y, 0.5])
        sim.setObjectOrientation(h, sim.handle_world, [0, 0, g + math.pi / 2])
        print(f"  + {name:25s} -> ({x:+.2f}, {y:+.2f})")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--spacing", type=float, default=5.0,
                    help="distanta intre semne pe drum (m)")
    ap.add_argument("--lateral", type=float, default=2.5,
                    help="distanta laterala fata de drum (m)")
    ap.add_argument("--skip-vision-reset", action="store_true",
                    help="nu repozitiona vision sensor-ul")
    ap.add_argument("--skip-disable-script", action="store_true",
                    help="nu dezactiva scriptul Pioneer")
    args = ap.parse_args()

    print("=" * 60)
    print(" Setup scena CoppeliaSim - proiect IA Pioneer P3-DX")
    print("=" * 60)

    ensure_textures()
    sim = connect()

    if not args.skip_disable_script:
        disable_pioneer_script(sim)

    if not args.skip_vision_reset:
        reset_vision_sensor(sim)

    print("Sterg semne vechi (daca exista)...")
    remove_existing_signs(sim)

    print("Creez si plasez 12 semne in fata robotului...")
    place_signs_in_front_of_robot(sim, spacing=args.spacing, lateral=args.lateral)

    print("=" * 60)
    print(" Setup complet. Acum poti rula:  python run_gui.py")
    print("=" * 60)


if __name__ == "__main__":
    main()

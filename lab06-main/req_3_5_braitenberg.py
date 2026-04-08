"""
Cerința 3.5 - Vehicul Braitenberg: evitare de obstacole (tip 'Frica').
IA Lab #06 - Inteligență Artificială 2025-2026
"""
import time
from coppeliasim_zmqremoteapi_client import RemoteAPIClient

V_BASE   = 3.0
V_MAX    = 6.0
K_SENSOR = 6.0
SENSOR_MAX = 1.0

WEIGHTS = [
    (+0.5, -0.5),
    (+1.0, -1.0),
    (+1.5, -1.5),
    (+2.0, -2.0),
    (-2.0, +2.0),
    (-1.5, +1.5),
    (-1.0, +1.0),
    (-0.5, +0.5),
]


def braitenberg_velocities(sim, sensors):
    """
    Calculeaza vitezele Braitenberg pentru evitarea obstacolelor.

    Fiecare senzor activat contribuie proportional cu apropierea
    de obstacol, prin ponderile definite in WEIGHTS.

    Args:
        sim: obiectul API CoppeliaSim.
        sensors: lista handle-urilor tuturor senzorilor.

    Returns:
        tuple (v_stang, v_drept) in rad/s.
    """
    v_left  = V_BASE
    v_right = V_BASE

    for i, (w_l, w_r) in enumerate(WEIGHTS):
        result, distance, *_ = sim.readProximitySensor(sensors[i])
        if result:
            proximity = 1.0 - (distance / SENSOR_MAX)
            proximity = max(0.0, min(1.0, proximity))

            v_left  += K_SENSOR * w_l * proximity
            v_right += K_SENSOR * w_r * proximity

    v_left  = max(-V_MAX, min(V_MAX, v_left))
    v_right = max(-V_MAX, min(V_MAX, v_right))

    return v_left, v_right


def main():
    client = RemoteAPIClient()
    sim = client.require('sim')

    left_motor  = sim.getObject('/PioneerP3DX/leftMotor')
    right_motor = sim.getObject('/PioneerP3DX/rightMotor')
    sensors     = [
        sim.getObject(f'/PioneerP3DX/ultrasonicSensor[{i}]')
        for i in range(16)
    ]

    sim.startSimulation()
    print("Vehicul Braitenberg (evitare) pornit. Ctrl+C pentru oprire.\n")

    try:
        iteration = 0
        while True:
            v_left, v_right = braitenberg_velocities(sim, sensors)

            sim.setJointTargetVelocity(left_motor,  v_left)
            sim.setJointTargetVelocity(right_motor, v_right)

            if iteration % 20 == 0:
                print(f"v_stang={v_left:+.2f} rad/s  |  v_drept={v_right:+.2f} rad/s")

            iteration += 1
            time.sleep(0.05)

    except KeyboardInterrupt:
        print("\nOprire vehicul Braitenberg.")
    finally:
        sim.setJointTargetVelocity(left_motor,  0.0)
        sim.setJointTargetVelocity(right_motor, 0.0)
        sim.stopSimulation()


if __name__ == '__main__':
    main()
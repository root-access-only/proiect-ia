"""
Tema D - Braitenberg 'Iubire'
Conexiuni ipsilaterale inhibitorii:
- senzorii din stanga reduc viteza motorului stang
- senzorii din dreapta reduc viteza motorului drept
"""

import time
from coppeliasim_zmqremoteapi_client import RemoteAPIClient

V_BASE = 4.0
V_MIN = 0.0
V_MAX = 6.0
K_SENSOR = 1.5
SENSOR_MAX = 1.0

WEIGHTS = [
    (-0.5,  0.0),
    (-1.0,  0.0),
    (-1.5,  0.0),
    (-2.0,  0.0),
    ( 0.0, -2.0),
    ( 0.0, -1.5),
    ( 0.0, -1.0),
    ( 0.0, -0.5),
]


def clamp(value, vmin, vmax):
    return max(vmin, min(vmax, value))


def set_velocity(sim, left_motor, right_motor, v_left, v_right):
    sim.setJointTargetVelocity(left_motor, v_left)
    sim.setJointTargetVelocity(right_motor, v_right)


def love_velocities(sim, sensors):
    v_left = V_BASE
    v_right = V_BASE

    for i, (w_left, w_right) in enumerate(WEIGHTS):
        result, distance, *_ = sim.readProximitySensor(sensors[i])

        if result:
            proximity = 1.0 - (distance / SENSOR_MAX)
            proximity = clamp(proximity, 0.0, 1.0)

            v_left += K_SENSOR * w_left * proximity
            v_right += K_SENSOR * w_right * proximity

    v_left = clamp(v_left, V_MIN, V_MAX)
    v_right = clamp(v_right, V_MIN, V_MAX)

    return v_left, v_right


def main():
    client = RemoteAPIClient()
    sim = client.require("sim")

    left_motor = sim.getObject("/PioneerP3DX/leftMotor")
    right_motor = sim.getObject("/PioneerP3DX/rightMotor")
    sensors = [
        sim.getObject(f"/PioneerP3DX/ultrasonicSensor[{i}]")
        for i in range(16)
    ]

    sim.startSimulation()
    print("Tema D pornita - Braitenberg 'Iubire'")
    print("Ctrl+C pentru oprire.\n")

    try:
        iteration = 0

        while True:
            v_left, v_right = love_velocities(sim, sensors)
            set_velocity(sim, left_motor, right_motor, v_left, v_right)

            if iteration % 20 == 0:
                print(f"v_stang={v_left:+.2f} rad/s | v_drept={v_right:+.2f} rad/s")

            iteration += 1
            time.sleep(0.05)

    except KeyboardInterrupt:
        print("\nOprire manuala.")

    finally:
        set_velocity(sim, left_motor, right_motor, 0.0, 0.0)
        sim.stopSimulation()
        print("Simulare oprita.")


if __name__ == "__main__":
    main()
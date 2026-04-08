"""
Tema B - Braitenberg cu inregistrare de date
Genereaza un fisier CSV cu:
timestamp, v_left, v_right, s0..s7, pos_x, pos_y
"""

import csv
import os
import time
from coppeliasim_zmqremoteapi_client import RemoteAPIClient

V_BASE = 3.0
V_MAX = 6.0
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

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "log_braitenberg.csv")


def clamp(value, vmin, vmax):
    return max(vmin, min(vmax, value))


def set_velocity(sim, left_motor, right_motor, v_left, v_right):
    sim.setJointTargetVelocity(left_motor, v_left)
    sim.setJointTargetVelocity(right_motor, v_right)


def read_sensor_proximities(sim, sensors):
    """
    Returneaza lista normalizata s0..s7 in [0, 1]
    0 = nimic detectat
    1 = obstacol foarte aproape
    """
    values = []
    for i in range(8):
        result, distance, *_ = sim.readProximitySensor(sensors[i])
        if result:
            proximity = 1.0 - (distance / SENSOR_MAX)
            proximity = clamp(proximity, 0.0, 1.0)
        else:
            proximity = 0.0
        values.append(proximity)
    return values


def braitenberg_velocities(sensor_values):
    v_left = V_BASE
    v_right = V_BASE

    for i, (w_left, w_right) in enumerate(WEIGHTS):
        proximity = sensor_values[i]
        v_left += K_SENSOR * w_left * proximity
        v_right += K_SENSOR * w_right * proximity

    v_left = clamp(v_left, -V_MAX, V_MAX)
    v_right = clamp(v_right, -V_MAX, V_MAX)

    return v_left, v_right


def write_csv_header(csv_writer):
    header = ["timestamp", "v_left", "v_right"]
    header += [f"s{i}" for i in range(8)]
    header += ["pos_x", "pos_y"]
    csv_writer.writerow(header)


def main():
    client = RemoteAPIClient()
    sim = client.require("sim")

    robot = sim.getObject("/PioneerP3DX")
    left_motor = sim.getObject("/PioneerP3DX/leftMotor")
    right_motor = sim.getObject("/PioneerP3DX/rightMotor")
    sensors = [
        sim.getObject(f"/PioneerP3DX/ultrasonicSensor[{i}]")
        for i in range(16)
    ]

    sim.startSimulation()
    time.sleep(0.5)

    print("Tema B pornita.")
    print(f"Se logheaza in: {CSV_PATH}")
    print("Ctrl+C pentru oprire.\n")

    try:
        with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            write_csv_header(writer)

            iteration = 0

            while True:
                timestamp = sim.getSimulationTime()
                sensor_values = read_sensor_proximities(sim, sensors)
                v_left, v_right = braitenberg_velocities(sensor_values)

                set_velocity(sim, left_motor, right_motor, v_left, v_right)

                pos = sim.getObjectPosition(robot, sim.handle_world)
                pos_x, pos_y = pos[0], pos[1]

                row = [timestamp, v_left, v_right]
                row += sensor_values
                row += [pos_x, pos_y]
                writer.writerow(row)
                f.flush()

                if iteration % 20 == 0:
                    print(
                        f"t={timestamp:6.2f}s | "
                        f"vL={v_left:+.2f} | vR={v_right:+.2f} | "
                        f"pos=({pos_x:+.2f}, {pos_y:+.2f})"
                    )

                iteration += 1
                time.sleep(0.05)

    except KeyboardInterrupt:
        print("\nOprire manuala.")

    finally:
        set_velocity(sim, left_motor, right_motor, 0.0, 0.0)
        sim.stopSimulation()
        print("Simulare oprita.")
        print("CSV salvat cu succes.")


if __name__ == "__main__":
    main()
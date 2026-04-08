"""
Tema C - Robot Explorer
Combina wall-following cu recuperare la blocaj si salveaza traiectoria.
"""

import csv
import math
import os
import random
import time
from enum import Enum

import matplotlib.pyplot as plt
from coppeliasim_zmqremoteapi_client import RemoteAPIClient

V_BASE = 2.0
V_TURN = 1.2
TARGET_DIST = 0.4
K_P = 1.8
FRONT_STOP = 0.4
SENSOR_MAX = 1.0

RUN_TIME = 60.0
CONTROL_STEP = 0.05

STUCK_WINDOW = 2.5
STUCK_DISTANCE_EPS = 0.08

RECOVERY_BACK_TIME = 1.0
RECOVERY_TURN_TIME = 0.85

RIGHT_SENSORS = [8, 9]
FRONT_SENSORS = [2, 3, 4, 5]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "tema_c_trajectory.csv")
PLOT_PATH = os.path.join(BASE_DIR, "tema_c_traiectorie.png")


class RobotState(Enum):
    SEARCH_WALL = "SEARCH_WALL"
    FOLLOW_WALL = "FOLLOW_WALL"
    AVOID_FRONT = "AVOID_FRONT"
    RECOVERY = "RECOVERY"


def clamp(value, vmin, vmax):
    return max(vmin, min(vmax, value))


def set_velocity(sim, left_motor, right_motor, v_left, v_right):
    sim.setJointTargetVelocity(left_motor, v_left)
    sim.setJointTargetVelocity(right_motor, v_right)


def read_min_dist(sim, sensors, indices):
    min_dist = SENSOR_MAX
    for idx in indices:
        result, dist, *_ = sim.readProximitySensor(sensors[idx])
        if result and dist < min_dist:
            min_dist = dist
    return min_dist


def distance_2d(p1, p2):
    return math.hypot(p2[0] - p1[0], p2[1] - p1[1])


def save_plot(csv_path, plot_path):
    xs = []
    ys = []

    with open(csv_path, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            xs.append(float(row["x"]))
            ys.append(float(row["y"]))

    if not xs:
        print("Nu exista puncte pentru grafic.")
        return

    plt.figure(figsize=(7, 6))
    plt.plot(xs, ys)
    plt.xlabel("X [m]")
    plt.ylabel("Y [m]")
    plt.title("Traiectoria robotului - Tema C")
    plt.axis("equal")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(plot_path, dpi=150)
    plt.close()


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

    state = RobotState.SEARCH_WALL
    recovery_turn = "left"

    stuck_start_time = 0.0
    stuck_start_pos = None

    sim.startSimulation()
    time.sleep(0.5)

    print("Tema C pornita.")
    print(f"Explorare autonoma pentru cel putin {RUN_TIME:.0f} secunde reale.")
    print("Ctrl+C pentru oprire.\n")

    try:
        with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "x", "y", "state", "dist_front", "dist_right"])

            real_start_time = time.time()
            last_print_real = 0.0

            while True:
                sim_time = sim.getSimulationTime()
                elapsed_real = time.time() - real_start_time

                pos = sim.getObjectPosition(robot, sim.handle_world)
                x, y = pos[0], pos[1]

                dist_front = read_min_dist(sim, sensors, FRONT_SENSORS)
                dist_right = read_min_dist(sim, sensors, RIGHT_SENSORS)

                writer.writerow([sim_time, x, y, state.value, dist_front, dist_right])
                f.flush()

                if stuck_start_pos is None:
                    stuck_start_pos = (x, y)
                    stuck_start_time = sim_time

                if state in (RobotState.SEARCH_WALL, RobotState.FOLLOW_WALL):
                    if sim_time - stuck_start_time >= STUCK_WINDOW:
                        traveled = distance_2d(stuck_start_pos, (x, y))
                        if traveled < STUCK_DISTANCE_EPS:
                            state = RobotState.RECOVERY
                            recovery_turn = random.choice(["left", "right"])
                            print(
                                f"[RECOVERY] Blocaj detectat: "
                                f"deplasare={traveled:.3f} m in {STUCK_WINDOW:.1f}s"
                            )
                            stuck_start_pos = (x, y)
                            stuck_start_time = sim_time
                            continue
                        else:
                            stuck_start_pos = (x, y)
                            stuck_start_time = sim_time

                if state == RobotState.SEARCH_WALL:
                    if dist_front < FRONT_STOP:
                        state = RobotState.AVOID_FRONT
                    elif dist_right < SENSOR_MAX * 0.95:
                        state = RobotState.FOLLOW_WALL
                    else:
                        v_left, v_right = V_BASE, V_BASE * 0.75
                        set_velocity(sim, left_motor, right_motor, v_left, v_right)

                elif state == RobotState.FOLLOW_WALL:
                    if dist_front < FRONT_STOP:
                        state = RobotState.AVOID_FRONT
                    elif dist_right >= SENSOR_MAX * 0.95:
                        state = RobotState.SEARCH_WALL
                    else:
                        error = dist_right - TARGET_DIST
                        v_left = V_BASE + K_P * error
                        v_right = V_BASE - K_P * error

                        cap = V_BASE * 1.25
                        v_left = clamp(v_left, -cap, cap)
                        v_right = clamp(v_right, -cap, cap)

                        set_velocity(sim, left_motor, right_motor, v_left, v_right)

                elif state == RobotState.AVOID_FRONT:
                    set_velocity(sim, left_motor, right_motor, -V_TURN, +V_TURN)
                    time.sleep(0.35)
                    set_velocity(sim, left_motor, right_motor, 0.0, 0.0)

                    dist_right = read_min_dist(sim, sensors, RIGHT_SENSORS)
                    if dist_right < SENSOR_MAX * 0.95:
                        state = RobotState.FOLLOW_WALL
                    else:
                        state = RobotState.SEARCH_WALL

                    pos = sim.getObjectPosition(robot, sim.handle_world)
                    stuck_start_pos = (pos[0], pos[1])
                    stuck_start_time = sim.getSimulationTime()

                elif state == RobotState.RECOVERY:
                    set_velocity(sim, left_motor, right_motor, -1.5, -1.5)
                    time.sleep(RECOVERY_BACK_TIME)

                    if recovery_turn == "left":
                        set_velocity(sim, left_motor, right_motor, -V_TURN, +V_TURN)
                    else:
                        set_velocity(sim, left_motor, right_motor, +V_TURN, -V_TURN)
                    time.sleep(RECOVERY_TURN_TIME)

                    set_velocity(sim, left_motor, right_motor, 0.0, 0.0)
                    state = RobotState.SEARCH_WALL

                    pos = sim.getObjectPosition(robot, sim.handle_world)
                    stuck_start_pos = (pos[0], pos[1])
                    stuck_start_time = sim.getSimulationTime()

                current_real = time.time()
                if current_real - last_print_real >= 1.0:
                    print(
                        f"t_real={elapsed_real:5.1f}s | state={state.value:<11} | "
                        f"front={dist_front:.3f} m | right={dist_right:.3f} m | "
                        f"pos=({x:+.2f}, {y:+.2f})"
                    )
                    last_print_real = current_real

                if elapsed_real >= RUN_TIME:
                    print("\nTimpul minim de explorare a fost atins.")
                    break

                time.sleep(CONTROL_STEP)

    except KeyboardInterrupt:
        print("\nOprire manuala.")

    finally:
        set_velocity(sim, left_motor, right_motor, 0.0, 0.0)
        sim.stopSimulation()
        print("Simulare oprita.")

        if os.path.exists(CSV_PATH):
            save_plot(CSV_PATH, PLOT_PATH)
            print(f"CSV salvat: {CSV_PATH}")
            print(f"Grafic salvat: {PLOT_PATH}")


if __name__ == "__main__":
    main()
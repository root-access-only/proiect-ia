"""
Tema A - Evitare cu recuperare
IA Lab #06

Robotul merge inainte. Daca detecteaza un obstacol in fata:
1. da inapoi o perioada scurta
2. vireaza aleatoriu stanga sau dreapta
3. reia mersul inainte
"""

import time
import random
from enum import Enum
from coppeliasim_zmqremoteapi_client import RemoteAPIClient

V_FORWARD = 2.0
V_BACKWARD = -1.5
V_TURN = 2.0

STOP_DISTANCE = 0.5
SENSOR_MAX = 1.0

BACKWARD_TIME = 1.0
TURN_TIME = 1.2

FRONT_SENSORS = [2, 3, 4, 5]


class RobotState(Enum):
    FORWARD = "FORWARD"
    BACKWARD = "BACKWARD"
    TURNING = "TURNING"


def set_velocity(sim, left_motor, right_motor, v_left, v_right):
    sim.setJointTargetVelocity(left_motor, v_left)
    sim.setJointTargetVelocity(right_motor, v_right)


def get_min_front_distance(sim, sensors, front_indices):
    min_dist = SENSOR_MAX

    for idx in front_indices:
        result, distance, *_ = sim.readProximitySensor(sensors[idx])
        if result and distance < min_dist:
            min_dist = distance

    return min_dist


def next_state(current_state, dist_front):
    if current_state == RobotState.FORWARD:
        if dist_front < STOP_DISTANCE:
            return RobotState.BACKWARD
        return RobotState.FORWARD

    if current_state == RobotState.BACKWARD:
        return RobotState.TURNING

    if current_state == RobotState.TURNING:
        return RobotState.FORWARD

    return current_state


def main():
    client = RemoteAPIClient()
    sim = client.require("sim")

    left_motor = sim.getObject("/PioneerP3DX/leftMotor")
    right_motor = sim.getObject("/PioneerP3DX/rightMotor")
    sensors = [
        sim.getObject(f"/PioneerP3DX/ultrasonicSensor[{i}]")
        for i in range(16)
    ]

    state = RobotState.FORWARD
    turn_direction = "left"

    sim.startSimulation()
    print("Tema A pornita.")
    print("Stari: FORWARD -> BACKWARD -> TURNING -> FORWARD")
    print("Ctrl+C pentru oprire.\n")

    try:
        while True:
            dist_front = get_min_front_distance(sim, sensors, FRONT_SENSORS)

            if state == RobotState.FORWARD:
                if dist_front < STOP_DISTANCE:
                    print(f"[{state.value}] Obstacol detectat la {dist_front:.3f} m -> trece in BACKWARD")
                    state = next_state(state, dist_front)
                    continue

                set_velocity(sim, left_motor, right_motor, V_FORWARD, V_FORWARD)
                print(f"[{state.value}] Mers inainte | dist_front={dist_front:.3f} m")
                time.sleep(0.05)

            elif state == RobotState.BACKWARD:
                print(f"[{state.value}] Da inapoi {BACKWARD_TIME:.1f}s")
                set_velocity(sim, left_motor, right_motor, V_BACKWARD, V_BACKWARD)
                time.sleep(BACKWARD_TIME)

                set_velocity(sim, left_motor, right_motor, 0.0, 0.0)
                turn_direction = random.choice(["left", "right"])
                print(f"[{state.value}] Urmeaza viraj aleatoriu: {turn_direction}")

                state = next_state(state, dist_front)

            elif state == RobotState.TURNING:
                print(f"[{state.value}] Vireaza {turn_direction} timp de {TURN_TIME:.1f}s")

                if turn_direction == "left":
                    set_velocity(sim, left_motor, right_motor, -V_TURN, V_TURN)
                else:
                    set_velocity(sim, left_motor, right_motor, V_TURN, -V_TURN)

                time.sleep(TURN_TIME)
                set_velocity(sim, left_motor, right_motor, 0.0, 0.0)

                state = next_state(state, dist_front)

    except KeyboardInterrupt:
        print("\nOprire manuala.")

    finally:
        set_velocity(sim, left_motor, right_motor, 0.0, 0.0)
        sim.stopSimulation()
        print("Simulare oprita.")


if __name__ == "__main__":
    main()
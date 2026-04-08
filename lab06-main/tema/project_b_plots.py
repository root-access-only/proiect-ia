"""
Tema B - Genereaza graficele din log_braitenberg.csv
1. Traiectorie XY
2. Viteze in timp
3. Heatmap senzori
"""

import csv
import os
import numpy as np
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "log_braitenberg.csv")

TRAJ_PATH = os.path.join(BASE_DIR, "grafic_traseu_xy.png")
VEL_PATH = os.path.join(BASE_DIR, "grafic_viteze_timp.png")
HEATMAP_PATH = os.path.join(BASE_DIR, "grafic_heatmap_senzori.png")


def read_csv_data(csv_path):
    timestamps = []
    v_left = []
    v_right = []
    sensor_matrix = [[] for _ in range(8)]
    pos_x = []
    pos_y = []

    with open(csv_path, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            timestamps.append(float(row["timestamp"]))
            v_left.append(float(row["v_left"]))
            v_right.append(float(row["v_right"]))

            for i in range(8):
                sensor_matrix[i].append(float(row[f"s{i}"]))

            pos_x.append(float(row["pos_x"]))
            pos_y.append(float(row["pos_y"]))

    return timestamps, v_left, v_right, sensor_matrix, pos_x, pos_y


def plot_trajectory(pos_x, pos_y, out_path):
    plt.figure(figsize=(7, 6))
    plt.plot(pos_x, pos_y)
    plt.xlabel("X [m]")
    plt.ylabel("Y [m]")
    plt.title("Traiectoria robotului in planul XY")
    plt.axis("equal")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_velocities(timestamps, v_left, v_right, out_path):
    plt.figure(figsize=(9, 5))
    plt.plot(timestamps, v_left, label="v_left")
    plt.plot(timestamps, v_right, label="v_right")
    plt.xlabel("Timp [s]")
    plt.ylabel("Viteza [rad/s]")
    plt.title("Vitezele rotilor in functie de timp")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_sensor_heatmap(sensor_matrix, timestamps, out_path):
    data = np.array(sensor_matrix)

    plt.figure(figsize=(10, 5))
    plt.imshow(data, aspect="auto", origin="lower")
    plt.colorbar(label="Activare senzor")
    plt.yticks(range(8), [f"s{i}" for i in range(8)])

    if len(timestamps) > 1:
        x_positions = np.linspace(0, len(timestamps) - 1, num=min(10, len(timestamps)), dtype=int)
        x_labels = [f"{timestamps[i]:.1f}" for i in x_positions]
        plt.xticks(x_positions, x_labels)

    plt.xlabel("Timp [s]")
    plt.ylabel("Senzori")
    plt.title("Heatmap activare senzori s0-s7")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def main():
    if not os.path.exists(CSV_PATH):
        print(f"Nu exista fisierul CSV: {CSV_PATH}")
        print("Ruleaza mai intai tema_b_logging.py")
        return

    timestamps, v_left, v_right, sensor_matrix, pos_x, pos_y = read_csv_data(CSV_PATH)

    if not timestamps:
        print("CSV-ul este gol.")
        return

    plot_trajectory(pos_x, pos_y, TRAJ_PATH)
    plot_velocities(timestamps, v_left, v_right, VEL_PATH)
    plot_sensor_heatmap(sensor_matrix, timestamps, HEATMAP_PATH)

    print("Grafice generate:")
    print(TRAJ_PATH)
    print(VEL_PATH)
    print(HEATMAP_PATH)


if __name__ == "__main__":
    main()
import numpy as np
import time
# --- Crearea array-urilor ---
print("=== Crearea array-urilor ===")
arr_1d = np.array([3, 1, 4, 1, 5, 9, 2, 6])
arr_2d = np.arange(1, 13).reshape(3, 4) # matrice 3×4 cu valorile 1..12
print(f"Array 1D: {arr_1d}")
print(f"Array 2D:\n{arr_2d}")
print(f"Forma 2D: {arr_2d.shape}, Tip: {arr_2d.dtype}")
# --- Operații statistice ---
print("\n=== Statistici descriptive ===")
print(f"Medie arr_1d: {np.mean(arr_1d):.2f}")
print(f"Deviație standard arr_1d: {np.std(arr_1d):.2f}")
print(f"Min / Max: {np.min(arr_1d)} / {np.max(arr_1d)}")
print(f"Suma pe coloane (axis=0): {np.sum(arr_2d, axis=0)}")
print(f"Suma pe linii (axis=1): {np.sum(arr_2d, axis=1)}")
# --- Operații vectorizate ---
print("\n=== Operații vectorizate ===")
x = np.linspace(0, 2 * np.pi, 5)
print(f"x = {x.round(3)}")
print(f"sin(x) = {np.sin(x).round(3)}")
# Normalizare Min-Max: scalează valorile în intervalul [0, 1]
date = np.array([10.0, 20.0, 30.0, 40.0, 50.0])
normalizat = (date - date.min()) / (date.max() - date.min())
print(f"\nDate originale: {date}")
print(f"Date normalizate: {normalizat}")
# --- Comparație performanță: liste vs. NumPy ---
print("\n=== Comparație performanță ===")
n = 1_000_000
# Liste Python
lista = list(range(n))
start = time.perf_counter()
suma_lista = sum(val * val for val in lista)
timp_lista = time.perf_counter() - start
# NumPy
arr = np.arange(n)
start = time.perf_counter()
suma_numpy = np.sum(arr ** 2)
timp_numpy = time.perf_counter() - start
print(f"Liste Python: {timp_lista:.4f}s")
print(f"NumPy: {timp_numpy:.4f}s")
print(f"Factor de accelerare: {timp_lista / timp_numpy:.1f}x")
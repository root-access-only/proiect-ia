import numpy as np


print("=== Generare matrice aleatoare ===")
np.random.seed(42)
A = np.random.randint(1, 11, size=(4, 3))
B = np.random.randint(1, 11, size=(3, 5))
print(f"Matricea A (4x3):\n{A}")
print(f"\nMatricea B (3x5):\n{B}")

print("\n=== Produsul matriceal C = A @ B ===")
C = A @ B
print(f"Matricea C (4x5):\n{C}")

print("\n=== Statistici pe matricea C ===")
print(f"Suma tuturor elementelor: {np.sum(C)}")
print(f"Media pe fiecare coloana (axis=0): {np.mean(C, axis=0)}")
print(f"Valoarea maxima globala: {np.max(C)}")

print("\n=== Bonus: matrice patrata 3x3 ===")
M = np.random.randint(1, 11, size=(3, 3))
print(f"Matricea M:\n{M}")

det_M = np.linalg.det(M)
print(f"\nDeterminantul lui M: {det_M:.2f}")

inv_M = np.linalg.inv(M)
print(f"\nInversa lui M:\n{inv_M.round(4)}")

produs = M @ inv_M
print(f"\nM @ inv(M):\n{produs.round(4)}")
print(f"M @ inv(M) ≈ I? {np.allclose(produs, np.eye(3))}")
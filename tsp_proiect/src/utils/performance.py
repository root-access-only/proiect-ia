import time
import random
import matplotlib.pyplot as plt
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.utils.backtracking import rezolva_tsp_backtracking
from hill_climbing_tsp import rezolva_tsp_hc

def genereaza_matrice_simetrica(n, seed=42):
    random.seed(seed)
    matrice = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            val = random.randint(1, 100)
            matrice[i][j] = val
            matrice[j][i] = val
    return matrice

def ruleaza_experiment():
    valori_n_bt = [5, 7, 8, 10, 12]
    valori_n_hc = [5, 7, 8, 10, 12, 15, 20, 30, 50]

    timpi_bt = []
    timpi_hc = []

    for n in valori_n_hc:
        matrice = genereaza_matrice_simetrica(n)
        
        start_hc = time.perf_counter()
        rezolva_tsp_hc(n, matrice, 10)
        timpi_hc.append(time.perf_counter() - start_hc)

        if n in valori_n_bt:
            start_bt = time.perf_counter()
            rezolva_tsp_backtracking(n, matrice)
            timpi_bt.append(time.perf_counter() - start_bt)

    plt.figure(figsize=(12, 5))

    plt.subplot(1, 2, 1)
    plt.plot(valori_n_bt, timpi_bt, label='Backtracking', marker='o')
    plt.plot(valori_n_hc, timpi_hc, label='Hill Climbing', marker='s')
    plt.xlabel('Numar orase (N)')
    plt.ylabel('Timp (secunde)')
    plt.title('Performanta (Scara liniara)')
    plt.legend()

    plt.subplot(1, 2, 2)
    plt.semilogy(valori_n_bt, timpi_bt, label='Backtracking', marker='o')
    plt.semilogy(valori_n_hc, timpi_hc, label='Hill Climbing', marker='s')
    plt.xlabel('Numar orase (N)')
    plt.ylabel('Timp (secunde)')
    plt.title('Performanta (Scara logaritmica)')
    plt.legend()

    plt.tight_layout()
    plt.savefig('comparare_performanta.png')
    print("Grafic salvat ca 'comparare_performanta.png'.")
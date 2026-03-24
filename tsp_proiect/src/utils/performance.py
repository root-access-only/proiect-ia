import sys
import os
import random
import time
import matplotlib.pyplot as plt

from backtracking import rezolva_tsp_backtracking
from nearest_neighbor import rezolva_tsp_nn_multistart
from io_utils import genereaza_matrice_aleatorie

# Importa Hill Climbing din directorul parinte (src/)
HC_DISPONIBIL = False
try:
    src_dir = os.path.join(os.path.dirname(__file__), '..')
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)
    
    from hill_climbing_tsp import rezolva_tsp_hc
    HC_DISPONIBIL = True
    print("[INFO] Hill Climbing importat cu succes\n")
except ImportError as e:
    print(f"[AVIZ] Hill Climbing nu disponibil: {e}\n")
    HC_DISPONIBIL = False


def masoara_timp_bt_prima(n, matrice):
    """Masoara timpul pentru BT modul 'prima'."""
    start = time.perf_counter()
    rezolva_tsp_backtracking(n, matrice, mod='prima')
    return time.perf_counter() - start


def masoara_timp_bt_y(n, matrice):
    """Masoara timpul pentru BT modul 'y_solutii' cu y=n."""
    start = time.perf_counter()
    rezolva_tsp_backtracking(n, matrice, mod='y_solutii', y_max=n)
    return time.perf_counter() - start


def masoara_timp_nn(n, matrice):
    """Masoara timpul pentru NN multistart."""
    start = time.perf_counter()
    rezolva_tsp_nn_multistart(n, matrice)
    return time.perf_counter() - start


def masoara_timp_hc(n, matrice, reporniri=20):
    """Masoara timpul pentru Hill Climbing."""
    if not HC_DISPONIBIL:
        return None

    try:
        start = time.perf_counter()
        result = rezolva_tsp_hc(n, matrice, reporniri)
        
        # Verifica daca rezultatul e valid
        if result is None or (isinstance(result, tuple) and result[0] is None):
            return None
        
        durata = time.perf_counter() - start
        return durata
    except Exception as e:
        print(f"      [EROARE HC la N={n}]: {type(e).__name__}: {e}")
        return None

def ruleaza_experiment():
    """Ruleaza experimentul comparativ - timpi de executie BT vs NN vs HC.

    Genereaza grafice cu timpii pentru diferite dimensiuni ale problemei.
    """
    valori_n_bt = [5, 8, 10, 12]
    valori_n_nn_hc = [5, 8, 10, 12, 15, 20, 30, 50]

    timpi_bt_prima = []
    timpi_bt_y = []
    timpi_nn = []
    timpi_hc = []

    print("=" * 70)
    print("PORNIRE EXPERIMENT COMPARATIV - PERFORMANTA ALGORITMI TSP")
    print("=" * 70)
    print()

    # ===== BACKTRACKING - PRIMA SOLUTIE =====
    print("1. BACKTRACKING - Modul 'prima'")
    print("-" * 70)
    for n in valori_n_bt:
        matrice = genereaza_matrice_aleatorie(n, seed=42)
        durata = masoara_timp_bt_prima(n, matrice)
        timpi_bt_prima.append(durata)
        print(f"   N={n:2d}: {durata:12.9f}s")
    print()

    # ===== BACKTRACKING - Y SOLUTII =====
    print("2. BACKTRACKING - Modul 'y_solutii' (y=n)")
    print("-" * 70)
    for n in valori_n_bt:
        matrice = genereaza_matrice_aleatorie(n, seed=42)
        durata = masoara_timp_bt_y(n, matrice)
        timpi_bt_y.append(durata)
        print(f"   N={n:2d}: {durata:12.9f}s")
    print()

    # ===== NEAREST NEIGHBOR =====
    print("3. NEAREST NEIGHBOR - Multistart")
    print("-" * 70)
    for n in valori_n_nn_hc:
        matrice = genereaza_matrice_aleatorie(n, seed=42)
        durata = masoara_timp_nn(n, matrice)
        timpi_nn.append(durata)
        print(f"   N={n:2d}: {durata:12.9f}s")
    print()

    # ===== HILL CLIMBING =====
    if HC_DISPONIBIL:
        print("4. HILL CLIMBING - 20 reporniri")
        print("-" * 70)
        for n in valori_n_nn_hc:
            matrice = genereaza_matrice_aleatorie(n, seed=42)
            durata = masoara_timp_hc(n, matrice, reporniri=20)
            
            if durata is not None:
                timpi_hc.append(durata)
                print(f"   N={n:2d}: {durata:12.9f}s")
            else:
                print(f"   N={n:2d}: SKIPAT (HC nu disponibil sau eroare)")
                timpi_hc.append(0)  # Adauga 0 pentru a pastra indexii
        print()
    else:
        print("4. HILL CLIMBING - NU ESTE DISPONIBIL")
        print("-" * 70)
        print("   (hill_climbing_tsp.py nu a putut fi gasit in src/)")
        print()

    # ===== GENERARE GRAFICE =====
    print("=" * 70)
    print("GENERARE GRAFICE...")
    print("=" * 70)

    if HC_DISPONIBIL and timpi_hc:
        genereaza_grafic_complet(valori_n_bt, timpi_bt_prima, timpi_bt_y,
                                 valori_n_nn_hc, timpi_nn, timpi_hc)
    else:
        genereaza_grafic_fara_hc(valori_n_bt, timpi_bt_prima, timpi_bt_y,
                                 valori_n_nn_hc, timpi_nn)

    print("\nGrafice salvate:")
    if HC_DISPONIBIL and timpi_hc:
        print("  - comparare_performanta_completa.png")
    else:
        print("  - comparare_performanta.png")


def genereaza_grafic_fara_hc(valori_n_bt, timpi_bt_prima, timpi_bt_y,
                              valori_n_nn, timpi_nn):
    """Genereaza grafic BT vs NN (fara HC)."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))

    # Subplot 1: Scara liniara
    ax1.plot(valori_n_bt, timpi_bt_prima, 'o-', label='BT (prima)', 
             linewidth=2.5, markersize=8, color='#e74c3c')
    ax1.plot(valori_n_bt, timpi_bt_y, 's-', label='BT (y_solutii)',
             linewidth=2.5, markersize=8, color='#c0392b')
    ax1.plot(valori_n_nn, timpi_nn, '^-', label='NN multistart',
             linewidth=2.5, markersize=8, color='#27ae60')

    ax1.set_xlabel('Numarul de orase (N)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Timp de executie (secunde)', fontsize=12, fontweight='bold')
    ax1.set_title('Comparare Performanta - Scara Liniara', fontsize=13, fontweight='bold')
    ax1.legend(fontsize=11, loc='upper left')
    ax1.grid(True, alpha=0.3, linestyle='--')

    # Subplot 2: Scara logaritmica
    ax2.semilogy(valori_n_bt, timpi_bt_prima, 'o-', label='BT (prima)',
                 linewidth=2.5, markersize=8, color='#e74c3c')
    ax2.semilogy(valori_n_bt, timpi_bt_y, 's-', label='BT (y_solutii)',
                 linewidth=2.5, markersize=8, color='#c0392b')
    ax2.semilogy(valori_n_nn, timpi_nn, '^-', label='NN multistart',
                 linewidth=2.5, markersize=8, color='#27ae60')

    ax2.set_xlabel('Numarul de orase (N)', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Timp de executie (secunde, scara log)', fontsize=12, fontweight='bold')
    ax2.set_title('Comparare Performanta - Scara Logaritmica', fontsize=13, fontweight='bold')
    ax2.legend(fontsize=11, loc='upper left')
    ax2.grid(True, alpha=0.3, which='both', linestyle='--')

    plt.tight_layout()
    plt.savefig('comparare_performanta.png', dpi=150, bbox_inches='tight')
    plt.close()


def genereaza_grafic_complet(valori_n_bt, timpi_bt_prima, timpi_bt_y,
                              valori_n_nn_hc, timpi_nn, timpi_hc):
    """Genereaza grafic BT vs NN vs HC (complet)."""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

    # Subplot 1: Scara liniara - toti
    ax1.plot(valori_n_bt, timpi_bt_prima, 'o-', label='BT (prima)',
             linewidth=2.5, markersize=8, color='#e74c3c')
    ax1.plot(valori_n_bt, timpi_bt_y, 's-', label='BT (y_solutii)',
             linewidth=2.5, markersize=8, color='#c0392b')
    ax1.plot(valori_n_nn_hc, timpi_nn, '^-', label='NN multistart',
             linewidth=2.5, markersize=8, color='#27ae60')
    ax1.plot(valori_n_nn_hc, timpi_hc, 'D-', label='HC (20 reporniri)',
             linewidth=2.5, markersize=8, color='#3498db')

    ax1.set_xlabel('Numarul de orase (N)', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Timp de executie (secunde)', fontsize=11, fontweight='bold')
    ax1.set_title('Scara Liniara - Toti Algoritmii', fontsize=12, fontweight='bold')
    ax1.legend(fontsize=10, loc='upper left')
    ax1.grid(True, alpha=0.3, linestyle='--')

    # Subplot 2: Scara logaritmica - toti
    ax2.semilogy(valori_n_bt, timpi_bt_prima, 'o-', label='BT (prima)',
                 linewidth=2.5, markersize=8, color='#e74c3c')
    ax2.semilogy(valori_n_bt, timpi_bt_y, 's-', label='BT (y_solutii)',
                 linewidth=2.5, markersize=8, color='#c0392b')
    ax2.semilogy(valori_n_nn_hc, timpi_nn, '^-', label='NN multistart',
                 linewidth=2.5, markersize=8, color='#27ae60')
    ax2.semilogy(valori_n_nn_hc, timpi_hc, 'D-', label='HC (20 reporniri)',
                 linewidth=2.5, markersize=8, color='#3498db')

    ax2.set_xlabel('Numarul de orase (N)', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Timp de executie (secunde, scara log)', fontsize=11, fontweight='bold')
    ax2.set_title('Scara Logaritmica - Toti Algoritmii', fontsize=12, fontweight='bold')
    ax2.legend(fontsize=10, loc='upper left')
    ax2.grid(True, alpha=0.3, which='both', linestyle='--')

    # Subplot 3: BT comparatie (prima vs y_solutii)
    ax3.plot(valori_n_bt, timpi_bt_prima, 'o-', label='BT (prima)',
             linewidth=2.5, markersize=8, color='#e74c3c')
    ax3.plot(valori_n_bt, timpi_bt_y, 's-', label='BT (y_solutii)',
             linewidth=2.5, markersize=8, color='#c0392b')

    ax3.set_xlabel('Numarul de orase (N)', fontsize=11, fontweight='bold')
    ax3.set_ylabel('Timp de executie (secunde)', fontsize=11, fontweight='bold')
    ax3.set_title('Backtracking - Comparare Moduri', fontsize=12, fontweight='bold')
    ax3.legend(fontsize=10)
    ax3.grid(True, alpha=0.3, linestyle='--')

    # Subplot 4: Metode constructive (NN vs HC)
    ax4.plot(valori_n_nn_hc, timpi_nn, '^-', label='NN multistart',
             linewidth=2.5, markersize=8, color='#27ae60')
    ax4.plot(valori_n_nn_hc, timpi_hc, 'D-', label='HC (20 reporniri)',
             linewidth=2.5, markersize=8, color='#3498db')

    ax4.set_xlabel('Numarul de orase (N)', fontsize=11, fontweight='bold')
    ax4.set_ylabel('Timp de executie (secunde)', fontsize=11, fontweight='bold')
    ax4.set_title('Metode Constructive - NN vs HC', fontsize=12, fontweight='bold')
    ax4.legend(fontsize=10)
    ax4.grid(True, alpha=0.3, linestyle='--')

    plt.tight_layout()
    plt.savefig('comparare_performanta_completa.png', dpi=150, bbox_inches='tight')
    plt.close()


if __name__ == "__main__":
    ruleaza_experiment()
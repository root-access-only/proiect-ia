import sys
import os
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.io_utils import citeste_matrice, afisare_matrice
from utils.backtracking import rezolva_tsp_backtracking
from utils.nearest_neighbor import (rezolva_tsp_nn, rezolva_tsp_nn_multistart, 
                                     rezolva_tsp_nn_timp)

# Incearca sa importe Hill Climbing
try:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from hill_climbing_tsp import rezolva_tsp_hc
    HC_DISPONIBIL = True
except ImportError:
    HC_DISPONIBIL = False


def main():
    """Punct de intrare cu suport pentru algoritmi multipli si moduri de oprire."""
    algoritmi_disponibili = ['bt', 'nn']
    if HC_DISPONIBIL:
        algoritmi_disponibili.append('hc')

    parser = argparse.ArgumentParser(
        description='Rezolvitor TSP cu Backtracking, Hill Climbing si Nearest Neighbor.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Exemple de utilizare:
  python main.py orase.txt --algoritm bt --mod y_solutii --y 10
  python main.py orase.txt --algoritm nn
  python main.py orase.txt --algoritm bt --mod timp --timp 30
  python main.py orase.txt --algoritm hc
        """
    )

    parser.add_argument('fisier', help='Fisierul de intrare cu matricea de distante')
    parser.add_argument('--algoritm', choices=algoritmi_disponibili, default='bt',
                        help='Algoritmul de utilizat (implicit: bt)')
    parser.add_argument('--mod', choices=['prima', 'toate', 'timp', 'y_solutii'],
                        default='toate', help='Modul de oprire pentru BT (implicit: toate)')
    parser.add_argument('--timp', type=float, default=60,
                        help='Durata maxima pentru modul timp (secunde)')
    parser.add_argument('--y', type=int, default=10,
                        help='Numarul maxim de solutii pentru modul y_solutii')
    parser.add_argument('--hc-reporniri', type=int, default=20,
                        help='Numarul de reporniri pentru Hill Climbing (implicit 20)')
    parser.add_argument('--afisare-matrice', action='store_true',
                        help='Afiseaza matricea de distante')

    args = parser.parse_args()

    # Gaseste si citeste fisierul
    if not os.path.exists(args.fisier):
        alt_cale = os.path.join('..', args.fisier)
        if os.path.exists(alt_cale):
            args.fisier = alt_cale
        else:
            print(f"Eroare: Fisierul '{args.fisier}' nu a fost gasit!")
            sys.exit(1)

    try:
        n, matrice = citeste_matrice(args.fisier)
    except (FileNotFoundError, ValueError) as e:
        print(f"Eroare: {e}")
        sys.exit(1)

    print(f"{'='*60}")
    print(f"Rezolvitor TSP - {args.algoritm.upper()}")
    print(f"{'='*60}")
    print(f"Numar de orase: {n}")
    print(f"Fisier: {args.fisier}\n")

    if args.afisare_matrice:
        afisare_matrice(matrice)

    # ===== BACKTRACKING =====
    if args.algoritm == 'bt':
        print(f"Modul de oprire: '{args.mod}'")
        if args.mod == 'timp':
            print(f"Timp maxim: {args.timp}s")
        elif args.mod == 'y_solutii':
            print(f"Solutii maxime: {args.y}")
        print()

        traseu, cost, nr_sol, durata = rezolva_tsp_backtracking(
            n, matrice, args.mod, args.timp, args.y)

        print(f"REZULTATE BACKTRACKING:")
        print(f"{'─'*60}")
        if traseu:
            sir_traseu = ' -> '.join(map(str, traseu)) + f' -> {traseu[0]}'
            print(f"Traseu optim: {sir_traseu}")
            print(f"Cost minim:   {cost}")
        else:
            print(f"Traseu:       Nu s-a gasit solutie")
            print(f"Cost:         inf")
        print(f"Solutii gasite: {nr_sol}")
        print(f"Timp executie: {durata:.6f}s")
        print()

    # ===== NEAREST NEIGHBOR =====
    elif args.algoritm == 'nn':
        print("Multistart NN (toți starturile)")
        print()

        traseu, cost, toate_costurile = rezolva_tsp_nn_multistart(n, matrice)

        print(f"REZULTATE NEAREST NEIGHBOR (MULTISTART):")
        print(f"{'─'*60}")
        sir_traseu = ' -> '.join(map(str, traseu)) + f' -> {traseu[0]}'
        print(f"Traseu optim: {sir_traseu}")
        print(f"Cost minim:   {cost}")
        print(f"Costuri pentru fiecare start: {toate_costurile}")
        print()

    # ===== HILL CLIMBING =====
    elif args.algoritm == 'hc':
        if not HC_DISPONIBIL:
            print("Eroare: Hill Climbing nu este disponibil.")
            print("Asigurati-va ca hill_climbing_tsp.py exista in directorul proiectului.")
            sys.exit(1)

        print(f"Numar de reporniri: {args.hc_reporniri}")
        print()

        try:
            traseu, cost = rezolva_tsp_hc(n, matrice, args.hc_reporniri)

            print(f"REZULTATE HILL CLIMBING:")
            print(f"{'─'*60}")
            sir_traseu = ' -> '.join(map(str, traseu)) + f' -> {traseu[0]}'
            print(f"Traseu: {sir_traseu}")
            print(f"Cost:   {cost}")
            print()

        except Exception as e:
            print(f"Eroare la executia Hill Climbing: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
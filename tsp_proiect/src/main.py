import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.utils.io_utils import citeste_matrice
from src.utils.backtracking import rezolva_tsp_backtracking
from hill_climbing_tsp import rezolva_tsp_hc
from src.utils.performance import ruleaza_experiment

def main():
    """Punctul de intrare in aplicatie pentru rularea solverelor sau experimentului."""
    if len(sys.argv) > 1 and sys.argv[1] == "exp":
        ruleaza_experiment()
    elif len(sys.argv) == 2:
        fisier = sys.argv[1]
        n, matrice = citeste_matrice(fisier)
        
        traseu_bt, cost_bt = rezolva_tsp_backtracking(n, matrice)
        print(f"Backtracking -> Traseu: {traseu_bt}, Cost: {cost_bt}")
        
        traseu_hc, cost_hc = rezolva_tsp_hc(n, matrice, 20)
        print(f"Hill Climbing -> Traseu: {traseu_hc}, Cost: {cost_hc}")
    else:
        print("Utilizare:")
        print("  Pentru fisier: python src/main.py <fisier_intrare.txt>")
        print("  Pentru grafic: python src/main.py exp")

if __name__ == "__main__":
    main()
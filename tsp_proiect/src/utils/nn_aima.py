"""Implementarea NN pentru TSP folosind biblioteca aima3."""

try:
    from aima3.search import nearest_neighbor_tsp
except ImportError:
    nearest_neighbor_tsp = None


def rezolva_tsp_nn_aima(n, matrice, start=0):
    """Nearest Neighbor cu aima3 - o singura rulare.

    Args:
        n: Numarul de orase (int).
        matrice: Matricea de distante NxN (lista de liste).
        start: Indexul orasului de plecare (implicit 0).

    Returns:
        Tuplu (traseu, cost) unde traseu este lista de indici,
        cost este costul total al turului (int).

    Raises:
        ImportError: Daca aima3 nu este instalat.
    """
    if nearest_neighbor_tsp is None:
        raise ImportError("aima3 nu este instalat. Ruleaza: pip install aima3")

    # Prepara datele in formatul cerut de aima3
    cities = list(range(n))
    distances = {}

    for i in range(n):
        distances[i] = {}
        for j in range(n):
            distances[i][j] = matrice[i][j]

    # Apeleaza functia din aima3
    traseu = nearest_neighbor_tsp(start, cities, distances)

    # Calculeaza costul
    cost = 0
    for i in range(len(traseu)):
        oras_curent = traseu[i]
        oras_urmator = traseu[(i + 1) % len(traseu)]
        cost += matrice[oras_curent][oras_urmator]

    return traseu, cost


def rezolva_tsp_nn_aima_multistart(n, matrice):
    """Nearest Neighbor cu aima3 - multistart (toti starturile).

    Args:
        n: Numarul de orase (int).
        matrice: Matricea de distante NxN (lista de liste).

    Returns:
        Tuplu (best_traseu, best_cost, toate_costurile).
    """
    best_traseu = None
    best_cost = float('inf')
    toate_costurile = []

    for start in range(n):
        traseu, cost = rezolva_tsp_nn_aima(n, matrice, start)
        toate_costurile.append(cost)

        if cost < best_cost:
            best_cost = cost
            best_traseu = traseu

    return best_traseu, best_cost, toate_costurile
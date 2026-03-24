"""Implementarea manuala a euristicii celui mai apropiat vecin pentru TSP."""

import time


def rezolva_tsp_nn(n, matrice, start=0):
    """Nearest Neighbor de baza - o singura rulare dintr-un punct de start.

    Args:
        n: Numarul de orase (int).
        matrice: Matricea de distante NxN (lista de liste).
        start: Indexul orasului de plecare (implicit 0).

    Returns:
        Tuplu (traseu, cost) unde traseu este lista de indici in ordinea
        vizitarii, iar cost este costul total al turului (int).
    """
    vizitat = [False] * n
    traseu = [start]
    vizitat[start] = True
    cost_total = 0
    oras_curent = start

    for _ in range(n - 1):
        cel_mai_apropiat = -1
        dist_min = float('inf')

        for urmator in range(n):
            if not vizitat[urmator] and matrice[oras_curent][urmator] < dist_min:
                dist_min = matrice[oras_curent][urmator]
                cel_mai_apropiat = urmator

        cost_total += dist_min
        traseu.append(cel_mai_apropiat)
        vizitat[cel_mai_apropiat] = True
        oras_curent = cel_mai_apropiat

    cost_total += matrice[oras_curent][start]
    return traseu, cost_total


def rezolva_tsp_nn_multistart(n, matrice):
    """Nearest Neighbor multistart - ruleaza din fiecare oras de start.

    Args:
        n: Numarul de orase (int).
        matrice: Matricea de distante NxN (lista de liste).

    Returns:
        Tuplu (best_traseu, best_cost, toate_costurile) unde best_traseu este
        lista cu traseul optimal gasit, best_cost este costul acestuia (int),
        si toate_costurile este o lista cu costurile pentru fiecare start.
    """
    best_traseu = None
    best_cost = float('inf')
    toate_costurile = []

    for start in range(n):
        traseu, cost = rezolva_tsp_nn(n, matrice, start)
        toate_costurile.append(cost)

        if cost < best_cost:
            best_cost = cost
            best_traseu = traseu

    return best_traseu, best_cost, toate_costurile


def rezolva_tsp_nn_timp(n, matrice, timp_max):
    """Nearest Neighbor cu limita de timp - ruleaza de la mai multe starturi pana la timp_max.

    Args:
        n: Numarul de orase (int).
        matrice: Matricea de distante NxN (lista de liste).
        timp_max: Durata maxima de executie in secunde (float).

    Returns:
        Tuplu (best_traseu, best_cost, nr_starturi) unde best_traseu este
        traseul optimal gasit, best_cost este costul acestuia, iar nr_starturi
        este numarul de starturi rulate in timp_max.
    """
    best_traseu = None
    best_cost = float('inf')
    start_timp = time.perf_counter()
    nr_starturi = 0

    for start in range(n):
        if time.perf_counter() - start_timp >= timp_max:
            break

        traseu, cost = rezolva_tsp_nn(n, matrice, start)
        nr_starturi += 1

        if cost < best_cost:
            best_cost = cost
            best_traseu = traseu

    return best_traseu, best_cost, nr_starturi
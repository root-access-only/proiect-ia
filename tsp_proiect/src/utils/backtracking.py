"""Rezolvarea TSP prin backtracking cu 4 moduri configurabile de oprire."""

import time
import sys


def rezolva_tsp_backtracking(n, matrice, mod='toate', timp_max=None, y_max=None):
    """Backtracking cu moduri de oprire: 'prima', 'toate', 'timp', 'y_solutii'.

    Args:
        n: Numarul de orase (int).
        matrice: Matricea de distante NxN (lista de liste).
        mod: Modul de oprire - 'prima', 'toate', 'timp', 'y_solutii' (str).
        timp_max: Pentru modul 'timp' - durata maxima in secunde (float).
        y_max: Pentru modul 'y_solutii' - numarul maxim de solutii (int).

    Returns:
        Tuplu (traseu_optim, cost_minim, nr_solutii, durata_exec) unde traseu_optim
        este lista de indici, cost_minim este costul (int), nr_solutii este numarul
        de tururi complete gasite, durata_exec este timp in secunde (float).
    """
    state = {
        'cost_minim': sys.maxsize,
        'traseu_optim': [],
        'nr_solutii': 0,
        'oprire': False,
        'timp_start': time.perf_counter()
    }

    vizitat = [False] * n
    vizitat[0] = True

    start_timp = time.perf_counter()
    _backtracking_recursiv(matrice, n, 0, vizitat, [0], 0, state, mod, timp_max, y_max)
    durata = time.perf_counter() - start_timp

    return state['traseu_optim'], state['cost_minim'], state['nr_solutii'], durata


def _backtracking_recursiv(matrice, n, oras_curent, vizitat, traseu, cost, state, 
                            mod, timp_max, y_max):
    """Functia recursiva interna pentru backtracking."""
    if state['oprire']:
        return

    if len(traseu) == n:
        cost_total = cost + matrice[oras_curent][traseu[0]]
        state['nr_solutii'] += 1

        if cost_total < state['cost_minim']:
            state['cost_minim'] = cost_total
            state['traseu_optim'] = traseu[:]

        if mod == 'prima':
            state['oprire'] = True
        elif mod == 'y_solutii' and state['nr_solutii'] >= y_max:
            state['oprire'] = True

        return

    for urmator in range(n):
        if state['oprire']:
            return

        if vizitat[urmator]:
            continue

        if mod == 'timp':
            timp_curent = time.perf_counter()
            if timp_curent - state['timp_start'] >= timp_max:
                state['oprire'] = True
                return

        cost_nou = cost + matrice[oras_curent][urmator]

        if mod in ['toate', 'prima', 'y_solutii']:
            if cost_nou >= state['cost_minim']:
                continue

        vizitat[urmator] = True
        traseu.append(urmator)

        _backtracking_recursiv(matrice, n, urmator, vizitat, traseu, cost_nou,
                               state, mod, timp_max, y_max)

        traseu.pop()
        vizitat[urmator] = False
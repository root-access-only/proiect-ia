import sys

def rezolva_tsp_backtracking(n, matrice):
    stare = {'cost_minim': sys.maxsize, 'traseu_optim': []}

    def _backtrack(oras_curent, vizitat, traseu, cost):
        if len(traseu) == n:
            cost_total = cost + matrice[oras_curent][traseu[0]]
            if cost_total < stare['cost_minim']:
                stare['cost_minim'] = cost_total
                stare['traseu_optim'] = traseu[:]
            return

        for urmator in range(n):
            if not vizitat[urmator]:
                cost_nou = cost + matrice[oras_curent][urmator]
                if cost_nou >= stare['cost_minim']:
                    continue
                vizitat[urmator] = True
                traseu.append(urmator)
                _backtrack(urmator, vizitat, traseu, cost_nou)
                traseu.pop()
                vizitat[urmator] = False

    vizitat = [False] * n
    vizitat[0] = True
    _backtrack(0, vizitat, [0], 0)
    return stare['traseu_optim'], stare['cost_minim']
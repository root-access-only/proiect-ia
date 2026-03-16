from simpleai.search import SearchProblem, hill_climbing_random_restarts

class TSPHillClimbing(SearchProblem):

    def __init__(self, initial_state, matrice):
        super().__init__(initial_state=initial_state)
        self.matrice = matrice
        self.n = len(matrice)

    def actions(self, state):
        acts = []
        for i in range(self.n - 1):
            for j in range(i + 1, self.n):
                acts.append((i, j))
        return acts

    def result(self, state, action):
        i, j = action
        lst = list(state)
        lst[i:j+1] = reversed(lst[i:j+1])
        return tuple(lst)

    def value(self, state):
        cost = 0
        for i in range(self.n - 1):
            cost += self.matrice[state[i]][state[i+1]]
        cost += self.matrice[state[-1]][state[0]]
        return -cost

def rezolva_tsp_hc(n, matrice, reporniri=10):
    initial = tuple(range(n))
    problema = TSPHillClimbing(initial, matrice)
    rezultat = hill_climbing_random_restarts(problema, restarts_limit=reporniri)
    return list(rezultat.state), -rezultat.value
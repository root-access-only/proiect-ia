from simpleai.search import hill_climbing_random_restarts, SearchProblem

class TSPHillClimbing(SearchProblem):
    def __init__(self, n, matrice):
        self.n = n
        self.matrice = matrice
        initial_state = tuple(range(n))
        super().__init__(initial_state)

    def generate_random_state(self):
        import random
        state = list(range(self.n))
        random.shuffle(state)
        return tuple(state)

    def actions(self, state):
        act = []
        for i in range(self.n):
            for j in range(i+1, self.n):
                act.append((i, j))
        return act

    def result(self, state, action):
        i, j = action
        lst = list(state)
        lst[i:j+1] = reversed(lst[i:j+1])
        return tuple(lst)

    def value(self, state):
        cost = 0
        for i in range(self.n-1):
            cost += self.matrice[state[i]][state[i+1]]
        cost += self.matrice[state[-1]][state[0]]
        return -cost

def rezolva_tsp_hc(n, matrice, reporniri):
    problem = TSPHillClimbing(n, matrice)
    result = hill_climbing_random_restarts(problem, restarts_limit=reporniri, iterations_limit=1000)
    traseu = list(result.state)
    cost = -problem.value(result.state)
    return traseu, cost

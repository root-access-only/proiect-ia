"""Genetic algorithm for TSP using Order Crossover (OX) and swap mutation."""
from __future__ import annotations

import random
from typing import Sequence

from .common import TSPResult, now, tour_cost


def _ox_crossover(p1: list[int], p2: list[int], rng: random.Random) -> list[int]:
    """Order Crossover (Davis, 1985) - produces a valid permutation child."""
    n = len(p1)
    a, b = sorted(rng.sample(range(n), 2))
    child = [-1] * n
    child[a:b + 1] = p1[a:b + 1]
    used = set(child[a:b + 1])
    fill = [g for g in p2 if g not in used]
    k = 0
    for i in range(n):
        if child[i] == -1:
            child[i] = fill[k]
            k += 1
    return child


def _swap_mutation(child: list[int], rate: float, rng: random.Random) -> list[int]:
    if rng.random() < rate:
        i, j = rng.sample(range(len(child)), 2)
        child[i], child[j] = child[j], child[i]
    return child


def _tournament(population: list[list[int]], costs: list[float], k: int, rng: random.Random) -> list[int]:
    competitors = rng.sample(range(len(population)), min(k, len(population)))
    winner = min(competitors, key=lambda idx: costs[idx])
    return population[winner][:]


def _roulette(population: list[list[int]], costs: list[float], rng: random.Random) -> list[int]:
    max_c = max(costs)
    weights = [(max_c - c) + 1e-9 for c in costs]
    total = sum(weights)
    r = rng.uniform(0, total)
    cumulative = 0.0
    for idx, w in enumerate(weights):
        cumulative += w
        if cumulative >= r:
            return population[idx][:]
    return population[-1][:]


def solve_ga(
    matrix: Sequence[Sequence[float]],
    population_size: int = 100,
    generations: int = 200,
    mutation_rate: float = 0.1,
    crossover_rate: float = 0.9,
    elitism: int = 2,
    selection: str = "tournament",
    tournament_k: int = 5,
    seed: int | None = None,
) -> TSPResult:
    """Genetic algorithm with Order Crossover and swap mutation.

    Args:
        matrix: Symmetric NxN distance matrix.
        population_size: Number of individuals per generation.
        generations: Number of evolution iterations.
        mutation_rate: Per-individual probability of a swap mutation.
        crossover_rate: Probability of producing a child via crossover.
        elitism: Number of best individuals carried over each generation.
        selection: ``"tournament"`` or ``"roulette"``.
        tournament_k: Tournament size for tournament selection.
        seed: RNG seed for reproducibility.

    Returns:
        ``TSPResult`` with one history entry per generation.
    """
    rng = random.Random(seed)
    n = len(matrix)
    if n == 0:
        return TSPResult("GA", [], 0.0, 0.0, 0, [], {})

    t0 = now()

    population = []
    for _ in range(population_size):
        ind = list(range(n))
        rng.shuffle(ind)
        population.append(ind)
    costs = [tour_cost(ind, matrix) for ind in population]

    best_idx = min(range(population_size), key=lambda i: costs[i])
    best_tour = population[best_idx][:]
    best_cost = costs[best_idx]
    history = [(0, best_cost)]

    for gen in range(1, generations + 1):
        order = sorted(range(population_size), key=lambda i: costs[i])
        elites = [population[i][:] for i in order[:elitism]]

        children: list[list[int]] = list(elites)
        while len(children) < population_size:
            if selection == "roulette":
                p1 = _roulette(population, costs, rng)
                p2 = _roulette(population, costs, rng)
            else:
                p1 = _tournament(population, costs, tournament_k, rng)
                p2 = _tournament(population, costs, tournament_k, rng)
            if rng.random() < crossover_rate:
                child = _ox_crossover(p1, p2, rng)
            else:
                child = p1[:]
            child = _swap_mutation(child, mutation_rate, rng)
            children.append(child)

        population = children[:population_size]
        costs = [tour_cost(ind, matrix) for ind in population]

        idx = min(range(population_size), key=lambda i: costs[i])
        if costs[idx] < best_cost:
            best_cost = costs[idx]
            best_tour = population[idx][:]
        history.append((gen, best_cost))

    return TSPResult(
        algorithm="GA",
        tour=best_tour,
        cost=best_cost,
        elapsed=now() - t0,
        iterations=generations,
        history=history,
        params={
            "population_size": population_size,
            "generations": generations,
            "mutation_rate": mutation_rate,
            "crossover_rate": crossover_rate,
            "elitism": elitism,
            "selection": selection,
            "tournament_k": tournament_k,
            "seed": seed,
        },
    )

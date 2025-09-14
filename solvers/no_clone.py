# -------------------------------------------------
# DON'T CHANGE THIS FILE.
# DFS solver with shortest-subtree-first heuristic (by weight).
#
# __author__ = 'Edward Small'
# __copyright__ = 'Copyright 2025, RMIT University'
# -------------------------------------------------

from graph.coordinate import Coordinate
from graph.graph import Graph
from solvers.util import estimate_subtree_weight, generate_actions_from_paths


def dfs_traverse(graph: Graph, current: Coordinate, visited: set, path: list[Coordinate]) -> bool:
    """
    Recursively traverses the graph using DFS with a shortest-subtree-first heuristic based on total weight.

    At each step, the traversal prioritizes neighbors whose subtrees have the lowest estimated total weight.
    Records the path taken. Movement costs are computed after traversal is complete.

    @param graph: The maze graph to traverse.
    @param current: The current coordinate being explored.
    @param visited: A set of coordinates that have already been visited.
    @param path: A list of coordinates representing the traversal path.

    @return: True if all vertices have been visited and traversal is complete; False otherwise.
    """
    visited.add(current)
    path.append(current)

    if len(visited) == graph.size:
        return True

    unvisited = [
        (neighbor, graph.getWeight(current, neighbor))
        for neighbor in graph.neighbours(current)
        if neighbor not in visited
    ]

    weighted_subtrees = []
    for neighbor, edge_weight in unvisited:
        subtree_weight = estimate_subtree_weight(graph, neighbor, visited.copy())
        weighted_subtrees.append((neighbor, edge_weight, subtree_weight))

    weighted_subtrees.sort(key=lambda x: x[2])  # ascending

    for neighbor, _, _ in weighted_subtrees:
        if dfs_traverse(graph, neighbor, visited, path):
            return True
        path.append(current)  # backtrack

    return False




def no_clone_solver(graph: Graph, start: Coordinate, clone_cost: int) -> tuple[list[Coordinate], int, int]:
    """
    Solves the maze using depth-first search with a shortest-subtree-first heuristic based on estimated weight.

    Starts from the given coordinate and explores the graph recursively, prioritizing lighter subtrees.
    Tracks the path taken and the total cost incurred. This solver does not spawn clones.

    @param graph: The maze graph to solve.
    @param start: The starting coordinate for the traversal.

    @return: A tuple containing:
        - path: The list of coordinates visited during traversal.
        - total_cost: The sum of edge weights traversed.
        - clone_count: Always 0 for this solver (no cloning behavior).
    """

    visited = set()
    path = []

    dfs_traverse(graph, start, visited, path)
    actions = generate_actions_from_paths(graph, [path], clone_cost)
    total_cost = sum(actions[0])

    return [path], total_cost, 0

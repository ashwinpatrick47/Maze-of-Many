# -------------------------------------------------
# DON'T CHANGE THIS FILE.
# Clone-based DFS solver using rule-driven branching.
#
# __author__ = 'Edward Small'
# __copyright__ = 'Copyright 2025, RMIT University'
# -------------------------------------------------

from graph.coordinate import Coordinate
from graph.graph import Graph
from solvers.util import estimate_subtree_weight, generate_actions_from_paths


def explore(graph: Graph, current: Coordinate, visited: set,
            all_paths: list[list[Coordinate]]) -> int:
    """
    Recursively explores the graph using a clone-based depth-first strategy.

    At each branching point, the explorer spawns clones to traverse all but the largest estimated subtree.
    Each explorer maintains its own path. Actions are computed after traversal using a helper function.

    @param graph: The maze graph to traverse.
    @param current: The current location of the explorer.
    @param visited: Shared set of visited coordinates across all explorers.
    @param clone_cost: Fixed cost incurred when spawning a clone.
    @param all_paths: A list of paths taken by each explorer. Each path is a list of Coordinates.

    @return: The total number of clones spawned (equal to len(all_paths) - 1).
    """
    # Assign a new explorer ID based on the current number of paths
    explorer_id = len(all_paths)

    # Initialize this explorer's path with its starting coordinate
    path = [current]

    # Register the new explorer's path
    all_paths.append(path)

    # Mark the starting coordinate as visited
    visited.add(current)

    # Begin exploring until no unvisited neighbors remain
    while True:
        # Gather all unvisited neighbors and their edge weights
        unvisited = [
            (neighbor, graph.getWeight(current, neighbor))
            for neighbor in graph.neighbours(current)
            if neighbor not in visited
        ]

        # If there are no unvisited neighbors, this path is complete
        if not unvisited:
            break

        # If there's only one unvisited neighbor, continue directly (no branching)
        if len(unvisited) == 1:
            neighbor, _ = unvisited[0]
            current = neighbor
            path.append(current)
            visited.add(current)
            continue

        # If multiple unvisited neighbors exist, we’re at a junction — time to evaluate cloning
        subtree_weights = []

        # Estimate the cost of exploring each branch using a heuristic
        for neighbor, _ in unvisited:
            weight = estimate_subtree_weight(graph, neighbor, visited.copy())
            subtree_weights.append((neighbor, weight))

        # Sort branches by estimated subtree weight (ascending)
        # This helps us identify the smallest branches for cloning
        subtree_weights.sort(key=lambda x: x[1])

        # Spawn clones for all but the largest branch
        for clone_neighbor, _ in subtree_weights[:-1]:
            # Mark the clone's starting point as visited
            visited.add(clone_neighbor)

            # Create a new explorer path for the clone
            pre_spawn_index = len(all_paths)

            # Recursively explore the clone's branch
            explore(graph, clone_neighbor, visited, all_paths)

            # Insert the junction coordinate at the start of the clone's path
            # This ensures the clone's path begins at the correct origin
            all_paths[pre_spawn_index].insert(0, current)

        # The original explorer commits to the largest remaining branch
        main_neighbor = subtree_weights[-1][0]
        current = main_neighbor
        path.append(current)
        visited.add(current)

    return len(all_paths) - 1  # total clones = total explorers - 1


def always_clone_solver(graph: Graph, start: Coordinate, clone_cost: int) -> tuple[list[list[Coordinate]], int, int]:
    """
    Executes a full clone-based DFS traversal starting from the given coordinate.

    Spawns clones at each branching point to explore all subtrees in parallel, tracking each explorer's path.
    Movement costs and clone costs are computed after traversal using a helper function.

    @param graph: The maze graph to traverse.
    @param start: The starting coordinate for the original explorer.
    @param clone_cost: Fixed cost incurred each time a clone is spawned.

    @return: A tuple containing:
        - all_paths: A list of paths taken by each explorer (original + clones).
        - max_total_cost: The highest cumulative cost incurred by any explorer (movement + clone costs).
        - clone_count: The total number of clones spawned (equal to len(all_paths) - 1).
    """
    visited = set()
    all_paths = []

    explore(graph, start, visited, all_paths=all_paths)
    all_actions = generate_actions_from_paths(graph, all_paths, clone_cost)
    max_total_cost = max(sum(actions) for actions in all_actions)
    clone_count = len(all_paths) - 1
    return all_paths, max_total_cost, clone_count

# -------------------------------------------------
# EDIT THIS FILE TO IMPLEMENT TASK D.
# Functions for your solver.
#
# __author__ = 'Ashwin Patrick'
# __copyright__ = 'Copyright 2025, RMIT University'
# -------------------------------------------------

from functools import partial
from graph.coordinate import Coordinate
from graph.graph import Graph
from solvers.util import estimate_subtree_weight, dfsBacktrack, generate_actions_from_paths


def _append_if_new(path: list[Coordinate], node: Coordinate) -> None:
    """Helper: append node if it isn’t a duplicate of the last one."""
    if not path or path[-1] != node:
        path.append(node)


def task_d_explore(graph: Graph, current: Coordinate, visited: set,
                   all_paths: list[list[Coordinate]], explorer_id: int = 0,
                   clone_cost: int = 1) -> int:
    """
    Returns a solution to the maze using YOUR exploration strategy. See always_clone and no_clone for inspiration.

    The expectation is that all_paths contains a list of lists. Each list is a traversal that each clone/sorcerer completed
    For example:
    [[Coordinates(0, 0), Coordinates(0, 1), Coordinates(0, 2), Coordinates(1, 2), Coordinates(1, 3), Coordinates(2, 3),
    Coordinates(3, 3), Coordinates(3, 2), Coordinates(2, 2), Coordinates(2, 1), Coordinates(2, 0), Coordinates(3, 0), Coordinates(3, 1)],
    [Coordinates(1, 3), Coordinates(0, 3)],
    [Coordinates(2, 0), Coordinates(1, 0), Coordinates(1, 1)]]

    The above output implies that the original sorcerer walked from (0,0)->(0,1)->...->(1,3)->made a clone->(3,2)->...
    We made 2 clones because we have 3 sets of lists (one original sorcerer and 2 clones). Clones MUST start their
    journey from the exact cell they are made from.

    You only have to handle the path generation - calculating the cost is handled for you via generate_actions_from_paths

    @param graph: The maze graph to traverse. Each node represents a coordinate, and edges have associated weights.
    @param start: The starting coordinate for the original explorer. All traversal begins from this point.
    @param clone_cost: The fixed cost incurred each time a clone is spawned. This cost is added to both the spawner
                       and the clone.

    @return: clone_count: The total number of clones spawned (equal to len(all_paths) - 1).
    """
    if explorer_id == len(all_paths):
        all_paths.append([current])
    else:
        _append_if_new(all_paths[explorer_id], current)

    path = all_paths[explorer_id]
    visited.add(current)

    while True:
        """BE SURE TO LOOK AT THE OTHER SOLVERS FOR INSPIRATION
        
        # HINT: Use graph.neighbours(current) to find adjacent nodes.
        # HINT: Use graph.getWeight(a, b) to get edge weights.
        # HINT: Use estimate_subtree_weight(...) to find the total weight in a sub-tree (branch).
        # HINT: Use dfsBacktrack(...) to return to junctions after exploring branches.
        # HINT: Use all_paths.append([...]) to spawn a new clone path."""
        # Gather all unvisited neighbours with estimated subtree weight
        unvisited = []
        for nbr in graph.neighbours(current):
            if nbr not in visited:
                w = graph.getWeight(current, nbr)
                est = estimate_subtree_weight(graph, nbr, visited.copy())
                unvisited.append((nbr, w, w + est))

        # End of branch
        if not unvisited:
            break

        # Single path — keep going
        if len(unvisited) == 1:
            nbr, w, _ = unvisited[0]
            _append_if_new(path, nbr)
            visited.add(nbr)
            current = nbr
            continue

        # Sort by descending estimated workload
        unvisited.sort(key=lambda t: t[2], reverse=True)
        main_nbr, main_w, main_B = unvisited[0]

        # Cost-aware decision rule
        # side = unvisited[1:]
        # clone_branches  = [(nbr, w, B) for (nbr, w, B) in side if 2 * w > clone_cost]
        # serial_branches = [(nbr, w, B) for (nbr, w, B) in side if 2 * w <= clone_cost]

        # Cost-aware decision rule (hybrid: cost + load + fan-out)
        side = unvisited[1:]

        # Thresholds:
        # - tau_size: how “heavy” a side subtree must be relative to the main branch
        # - tau_cost: how expensive the down-and-back is compared to a clone
        tau_size = 0.6 * main_B
        tau_cost = clone_cost

        # if cloning costs more than backtracking all side branches, disable cloning here
        total_back = sum(2 * w for (_, w, _) in side)
        if clone_cost >= total_back:
            clone_branches  = []
            serial_branches = side
        else:
            # If fan-out is high, protect the lightest side (keep serial) and consider cloning the rest.
            fanout = len(side) >= 3
            protect = set()
            if fanout:
                # Sort sides by estimated load descending; protect the lightest one
                side_sorted = sorted(side, key=lambda t: t[2], reverse=True)
                protect.add(side_sorted[-1][0])  # lightest by B

            clone_branches = []
            serial_branches = []
            for nbr, w, B in side:
                if nbr in protect:
                    serial_branches.append((nbr, w, B))
                    continue

                # Clone if either:
                #  the subtree is heavy relative to the main branch, OR
                #  the round-trip for the entry edge is pricier than a clone.
                if (B >= tau_size) or (2 * w >= tau_cost):
                    clone_branches.append((nbr, w, B))
                else:
                    serial_branches.append((nbr, w, B))




        # Clone branches
        for nbr, _, _ in clone_branches:
            visited.add(nbr)
            pre_idx = len(all_paths)
            all_paths.append([current, nbr])
            task_d_explore(graph, nbr, visited, all_paths, explorer_id=pre_idx, clone_cost=clone_cost)

        # Serial branches
        junction = current
        for nbr, _, _ in serial_branches:
            _append_if_new(path, nbr)
            visited.add(nbr)
            task_d_explore(graph, nbr, visited, all_paths, explorer_id=explorer_id, clone_cost=clone_cost)
            backtrack_path = dfsBacktrack(graph, path[-1], junction)
            if backtrack_path and len(backtrack_path) > 1:
                for node in backtrack_path[1:]:
                    _append_if_new(path, node)
            current = junction

        # Continue along main branch
        _append_if_new(path, main_nbr)
        visited.add(main_nbr)
        current = main_nbr

    return len(all_paths) - 1


def task_d_solver(graph: Graph, start: Coordinate, clone_cost: int) -> tuple[list[list[Coordinate]], int, int]:
    """
    Solves the maze using cost-aware clone-based DFS.

    Spawns clones only when the cost of exploring and returning from a subtree exceeds the clone cost.
    Tracks each explorer's path and actions, and returns the full traversal history.

    @param graph: The maze graph to traverse.
    @param start: The starting coordinate for the original explorer.
    @param clone_cost: Fixed cost incurred each time a clone is spawned.

    @return: A tuple containing:
        - all_paths: A list of paths taken by each explorer (original + clones).
        - max_total_cost: The highest cumulative cost incurred by any explorer (movement + clone costs).
        - clone_count: The total number of clones spawned (equal to len(all_paths) - 1).
    
    
    Solves the maze using cost-aware clone-based DFS.
    """
    # visited = set()
    # all_paths = []

    # # Use partial to inject clone_cost into recursive calls without globals
    # explore_with_cost = partial(task_d_explore, clone_cost=clone_cost)
    # explore_with_cost(graph, start, visited, all_paths=all_paths)

    # # Compute total costs
    # all_actions = generate_actions_from_paths(graph, all_paths, clone_cost)
    # max_total_cost = max(sum(actions) for actions in all_actions)
    # clone_count = len(all_paths) - 1

    # return all_paths, max_total_cost, clone_count


    visited = set()
    all_paths = []

    # the below function is your method for generating paths!
    task_d_explore(graph, start, visited, all_paths=all_paths, explorer_id=0, clone_cost=clone_cost)

    # Post-process actions from paths
    all_actions = generate_actions_from_paths(graph, all_paths, clone_cost)

    max_total_cost = max(sum(actions) for actions in all_actions)
    clone_count = len(all_paths) - 1

    return all_paths, max_total_cost, clone_count


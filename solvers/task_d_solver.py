# -------------------------------------------------
# EDIT THIS FILE TO IMPLEMENT TASK D.
# Functions for your solver.
#
# __author__ = 'YOUR NAME HERE'
# __copyright__ = 'Copyright 2025, RMIT University'
# -------------------------------------------------

from graph.coordinate import Coordinate
from graph.graph import Graph
from solvers.util import estimate_subtree_weight, dfsBacktrack, generate_actions_from_paths


def task_d_explore(graph: Graph, current: Coordinate, visited: set,
                   all_paths: list[list[Coordinate]], explorer_id: int = 0) -> int:
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
        all_paths[explorer_id].append(current)

    path = all_paths[explorer_id]
    visited.add(current)

    # put your exploration below!
    while True:
        break  # remove this line when you are ready to go

        """BE SURE TO LOOK AT THE OTHER SOLVERS FOR INSPIRATION
        
        # HINT: Use graph.neighbours(current) to find adjacent nodes.
        # HINT: Use graph.getWeight(a, b) to get edge weights.
        # HINT: Use estimate_subtree_weight(...) to find the total weight in a sub-tree (branch).
        # HINT: Use dfsBacktrack(...) to return to junctions after exploring branches.
        # HINT: Use all_paths.append([...]) to spawn a new clone path."""

    return len(all_paths) - 1  # number of current clones


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
    """
    visited = set()
    all_paths = []

    # the below function is your method for generating paths!
    task_d_explore(graph, start, visited, all_paths=all_paths)

    # Post-process actions from paths
    all_actions = generate_actions_from_paths(graph, all_paths, clone_cost)

    max_total_cost = max(sum(actions) for actions in all_actions)
    clone_count = len(all_paths) - 1

    return all_paths, max_total_cost, clone_count

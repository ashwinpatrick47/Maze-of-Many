# -------------------------------------------------
# DON'T CHANGE THIS FILE.
# Functions that are shared between solvers.
#
# __author__ = 'Edward Small'
# __copyright__ = 'Copyright 2025, RMIT University'
# -------------------------------------------------

from collections import defaultdict
from graph.coordinate import Coordinate
from graph.graph import Graph


def generate_actions_from_paths(graph: Graph, all_paths: list[list[Coordinate]], clone_cost: int) -> list[list[int]]:
    """
    Constructs action lists for each explorer path, including movement costs and clone costs.

    - Movement costs are computed between consecutive coordinates.
    - If a later path starts at a coordinate visited by an earlier path, the earlier path is the spawner.
      The spawner pays a clone cost at the spawn point, and the clone inherits the spawner's cost up to that point
      (including prior clone costs), and pays its own clone cost.

    @param graph: The maze graph.
    @param all_paths: A list of explorer paths.
    @param clone_cost: The fixed cost for spawning a clone.

    @return: A list of action lists corresponding to each explorer.
    """
    all_actions = []
    coord_to_spawner = {}  # Maps coordinates to (explorer index, index in path)
    spawn_events = []  # List of (clone_id, spawner_id, spawn_index)

    # First pass: build movement actions and track first visits
    for i, path in enumerate(all_paths):
        actions = []
        if not path:
            all_actions.append(actions)
            continue

        for j in range(1, len(path)):
            weight = graph.getWeight(path[j - 1], path[j])
            actions.append(weight)

        all_actions.append(actions)

        for j, coord in enumerate(path):
            if coord not in coord_to_spawner:
                coord_to_spawner[coord] = (i, j)

    # Second pass: record spawn events
    for clone_id, clone_path in enumerate(all_paths):
        if not clone_path:
            continue

        start = clone_path[0]
        for spawner_id in range(clone_id):
            spawner_path = all_paths[spawner_id]
            if start in spawner_path:
                spawn_index = spawner_path.index(start)
                spawn_events.append((clone_id, spawner_id, spawn_index))
                break  # Only one spawner per clone

    # Third pass: apply clone costs to spawners
    for clone_id, spawner_id, spawn_index in spawn_events:
        insert_at = spawn_index if spawn_index > 0 else 0
        all_actions[spawner_id].insert(insert_at, clone_cost)

    # Fourth pass: compute inherited cost for each clone
    for clone_id, spawner_id, spawn_index in spawn_events:
        insert_at = spawn_index if spawn_index > 0 else 0
        inherited_cost = sum(all_actions[spawner_id][:insert_at + 1])
        all_actions[clone_id].insert(0, inherited_cost)

    return all_actions


def estimate_subtree_weight(graph: Graph, start: Coordinate, visited: set) -> int:
    """
    Computes the total weight of the unvisited subtree rooted at `start`.

    Traverses all reachable unvisited nodes from `start` using DFS,
    summing the weights of edges that connect unvisited nodes.

    @param graph: The maze graph to traverse.
    @param start: The coordinate from which to begin the subtree estimation.
    @param visited: A set of coordinates that have already been visited globally.

    @return: The total weight of the unvisited subtree rooted at `start`.
    """
    total_weight = 0
    stack = [start]
    local_visited = set()

    while stack:
        node = stack.pop()
        if node in visited or node in local_visited:
            continue

        local_visited.add(node)

        for neighbor in graph.neighbours(node):
            if neighbor not in visited and neighbor not in local_visited:
                edge_weight = graph.getWeight(node, neighbor)
                total_weight += edge_weight
                stack.append(neighbor)

    return total_weight


def dfsBacktrack(graph: Graph, start: Coordinate, goal: Coordinate) -> list[Coordinate]:
    """
    Returns a path from start to goal using DFS with a stack.
    Assumes the graph is a tree (no cycles), so any path found is valid.

    @param graph: The maze graph.
    @param start: Starting coordinate (end of branch).
    @param goal: Target coordinate (junction).

    @return: A list of Coordinates from start to goal (inclusive).
             Returns an empty list if no path exists.
    """
    stack = [(start, [start])]
    visited = {start}

    while stack:
        current, path = stack.pop()
        if current == goal:
            return path

        for neighbor in graph.neighbours(current):
            if neighbor not in visited:
                visited.add(neighbor)
                stack.append((neighbor, path + [neighbor]))

    return []

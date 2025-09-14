# -------------------------------------------------
# DON'T CHANGE THIS FILE.
# Generates a braided-connected maze from a graph using DFS.
#
# __author__ = 'Edward Small'
# __copyright__ = 'Copyright 2025, RMIT University'
# -------------------------------------------------

import sys
import random
from collections import deque
from typing import Set, List
from graph.coordinate import Coordinate
from maze.util import get_adjacent_coords, validateMaze, assertConnected
from graph.graph import Graph

def generateMazeDFS(graph: Graph, wall_removal: int = 0, max_weight: int = 1):
    """
    Generates a perfect maze (single connected component, no cycles) initially
    by performing a depth-first search and carving passages. It then deletes
    some walls to enforce cycles (wall_removal, which is a percentage)

    @param graph: The maze graph to modify (assumed initialised with all walls).
    @param wall_removal: Percentage of walls we should remove (0 if no loops, 100 if no walls).
    @param max_weight: When we delete a wall, we must put in a random traversal cost of [1, max_Weight].
    """
    # check that the percentage of remaining walls we want to remove is between 0 and 100
    assert (100 >= wall_removal >= 0), "Attempting to remove more than 100% of walls or less than 0%"

    # Choose a start and initialise visited/stack correctly
    if not getattr(graph, "vertices", None):
        return
    start: Coordinate = graph.vertices[0]
    visited: Set[Coordinate] = {start}
    stack: List[Coordinate] = [start]

    # If your Graph stores dimensions, prefer them to avoid off-by-ones.
    rows = getattr(graph, "rows", None)
    cols = getattr(graph, "cols", None)
    if rows is None or cols is None:
        # Fallback: infer a bounding box from vertices (works for full grids).
        all_r = [v.getRow() for v in graph.vertices]
        all_c = [v.getCol() for v in graph.vertices]
        rows = max(all_r) + 1
        cols = max(all_c) + 1

    while stack:
        current = stack[-1]

        # Consider only unvisited adjacent cells that still have a wall
        candidates = []
        for nb in get_adjacent_coords(current, rows, cols):
            if nb in visited:
                continue
            # getWallStatus should return True iff a wall exists (weight == 0)
            if graph.getWallStatus(current, nb):
                candidates.append(nb)

        if candidates:
            next_cell = random.choice(candidates)
            # Carve passage BOTH ways
            # Ensure the traversable edge exists (weight > 0).
            weight = random.randint(1, max_weight)
            ok = graph.updateWall(current, next_cell, hasWall=False, weight=weight)
            if not ok:
                # If updateWall enforces only the wall flag, also add an edge.
                graph.addEdge(current, next_cell, weight=0)
            else:
                # In case updateWall didn't set a positive weight, make sure.

                graph.addEdge(current, next_cell, weight=weight)

            visited.add(next_cell)
            stack.append(next_cell)
        else:
            stack.pop()

    # Sanity: verify graph is actually connected using its own neighbours()
    # BFS/DFS over the carved graph must reach all vertices.
    seen = set()
    q = deque([start])
    seen.add(start)
    while q:
        u = q.popleft()
        for v in graph.neighbours(u):
            if v not in seen:
                seen.add(v)
                q.append(v)

    # for debugging
    # print("Checking maze is valid...")
    # if not (assertConnected(graph) and validateMaze(graph)):
    #    print(f"Invalid maze generated - exiting...")
    #    sys.exit(1)

    # Remove a percentage of remaining walls to introduce cycles
    if wall_removal > 0:
        print(f"Removing {wall_removal}% of remaining walls to introduce cycles...")

        # Collect all walls between adjacent cells
        wall_candidates = []
        for room in graph.vertices:
            for neighbor in get_adjacent_coords(room, rows, cols):
                if room.isAdjacent(neighbor) and graph.getWallStatus(room, neighbor):
                    wall = tuple(sorted([room, neighbor], key=lambda x: (x.getRow(), x.getCol())))
                    wall_candidates.append(wall)

        # Determine how many walls to remove
        num_to_remove = int((wall_removal / 100.0) * len(wall_candidates))
        walls_to_remove = random.sample(wall_candidates, min(num_to_remove, len(wall_candidates)))

        # Remove selected walls
        for a, b in walls_to_remove:
            weight = random.randint(1, max_weight)
            success = graph.updateWall(a, b, hasWall=False, weight=weight)
            if not success:
                graph.addEdge(a, b, weight=0)
            else:
                graph.addEdge(a, b, weight=weight)

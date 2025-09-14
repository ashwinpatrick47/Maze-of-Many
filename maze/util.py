# -------------------------------------------------
# DON'T CHANGE THIS FILE.
# Contains some helper functions and validation tools.
#
# __author__ = 'Edward Small'
# __copyright__ = 'Copyright 2025, RMIT University'
# -------------------------------------------------

from graph.coordinate import Coordinate
from graph.graph import Graph
from typing import List, Set
from collections import deque

def get_adjacent_coords(coord: Coordinate, rows: int, cols: int) -> List[Coordinate]:
    r, c = coord.getRow(), coord.getCol()
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    result = []
    for dr, dc in directions:
        nr, nc = r + dr, c + dc
        if 0 <= nr < rows and 0 <= nc < cols:
            result.append(Coordinate(nr, nc))
    return result

def validateMaze(graph: Graph) -> None:
    """
    Runs invariants between matrix edges, wall flags, and neighbours().
    Prints any inconsistencies found.
    """
    bad = False
    V = getattr(graph, "vertices", [])
    for u in V:
        # neighbours should be symmetric
        for v in graph.neighbours(u):
            if u not in graph.neighbours(v):
                print("Asymmetry:", u, "<->", v); bad = True

    # Consistency between walls and edges
    for u in V:
        for v in V:
            if u == v: continue
            wall = graph.getWallStatus(u, v)         # True means “wall exists”
            in_nei = v in graph.neighbours(u)        # True means “edge exists”
            if wall and in_nei:
                print("Contradiction: wall=True but neighbour present", u, v); bad = True
            if (not wall) and (not in_nei):
                print("Contradiction: wall=False but no neighbour", u, v); bad = True

    if not bad:
        print("Maze invariants OK")
        return True

def assertConnected(graph: Graph) -> bool:
    """
    Checks if the carved maze graph is fully connected using neighbours().

    @param graph: The maze graph after generation.
    @returns True if connected, else False.
    """
    if not getattr(graph, "vertices", None):
        return True
    start: Coordinate = graph.vertices[0]
    seen: Set[Coordinate] = {start}
    q = deque([start])
    while q:
        u = q.popleft()
        for v in graph.neighbours(u):
            if v not in seen:
                seen.add(v); q.append(v)
    return len(seen) == len(graph.vertices)
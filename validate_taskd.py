# tests_task_d.py
# Robust testcases for Task D (clone-aware MST traversal).
#
# Run:
#   python tests_task_d.py
#
# Requirements: uses your project modules and grid-graph rules (orthogonal neighbors only).

from solvers.task_d_solver import task_d_solver
from solvers.util import generate_actions_from_paths
from helpers.helpers import load_maze_from_txt
from MST.prims import primMST
from graph.coordinate import Coordinate
from graph.adjacency_list import AdjacencyListGraph
import json
import math
import random
from typing import Tuple, Set, List


# -------------------------
# Utilities / Assertions
# -------------------------
def parse_entrance(cfg) -> Tuple[int, int]:
    ent = cfg.get("entrance", [0, 0])
    if isinstance(ent, (list, tuple)) and len(ent) == 2:
        return int(ent[0]), int(ent[1])
    if isinstance(ent, dict) and "row" in ent and "col" in ent:
        return int(ent["row"]), int(ent["col"])
    if isinstance(ent, str):
        for sep in [",", " "]:
            if sep in ent:
                a, b = ent.split(sep)
                return int(a), int(b)
    return 0, 0


def pick_start_from_graph(g, erow: int, ecol: int) -> Coordinate:
    vs = list(g.getVertices())
    exact = [v for v in vs if v.getRow() == erow and v.getCol() == ecol]
    if exact:
        return exact[0]
    return min(vs, key=lambda v: abs(v.getRow() - erow) + abs(v.getCol() - ecol))


def assert_task_d_solution(graph, start: Coordinate, clone_cost: int):
    """Runs solver and checks coverage, path validity, clone accounting, and cost recomputation."""
    all_paths, max_total_cost, clone_count = task_d_solver(graph, start, clone_cost)

    # 0) shape
    assert all_paths and all_paths[0], "Primary path missing/empty"
    assert all(len(p) > 0 for p in all_paths), "A clone path is empty"
    assert all_paths[0][0] == start, "Primary path must start at the provided start"

    # 1) Coverage == all vertices
    seen: Set[Coordinate] = {v for path in all_paths for v in path}
    V: Set[Coordinate] = set(graph.getVertices())
    assert seen == V, f"Coverage mismatch: visited={len(seen)}/{len(V)}"

    # 2) Path validity: every hop exists, positive-weight edge
    for i, path in enumerate(all_paths):
        for a, b in zip(path, path[1:]):
            assert b in graph.neighbours(a), f"Non-neighbor in path[{i}]: {a}->{b}"
            w = graph.getWeight(a, b)
            assert w > 0, f"Non-positive edge in path[{i}]: {a}->{b} (w={w})"

    # 3) Clone accounting
    assert clone_count == len(all_paths) - 1, "clone_count != len(all_paths) - 1"

    # 4) Cost recomputation == makespan
    actions = generate_actions_from_paths(graph, all_paths, clone_cost)
    recomputed = max(sum(a) for a in actions)
    assert recomputed == max_total_cost, f"Cost mismatch: recomputed={recomputed} vs reported={max_total_cost}"

    print(f"d={clone_cost:<6} → clones={clone_count:<4} | cost={max_total_cost}")
    return clone_count, max_total_cost


def assert_is_tree(g):
    vs = list(g.getVertices())
    edges = set()
    for u in vs:
        for v in g.neighbours(u):
            edges.add(frozenset({u, v}))
    m = len(edges)
    n = len(vs)
    assert m == max(0, n - 1), f"Not a tree: |E|={m}, |V|={n}"


# -------------------------
# Adversarial trees
# -------------------------
def make_line_tree(n: int) -> AdjacencyListGraph:
    """A simple path of length n-1 with small varying weights."""
    g = AdjacencyListGraph(1, n)
    verts = [Coordinate(0, i) for i in range(n)]
    g.addVertices(verts)
    for i in range(n - 1):
        assert g.addEdge(verts[i], verts[i + 1], 1 + (i % 3))
    return g


def make_plus_tree(total_work_hint: int) -> AdjacencyListGraph:
    """
    A plus-shaped tree (4 arms) with arm length L = ceil(total_work_hint/4).
    Only vertices on the plus are added -> true tree.
    """
    L = max(1, math.ceil(total_work_hint / 4))
    n = 2 * L + 1
    g = AdjacencyListGraph(n, n)

    center = Coordinate(L, L)
    used = {center}
    for t in range(1, L + 1):
        used.add(Coordinate(L - t, L))  # up
        used.add(Coordinate(L + t, L))  # down
        used.add(Coordinate(L, L + t))  # right
        used.add(Coordinate(L, L - t))  # left
    g.addVertices(list(used))

    def link(a, b, w):
        assert g.addEdge(a, b, w)

    # up
    for t in range(1, L + 1):
        link(Coordinate(L - (t - 1), L), Coordinate(L - t, L), 1 if t % 2 else 2)
    # right
    for t in range(1, L + 1):
        link(Coordinate(L, L + (t - 1)), Coordinate(L, L + t), 2 if t % 2 else 1)
    # down
    for t in range(1, L + 1):
        link(Coordinate(L + (t - 1), L), Coordinate(L + t, L), 1 if t % 2 else 2)
    # left
    for t in range(1, L + 1):
        link(Coordinate(L, L - (t - 1)), Coordinate(L, L - t), 2 if t % 2 else 1)

    return g


def make_small_grid_mst(r: int, c: int) -> AdjacencyListGraph:
    """Build an r×c grid with orthogonal edges, then take its MST."""
    base = AdjacencyListGraph(r, c)
    verts = [Coordinate(i, j) for i in range(r) for j in range(c)]
    base.addVertices(verts)
    for v in verts:
        i, j = v.getRow(), v.getCol()
        if i + 1 < r: base.addEdge(v, Coordinate(i + 1, j), 1)
        if j + 1 < c: base.addEdge(v, Coordinate(i, j + 1), 2)
    return primMST(base)


def make_random_tree(rows: int, cols: int, seed: int = 7) -> AdjacencyListGraph:
    """
    Create a random spanning tree embedded in a grid by Kruskal on a random-weight orthogonal grid graph.
    Then convert to AdjacencyListGraph if needed (we already build as list).
    """
    rng = random.Random(seed)
    base = AdjacencyListGraph(rows, cols)
    verts = [Coordinate(i, j) for i in range(rows) for j in range(cols)]
    base.addVertices(verts)

    # Build all candidate orthogonal edges with random weights
    edges = []
    for v in verts:
        i, j = v.getRow(), v.getCol()
        if i + 1 < rows:
            edges.append((rng.randint(1, 7), v, Coordinate(i + 1, j)))
        if j + 1 < cols:
            edges.append((rng.randint(1, 7), v, Coordinate(i, j + 1)))

    # Kruskal to make a tree
    parent = {v: v for v in verts}
    def find(x):
        if parent[x] != x:
            parent[x] = find(parent[x])
        return parent[x]
    def union(a, b):
        ra, rb = find(a), find(b)
        if ra == rb: return False
        parent[rb] = ra
        return True

    edges.sort(key=lambda x: x[0])
    tree = AdjacencyListGraph(rows, cols)
    tree.addVertices(verts)
    added = 0
    for w, u, v in edges:
        if union(u, v):
            assert tree.addEdge(u, v, w)
            added += 1
            if added == len(verts) - 1:
                break
    return tree


# -------------------------
# Test Runner
# -------------------------
def main():
    # A) Maze → MST
    full_graph = load_maze_from_txt("mazes/specMaze.txt", graph_type="matrix")
    maze_mst = primMST(full_graph)
    assert_is_tree(maze_mst)
    try:
        with open("config.json", "r") as f:
            cfg = json.load(f)
    except Exception:
        cfg = {}
    erow, ecol = parse_entrance(cfg)
    start = pick_start_from_graph(maze_mst, erow, ecol)

    print("Maze MST")
    for d in [0, 1, 5, 10, 100, 1000]:
        assert_task_d_solution(maze_mst, start, d)

    # B) Line
    line = make_line_tree(15)
    assert_is_tree(line)
    print("\nLine tree")
    for d in [0, 1, 10, 10_000]:
        assert_task_d_solution(line, Coordinate(0, 0), d)

    # C) Plus-shaped (star-like)
    plus = make_plus_tree(12)
    assert_is_tree(plus)
    center = Coordinate(plus.rows // 2, plus.cols // 2)
    print("\nPlus-shaped tree")
    for d in [0, 1, 5, 10_000]:
        assert_task_d_solution(plus, center, d)

    # D) Small grid MST
    grid = make_small_grid_mst(4, 4)
    assert_is_tree(grid)
    print("\nGrid(4x4) MST")
    for d in [0, 1, 5, 50, 10_000]:
        assert_task_d_solution(grid, Coordinate(0, 0), d)

    # E) Random tree
    rand_tree = make_random_tree(5, 5, seed=123)
    assert_is_tree(rand_tree)
    print("\nRandom 5x5 tree")
    for d in [0, 1, 5, 20, 10_000]:
        assert_task_d_solution(rand_tree, Coordinate(0, 0), d)

    print("\nAll Task D tests passed")


if __name__ == "__main__":
    main()

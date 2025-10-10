# testlist_extra.py
# Extra (complicated) tests for AdjacencyListGraph + Kruskal MST
#
# Assumes your project layout and imports:
#   graph.coordinate.Coordinate
#   graph.adjacency_list.AdjacencyListGraph
#   MST.kruskals.kruskalMST   (or wherever your kruskalMST lives)
#
# 

import random
from collections import deque, defaultdict

from graph.coordinate import Coordinate
from graph.adjacency_list import AdjacencyListGraph
from MST.kruskals import kruskalMST  # adjust path if different




def all_grid_coords(R, C):
    return [Coordinate(r, c) for r in range(R) for c in range(C)]

def orth_adjacent_pairs(R, C):
    """All undirected orthogonal neighbor pairs in an R x C grid."""
    pairs = []
    for r in range(R):
        for c in range(C):
            u = Coordinate(r, c)
            if r + 1 < R:
                pairs.append((u, Coordinate(r+1, c)))
            if c + 1 < C:
                pairs.append((u, Coordinate(r, c+1)))
    return pairs

def assert_invariants(g: AdjacencyListGraph, label=""):
    # 1) degree ≤ 4 and neighbors sorted
    for u in g.getVertices():
        neighs = g.neighbours(u)
        assert len(neighs) <= 4, f"{label} degree>4 at {u}"
        sorted_neighs = sorted(neighs, key=lambda z: (z.getRow(), z.getCol()))
        assert neighs == sorted_neighs, f"{label} neighbours not sorted at {u}"

    # 2) symmetry and positive weights
    for u in g.getVertices():
        for v in g.neighbours(u):
            wu = g.getWeight(u, v)
            wv = g.getWeight(v, u)
            assert wu > 0 and wv > 0, f"{label} non-positive weight on {u}<->{v}"
            assert wu == wv, f"{label} asymmetric weights {wu}!={wv} for {u}<->{v}"
            assert g.hasEdge(u, v) and g.hasEdge(v, u), f"{label} hasEdge inconsistent"

    # 3) getWallStatus consistency
    for u in g.getVertices():
        for v in g.getVertices():
            if u.isAdjacent(v):
                if g.hasEdge(u, v):
                    assert g.getWallStatus(u, v) is False, f"{label} wall reported for corridor {u}<->{v}"
                else:
                    assert g.getWallStatus(u, v) is True, f"{label} no wall reported for blocked {u}<->{v}"

def edges_of_graph(g: AdjacencyListGraph):
    """Return list of unique undirected edges (w, u, v) with u<v lexicographically."""
    edges = []
    seen = set()
    for u in g.getVertices():
        for v in g.neighbours(u):
            key = tuple(sorted([(u.getRow(), u.getCol()), (v.getRow(), v.getCol())]))
            if key in seen:
                continue
            seen.add(key)
            edges.append((g.getWeight(u, v), u, v))
    return edges

def mst_edge_set(mst: AdjacencyListGraph):
    S = set()
    for w, u, v in edges_of_graph(mst):
        key = tuple(sorted([(u.getRow(), u.getCol()), (v.getRow(), v.getCol())]))
        S.add(key)
    return S

def mst_path_max_edge(mst: AdjacencyListGraph, s: Coordinate, t: Coordinate):
    """Return the maximum edge weight on the unique MST path between s and t."""
    # BFS parents
    parent = {s: None}
    pw = {}  # edge weight from parent to node
    q = deque([s])
    while q and t not in parent:
        u = q.popleft()
        for v in mst.neighbours(u):
            if v not in parent:
                parent[v] = u
                pw[v] = mst.getWeight(u, v)
                q.append(v)

    assert t in parent, "MST path not found (graph disconnected?)"
    # Reconstruct and compute max
    cur = t
    max_w = 0
    while parent[cur] is not None:
        max_w = max(max_w, pw[cur])
        cur = parent[cur]
    return max_w

def is_connected(g: AdjacencyListGraph):
    V = g.getVertices()
    if not V:
        return True
    seen = set([V[0]])
    q = deque([V[0]])
    while q:
        u = q.popleft()
        for v in g.neighbours(u):
            if v not in seen:
                seen.add(v)
                q.append(v)
    return len(seen) == len(V)


# ---------- Tests ----------

def test_random_fuzz_open_close(seed=7, R=8, C=8, operations=2000):
    print("\nTEST: Randomized open/close fuzz with invariants")
    random.seed(seed)
    g = AdjacencyListGraph(R, C)
    g.addVertices(all_grid_coords(R, C))

    pairs = orth_adjacent_pairs(R, C)
    for _ in range(operations):
        u, v = random.choice(pairs)
        op = random.random()
        if op < 0.5:
            # open corridor with random positive weight
            w = random.randint(1, 9)
            ok = g.updateWall(u, v, hasWall=False, weight=w)
            assert ok, f"Failed to open wall {u}<->{v} with weight {w}"
        else:
            # close wall
            ok = g.updateWall(u, v, hasWall=True)
            assert ok, f"Failed to close wall {u}<->{v}"

        # invariants should always hold
        assert_invariants(g, label="fuzz")

    print("PASS: All fuzz operations maintained invariants")

def test_large_grid_stress(seed=11, R=20, C=20, open_prob=0.5):
    print("\nTEST: Large-grid stress + invariants")
    random.seed(seed)
    g = AdjacencyListGraph(R, C)
    g.addVertices(all_grid_coords(R, C))
    for u, v in orth_adjacent_pairs(R, C):
        if random.random() < open_prob:
            w = random.randint(1, 5)
            assert g.updateWall(u, v, hasWall=False, weight=w)

    # run invariants once at the end (heavier graph)
    assert_invariants(g, label="stress")
    print("PASS: Large-grid graph satisfied all invariants")

def test_idempotency_and_overwrite():
    print("\nTEST: Idempotency + overwrite semantics")
    g = AdjacencyListGraph(3, 3)
    a = Coordinate(0, 0)
    b = Coordinate(0, 1)
    g.addVertices([a, b])

    # addEdge once
    assert g.addEdge(a, b, 3) is True
    # addEdge again should be rejected
    assert g.addEdge(a, b, 4) is False
    assert g.getWeight(a, b) == 3

    # updateWall reopen should overwrite weight
    assert g.updateWall(a, b, hasWall=True)
    assert g.getWallStatus(a, b) is True

    assert g.updateWall(a, b, hasWall=False, weight=9)
    assert g.getWeight(a, b) == 9

    print("PASS: Idempotency and overwrite behavior correct")

def test_kruskal_mst_properties(seed=123, R=8, C=8, open_prob=0.75):
    print("\nTEST: Kruskal MST: size, connectivity, acyclicity, cycle property")
    random.seed(seed)
    g = AdjacencyListGraph(R, C)
    V = all_grid_coords(R, C)
    g.addVertices(V)

    # Make a connected-ish graph by biasing to open edges, but allow randomness
    for u, v in orth_adjacent_pairs(R, C):
        if random.random() < open_prob:
            w = random.randint(1, 20)
            g.updateWall(u, v, hasWall=False, weight=w)

    # If graph ended up disconnected (rare), connect minimally
    # Connect each row chain if needed
    for r in range(R):
        for c in range(C-1):
            u, v = Coordinate(r, c), Coordinate(r, c+1)
            if g.getWallStatus(u, v):
                g.updateWall(u, v, hasWall=False, weight=random.randint(1, 20))

    assert is_connected(g), "Base graph should be connected after patching"

    mst = kruskalMST(g)

    # 1) |E(MST)| == |V|-1
    E_mst = edges_of_graph(mst)
    assert len(E_mst) == len(V) - 1, f"MST edges wrong: {len(E_mst)} vs {len(V)-1}"

    # 2) MST connectivity
    assert is_connected(mst), "MST should be connected"

    # 3) Acyclic: connected + |E|=|V|-1 suffices, but we can also do a quick cycle-free check
    #    (already implied, so we skip extra check)

    # 4) Cycle property: For each non-MST edge e=(u,v) with weight w_e,
    #    w_e >= max edge on path_MST(u,v). If violated, MST is not minimal.
    mst_set = mst_edge_set(mst)
    for w_e, u, v in edges_of_graph(g):
        key = tuple(sorted([(u.getRow(), u.getCol()), (v.getRow(), v.getCol())]))
        if key in mst_set:
            continue
        max_on_path = mst_path_max_edge(mst, u, v)
        assert w_e >= max_on_path, (
            f"Cycle property violated: e({u}<->{v})={w_e} < max_on_path={max_on_path}"
        )

    print("PASS: MST properties (size/connectivity/cycle property) all hold")

def test_dense_line_then_prune(R=6, C=6):
    print("\nTEST: Dense line-open then prune (robustness)")
    g = AdjacencyListGraph(R, C)
    V = all_grid_coords(R, C)
    g.addVertices(V)

    # Open all horizontal lines with incremental weights, then close every second, etc.
    w = 1
    for r in range(R):
        for c in range(C-1):
            u, v = Coordinate(r, c), Coordinate(r, c+1)
            g.updateWall(u, v, hasWall=False, weight=w)
            w += 1

    # Now prune: close every second horizontal edge
    for r in range(R):
        for c in range(C-1):
            if (r + c) % 2 == 0:
                u, v = Coordinate(r, c), Coordinate(r, c+1)
                g.updateWall(u, v, hasWall=True)

    # Open some vertical links
    for r in range(R-1):
        for c in range(C):
            u, v = Coordinate(r, c), Coordinate(r+1, c)
            g.updateWall(u, v, hasWall=False, weight=(r+c+1))

    assert_invariants(g, label="line-prune")
    print("PASS: Dense line/prune graph preserved invariants")

if __name__ == "__main__":
    print("========== EXTRA TESTS: AdjacencyListGraph (complex) ==========")
    test_random_fuzz_open_close()
    test_large_grid_stress()
    test_idempotency_and_overwrite()
    test_kruskal_mst_properties()
    test_dense_line_then_prune()
    print("\nAll complex tests passed")

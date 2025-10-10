
import random
from collections import deque

from graph.coordinate import Coordinate
from graph.adjacency_matrix import AdjacencyMatrixGraph
from graph.adjacency_list import AdjacencyListGraph
from MST.kruskals import kruskalMST
from MST.prims import primMST
from graph.graph import Graph  # Base class



def edge_key(u, v):
    return frozenset((u, v))

def edge_set_and_weight(g: Graph):
    seen = set()
    total = 0
    E = set()
    for u in g.getVertices():
        for v in g.neighbours(u):
            k = edge_key(u, v)
            if k in seen:  # undirected
                continue
            seen.add(k)
            E.add(k)
            total += g.getWeight(u, v)
    return E, total

def is_acyclic_and_count(g: Graph):
    V = list(g.getVertices())
    visited = set()
    edges_count = 0
    counted = set()
    for u in V:
        for v in g.neighbours(u):
            k = edge_key(u, v)
            if k not in counted:
                counted.add(k)
                edges_count += 1

    def bfs(s):
        q = deque([s])
        visited.add(s)
        parent = {s: None}
        has_cycle = False
        while q:
            x = q.popleft()
            for y in g.neighbours(x):
                if y not in visited:
                    visited.add(y)
                    parent[y] = x
                    q.append(y)
                elif parent[x] != y:
                    has_cycle = True
        return has_cycle

    components = 0
    has_cycle_any = False
    for s in V:
        if s not in visited:
            components += 1
            has_cycle_any |= bfs(s)

    return (not has_cycle_any), components, edges_count

def count_components(graph: Graph) -> int:
    seen = set(); comps = 0
    for s in graph.getVertices():
        if s in seen: continue
        comps += 1
        stack = [s]; seen.add(s)
        while stack:
            u = stack.pop()
            for v in graph.neighbours(u):
                if v not in seen:
                    seen.add(v); stack.append(v)
    return comps

def connected_components_of_original(g: Graph):
    V = list(g.getVertices())
    vis = set()
    comps = []
    for s in V:
        if s in vis: continue
        comp = set()
        q = deque([s]); vis.add(s); comp.add(s)
        while q:
            x = q.popleft()
            for y in g.neighbours(x):
                if y not in vis:
                    vis.add(y); comp.add(y); q.append(y)
        comps.append(comp)
    return comps

def build_graph_pair(n, p, w_fn, seed=0):
    """
    Build a random undirected simple graph on an n x n grid of Coordinates with edge prob p.
    Returns (matrix_graph, list_graph). Weight function is w_fn(u,v) -> int.
    """
    rng = random.Random(seed)
    coords = [Coordinate(i // n, i % n) for i in range(n * n)]
    Gm = AdjacencyMatrixGraph(n, n)
    Gl = AdjacencyListGraph(n, n)
    Gm.addVertices(coords)
    Gl.addVertices(coords)

    # Add edges randomly between adjacent grid neighbors (N,E,S,W)
    def neighbors(c: Coordinate):
        r, c2 = c.getRow(), c.getCol()
        cand = [(r-1, c2), (r+1, c2), (r, c2-1), (r, c2+1)]
        for rr, cc in cand:
            if 0 <= rr < n and 0 <= cc < n:
                yield Coordinate(rr, cc)

    # Collect candidate edges to allow shuffled insertion later
    edges = set()
    for u in coords:
        for v in neighbors(u):
            if u != v:
                k = edge_key(u, v)
                if k not in edges:
                    edges.add(k)

    chosen_edges = []
    for k in edges:
        u, v = tuple(k)
        if rng.random() <= p:
            chosen_edges.append((u, v))

    rng.shuffle(chosen_edges)
    for (u, v) in chosen_edges:
        w = w_fn(u, v, rng)
        Gm.addEdge(u, v, w)
        Gl.addEdge(u, v, w)

    return Gm, Gl

def path_max_edge_weight(tree: Graph, src: Coordinate, dst: Coordinate):
    parent = {src: None}
    stack = [src]
    found = False
    while stack and not found:
        u = stack.pop()
        if u == dst:
            found = True
            break
        for v in tree.neighbours(u):
            if v not in parent:
                parent[v] = u
                stack.append(v)
    if not found:
        return None  # forest case

    cur = dst
    mx = float("-inf")
    while parent[cur] is not None:
        p = parent[cur]
        mx = max(mx, tree.getWeight(p, cur))
        cur = p
    return mx



def test_small_sanity():
    print("TEST 1: Small sanity (diamond with diagonal)")
    g = AdjacencyMatrixGraph(3, 3)
    a, b, c, d = Coordinate(0,0), Coordinate(0,1), Coordinate(1,1), Coordinate(1,0)
    g.addVertices([a,b,c,d])
    assert g.addEdge(a,b,4)
    assert g.addEdge(b,c,2)
    assert g.addEdge(c,d,1)
    assert g.addEdge(d,a,3)
    _ = g.addEdge(a,c,10)  # diagonal; some implementations reject this — that's fine

    mst_k = kruskalMST(g)
    mst_p = primMST(g)
    Ek, Wk = edge_set_and_weight(mst_k)
    Ep, Wp = edge_set_and_weight(mst_p)

    acyclic, comps, m = is_acyclic_and_count(mst_k)
    assert acyclic, "MST must be acyclic"
    assert Wk == Wp, f"Prim vs Kruskal weights differ: {Wk} vs {Wp}"
    assert m == len(mst_k.getVertices()) - comps, "Forest edges count mismatch"
    print("PASS: Sanity OK (acyclic, same weight as Prim, correct size)")


# ----------------------------
# 2) Equal weights / ties (adjacent-only, positive)
# ----------------------------
def test_negative_zero_equal_weights():
    print("\nTEST 2: Equal weights / ties (adjacent-only, positive weights)")
    g = AdjacencyListGraph(2, 3)
    V = [Coordinate(r, c) for r in range(2) for c in range(3)]
    g.addVertices(V)

    def add(u, v, w):
        ok = g.addEdge(u, v, w)
        assert ok, f"addEdge refused {(u,v,w)}"

    # Horizontal
    add(Coordinate(0,0), Coordinate(0,1), 1)
    add(Coordinate(0,1), Coordinate(0,2), 1)  # tie
    add(Coordinate(1,0), Coordinate(1,1), 2)
    add(Coordinate(1,1), Coordinate(1,2), 2)  # tie
    # Vertical
    add(Coordinate(0,0), Coordinate(1,0), 3)
    add(Coordinate(0,1), Coordinate(1,1), 1)  # tie with 1s
    add(Coordinate(0,2), Coordinate(1,2), 4)

    assert count_components(g) == 1, "Input must be connected"

    mst_k = kruskalMST(g)
    acyclic, comps, m = is_acyclic_and_count(mst_k)
    assert acyclic, "MST must be acyclic"
    assert comps == 1, "MST should be a single component"
    assert m == len(mst_k.getVertices()) - comps, "Tree size must be |V|-1"
    print("PASS: Handles equal-weight ties correctly")



def test_random_parity_and_cycle_property():
    print("\nTEST 3: Random graphs parity (Matrix vs List) + cycle property")
    rng = random.Random(42)

    def w_fn(_u, _v, r):
        return r.randint(1, 9)  # positive ints, ties allowed

    for n in [4, 5]:
        for p in [0.4, 0.7]:
            Gm, Gl = build_graph_pair(n, p, w_fn, seed=rng.randint(0, 9999))
            mst_k_m = kruskalMST(Gm)
            mst_k_l = kruskalMST(Gl)
            (Em, Wm) = edge_set_and_weight(mst_k_m)
            (El, Wl) = edge_set_and_weight(mst_k_l)

            assert Wm == Wl, f"Matrix vs List MST weight mismatch ({Wm} vs {Wl})"

            base = mst_k_l
            base_edges, _ = edge_set_and_weight(base)  # use same base's edges

            def in_tree(u, v):
                return edge_key(u, v) in base_edges

            for u in Gl.getVertices():
                for v in Gl.neighbours(u):
                    if u == v: continue
                    if in_tree(u, v): continue
                    w = Gl.getWeight(u, v)
                    mx = path_max_edge_weight(base, u, v)
                    if mx is None:
                        continue  # forest case
                    assert mx <= w, f"Cycle property violated: max_on_path({mx}) > edge({w})"


    print("PASS: Random parity holds and cycle property satisfied")



def test_edge_order_invariance():
    print("\nTEST 4: Edge insertion order invariance")
    n = 6
    coords = [Coordinate(i // n, i % n) for i in range(n * n)]

    def build_in_order(order_seed):
        rng = random.Random(order_seed)
        G = AdjacencyListGraph(n, n)
        G.addVertices(coords)

        edges = []
        for u in coords:
            r0, c0 = u.getRow(), u.getCol()
            nbrs = [Coordinate(r0-1,c0), Coordinate(r0+1,c0),
                    Coordinate(r0,c0-1), Coordinate(r0,c0+1)]
            for v in nbrs:
                if 0 <= v.getRow() < n and 0 <= v.getCol() < n and u != v:
                    k = edge_key(u, v)
                    if k not in edges:
                        edges.append(k)

        rng.shuffle(edges)
        for k in edges:
            u, v = tuple(k)
            w = (u.getRow() + u.getCol() + v.getRow() + v.getCol()) % 11 + 1  # ensure > 0
            ok = G.addEdge(u, v, w)
            assert ok
        return G

    baseline = kruskalMST(build_in_order(0))
    _, W0 = edge_set_and_weight(baseline)

    for seed in [1, 2, 3, 10, 999]:
        Gi = build_in_order(seed)
        mst_i = kruskalMST(Gi)
        _, Wi = edge_set_and_weight(mst_i)
        assert Wi == W0, f"MST weight changed with insertion order (seed {seed}): {Wi} vs {W0}"

    print("PASS: Insertion order does not affect MST weight")


def test_unique_weights_edge_set_equality():
    print("\nTEST 5: Distinct weights -> Kruskal and Prim edge sets equal")
    n = 5
    G = AdjacencyMatrixGraph(n, n)
    coords = [Coordinate(i // n, i % n) for i in range(n * n)]
    G.addVertices(coords)

    w = 1
    for u in coords:
        r, c = u.getRow(), u.getCol()
        for v in (Coordinate(r+1,c), Coordinate(r,c+1)):
            if 0 <= v.getRow() < n and 0 <= v.getCol() < n:
                ok = G.addEdge(u, v, w)
                assert ok
                w += 1

    mk = kruskalMST(G)
    mp = primMST(G)
    Ek, _ = edge_set_and_weight(mk)
    Ep, _ = edge_set_and_weight(mp)
    assert Ek == Ep, "With distinct weights, MST edge sets must match"
    print("PASS: Unique MST edge sets identical")



def test_disconnected_spanning_forest():
    print("\nTEST 6: Disconnected graph -> spanning forest")
    G = AdjacencyListGraph(2, 3)

    # Component 1: a—b—c (top row)
    a, b, c = Coordinate(0,0), Coordinate(0,1), Coordinate(0,2)
    # Component 2: d—e—f (bottom row)
    d, e, f = Coordinate(1,0), Coordinate(1,1), Coordinate(1,2)

    G.addVertices([a, b, c, d, e, f])

    # All edges are orthogonal neighbors (valid)
    assert G.addEdge(a, b, 1)
    assert G.addEdge(b, c, 2)

    assert G.addEdge(d, e, 1)
    assert G.addEdge(e, f, 2)

    comps = connected_components_of_original(G)   # two components of size 3 each
    mst = kruskalMST(G)
    acyclic, comps_mst, m = is_acyclic_and_count(mst)

    assert acyclic, "Forest must be acyclic per component"
    expected_edges = sum(len(comp) - 1 for comp in comps)  # (3-1) + (3-1) = 4
    assert m == expected_edges, f"Forest size wrong: {m} vs {expected_edges}"
    assert comps_mst == len(comps), "Number of components should be preserved"
    print("PASS: Spanning forest correct on disconnected input")



if __name__ == "__main__":
    test_small_sanity()
    test_negative_zero_equal_weights()
    test_random_parity_and_cycle_property()
    test_edge_order_invariance()
    test_unique_weights_edge_set_equality()
    test_disconnected_spanning_forest()
    print("\nAll advanced Kruskal tests passed ")

# -------------------------------------------------
# DON'T CHANGE THIS FILE.
# Basic Tests for Kruskals Implementation (not exhaustive).
#
# __author__ = 'Edward Small'
# __copyright__ = 'Copyright 2025, RMIT University'
# -------------------------------------------------

from graph.coordinate import Coordinate
from graph.adjacency_matrix import AdjacencyMatrixGraph
from MST.kruskals import kruskalMST
from MST.prims import primMST
from graph.graph import Graph  # Base class

def build_test_graph():
    g = AdjacencyMatrixGraph(3, 3)
    a = Coordinate(0, 0)
    b = Coordinate(0, 1)
    c = Coordinate(1, 1)
    d = Coordinate(1, 0)

    g.addVertices([a, b, c, d])
    g.addEdge(a, b, 4)
    g.addEdge(b, c, 2)
    g.addEdge(c, d, 1)
    g.addEdge(d, a, 3)
    g.addEdge(a, c, 10)  # Should be excluded from MST

    return g

def test_return_type():
    print("TEST: Return Type")
    g = build_test_graph()
    mst = kruskalMST(g)

    if isinstance(mst, Graph):
        print("PASS: kruskalMST returns a Graph object")
    else:
        print("FAIL: kruskalMST did not return a Graph")

def test_no_loops():
    print("\nTEST: No Loops in MST")
    g = build_test_graph()
    mst = kruskalMST(g)

    has_loops = any(u == v for u in mst.getVertices() for v in mst.neighbours(u))
    if not has_loops:
        print("PASS: No loops found in MST")
    else:
        print("FAIL: MST contains loops")

def test_weight_agreement_with_prims():
    print("\nTEST: Weight Agreement with Prim's MST")
    g = build_test_graph()
    mst_k = kruskalMST(g)
    mst_p = primMST(g)

    def total_weight(graph):
        seen = set()
        total = 0
        for u in graph.getVertices():
            for v in graph.neighbours(u):
                edge = frozenset([u, v])
                if edge not in seen:
                    total += graph.getWeight(u, v)
                    seen.add(edge)
        return total

    w_k = total_weight(mst_k)
    w_p = total_weight(mst_p)

    if w_k == w_p:
        print(f"PASS: MST weights match ({w_k})")
    else:
        print(f"FAIL: MST weights differ (Kruskal={w_k}, Prim={w_p})")

if __name__ == "__main__":
    test_return_type()
    test_no_loops()
    test_weight_agreement_with_prims()

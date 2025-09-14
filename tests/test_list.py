# -------------------------------------------------
# DON'T CHANGE THIS FILE.
# Basic Tests for List Implementation (not exhaustive).
#
# __author__ = 'Edward Small'
# __copyright__ = 'Copyright 2025, RMIT University'
# -------------------------------------------------

from graph.coordinate import Coordinate
from graph.adjacency_list import AdjacencyListGraph

def test_vertex_storage():
    print("TEST: Vertex Storage")
    g = AdjacencyListGraph(3, 3)
    a = Coordinate(0, 0)
    g.addVertex(a)

    if isinstance(g.getVertices(), list):
        print("PASS: getVertices returns a list")
    else:
        print("FAIL: getVertices should return a list")

    if a in g.getVertices():
        print("PASS: Vertex was added and retrievable")
    else:
        print("FAIL: Vertex not found after addition")

def test_edge_storage_and_types():
    print("\nTEST: Edge Storage and Types")
    g = AdjacencyListGraph(3, 3)
    a = Coordinate(0, 0)
    b = Coordinate(0, 1)
    g.addVertices([a, b])
    g.addEdge(a, b, 5)

    if isinstance(g.neighbours(a), list):
        print("PASS: neighbours returns a list")
    else:
        print("FAIL: neighbours should return a list")

    if b in g.neighbours(a):
        print("PASS: Edge correctly stored")
    else:
        print("FAIL: Edge not found in neighbours")

    if g.getWeight(a, b) == 5:
        print("PASS: Edge weight is correct")
    else:
        print("FAIL: Edge weight is incorrect")

def test_max_four_edges():
    print("\nTEST: Max Four Edges Per Vertex")
    g = AdjacencyListGraph(3, 3)
    center = Coordinate(1, 1)
    neighbors = [
        Coordinate(0, 1),
        Coordinate(1, 0),
        Coordinate(1, 2),
        Coordinate(2, 1),
        Coordinate(0, 0)  # fifth edge, should not be allowed
    ]
    g.addVertex(center)
    g.addVertices(neighbors)

    for n in neighbors:
        g.addEdge(center, n, 1)

    if len(g.neighbours(center)) <= 4:
        print("PASS: Vertex has ≤ 4 edges")
    else:
        print("FAIL: Vertex has more than 4 edges")

if __name__ == "__main__":
    test_vertex_storage()
    test_edge_storage_and_types()
    test_max_four_edges()

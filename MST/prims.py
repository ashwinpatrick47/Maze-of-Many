# -------------------------------------------------
# DON'T CHANGE THIS FILE.
# Function turns a graph into a minimum spanning tree using Prim's.
#
# __author__ = 'Edward Small'
# __copyright__ = 'Copyright 2025, RMIT University'
# -------------------------------------------------

import heapq
from graph.graph import Graph
import itertools


def primMST(graph: Graph) -> Graph:
    """
    Constructs and returns the minimum spanning tree (MST) of the given graph using Prim's algorithm.
    The returned graph is of the same type (matrix or list) and contains only the MST edges.

    @param graph: A Graph object implementing the required interface.
    @returns A new Graph object representing the MST.
    """

    # Handle edge case — if the graph is empty, return an empty MST of the same type.
    if not graph.getVertices():
        return type(graph)(graph.rows, graph.cols)

    # Choose an arbitrary starting vertex. Prim’s doesn’t care where you begin.
    start = graph.getVertices()[0]

    # Track which vertices we've already added to the MST.
    visited = {start}

    # Create a new graph to hold the MST. It should be the same type as the input graph.
    mst = type(graph)(graph.rows, graph.cols)

    # Copy all vertices into the MST. We'll selectively add edges as we go.
    mst.addVertices(graph.getVertices())

    # Initialize a priority queue (min-heap) to store candidate edges.
    # Each entry is a tuple: (weight, from_vertex, to_vertex)
    counter = itertools.count()
    edge_heap = []

    for neighbor in graph.neighbours(start):
        weight = graph.getWeight(start, neighbor)
        heapq.heappush(edge_heap, (weight, next(counter), start, neighbor))

    while len(visited) < len(graph.getVertices()) and edge_heap:
        weight, _, u, v = heapq.heappop(edge_heap)
        if v in visited:
            continue

        if mst.addEdge(u, v, weight):
            visited.add(v)
            for neighbor in graph.neighbours(v):
                if neighbor not in visited:
                    w = graph.getWeight(v, neighbor)
                    heapq.heappush(edge_heap, (w, next(counter), v, neighbor))

    # Return the completed MST.
    return mst

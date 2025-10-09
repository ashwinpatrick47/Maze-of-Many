# -------------------------------------------------
# EDIT THIS FILE TO IMPLEMENT KRUSKALS.
# Function turns a graph into a minimum spanning tree using Kruskal's.
#
# __author__ = 'Ashwin Patrick'
# __copyright__ = 'Copyright 2025, RMIT University'
# -------------------------------------------------

from graph.graph import Graph


def kruskalMST(graph: Graph) -> Graph:
    """
    Constructs and returns the minimum spanning tree (MST) of the given graph using Kruskal's algorithm.
    The returned graph is of the same type (matrix or list) and contains only the MST edges.

    @param graph: A Graph object implementing the required interface.
    @returns A new Graph object representing the MST.
    """

    # just return an empty graph if the graph is empty
    if not graph.getVertices():
        return type(graph)(graph.rows, graph.cols)

    # We know the MST will have the same number of nodes as the original input graph
    mst = type(graph)(graph.rows, graph.cols)
    mst.addVertices(graph.getVertices())

    # IMPLEMENT ME HERE
    vertices = graph.getVertices()
    if not vertices:
        return type(graph)(graph.rows, graph.cols)
    
    mst = type(graph)(graph.rows, graph.cols)
    mst.addVertices(vertices)
    # Collect all unique edges (avoid duplicates in undirected graph)
    edges = []
    seen = set()
    for u in vertices:
        for v in graph.neighbours(u):
            key = tuple(sorted([(u.getRow(), u.getCol()), (v.getRow(), v.getCol())]))

            if key in seen:
                continue
            seen.add(key)
            w = graph.getWeight(u, v)
            edges.append((w, u, v))

    # Sort all edges by ascending weight
    edges.sort(key=lambda x: x[0])
    # Disjoint-set (union–find) structure for cycle detection
    parent = {v: v for v in vertices}

     # Build MST incrementally
    added = 0
    target = len(vertices) - 1   # MST has |V|-1 edges
    for w, u, v in edges:
        if union(u, v, parent):        # only connect if they are in different components
            if mst.addEdge(u, v, w):     # add edge to MST
                added += 1
                if added == target: # stop once MST complete
                    break


    return mst


def find(coord, parent):
    """
    Recursively finds the root of the set containing `coord` using path compression.

    @param coord: The coordinate whose set root is being queried.
    @param parent: A mapping from each coordinate to its parent in the disjoint set forest.

    @returns: The root coordinate of the set containing `coord`.
    """
    if parent[coord] != coord:
        parent[coord] = find(parent[coord], parent)
    return parent[coord]


def union(a, b, parent):
    """
    Attempts to unite the sets containing `a` and `b`.

    @param a: First coordinate.
    @param b: Second coordinate.
    @param parent: Disjoint set parent mapping.

    @returns: True if the union was successful (i.e., no cycle formed), False otherwise.
    """

    root_a = find(a, parent)
    root_b = find(b, parent)
    if root_a != root_b:
        parent[root_b] = root_a
        return True
    return False

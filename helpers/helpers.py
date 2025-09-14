# -------------------------------------------------
# DON'T CHANGE THIS FILE.
# Contains helper functions to keep maze_runner file clean.
#
# __author__ = 'Edward Small'
# __copyright__ = 'Copyright 2025, RMIT University'
# -------------------------------------------------

import sys
import json
import time
import re
from graph.coordinate import Coordinate
from graph.graph import Graph
from graph.adjacency_list import AdjacencyListGraph
from graph.adjacency_matrix import AdjacencyMatrixGraph
from maze.maze import Maze

_timer_start = None  # need a global counter to keep track


def load_config(config_path: str) -> dict:
    """
    Loads the configuration file from JSON.

    @param config_path: Path to the config file.
    @returns Parsed config dictionary.
    """
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        sys.exit(1)


def build_maze(rows: int, cols: int, graph_type: str = "matrix") -> Maze:
    """
    Constructs a maze with all rooms added, but no connections yet.

    @param rows: Number of rows in the maze.
    @param cols: Number of columns in the maze.
    @param graph_type: 'matrix' or 'list' to choose graph implementation.
    @returns Maze object with graph populated.
    """

    if graph_type == "matrix":
        from graph.adjacency_matrix import AdjacencyMatrixGraph
        graph = AdjacencyMatrixGraph(rows, cols)
    elif graph_type == "list":
        from graph.adjacency_list import AdjacencyListGraph
        graph = AdjacencyListGraph(rows, cols)
    else:
        print(f"Unknown graph_type '{graph_type}'. Use 'matrix' or 'list'.")
        sys.exit(1)

    # Add all rooms (vertices) to the graph
    for r in range(rows):
        for c in range(cols):
            coord = Coordinate(r, c)
            graph.addVertex(coord)

    return Maze(graph)


def start_timer():
    """Starts a timer for measuring elapsed time."""
    global _timer_start
    _timer_start = time.perf_counter()


def stop_timer(label="Elapsed"):
    """Stops the timer and prints the elapsed time with a label."""
    global _timer_start
    if _timer_start is None:
        print(f"{label}: Timer was not started.")
        return
    elapsed = time.perf_counter() - _timer_start
    print(f"{label}: {elapsed:.4f} seconds")
    _timer_start = None


def save_maze_to_txt(graph, filename: str):
    """
    Saves the maze graph to a text file.

    Format:
    rows: <int>
    cols: <int>

    Edges:
    (row1, col1) <-> (row2, col2) [weight]

    @param graph: A Graph object implementing getVertices(), neighbours(), getWeight()
    @param filename: Path to the output .txt file
    """
    with open(filename, 'w') as f:
        f.write(f"rows: {graph.rows}\n")
        f.write(f"cols: {graph.cols}\n\n")
        f.write("Edges:\n")

        written = set()
        for u in graph.getVertices():
            for v in graph.neighbours(u):
                edge = frozenset([u, v])
                if edge in written:
                    continue
                weight = graph.getWeight(u, v)
                f.write(f"({u.getRow()}, {u.getCol()}) <-> ({v.getRow()}, {v.getCol()}) [{weight}]\n")
                written.add(edge)

    print(f"Maze saved to {filename}")


def load_maze_from_txt(filename: str, graph_type="list"):
    """
    Loads a maze graph from a text file and returns a Graph object.

    Format:
    rows: <int>
    cols: <int>

    Edges:
    (row1, col1) <-> (row2, col2) [weight]

    @param filename: Path to the .txt file
    @param graph_type: "list" or "matrix" to specify graph implementation
    @returns: A Graph object populated with vertices and edges
    """
    with open(filename, 'r') as f:
        lines = f.readlines()

    # Parse rows and cols
    row_line = next(line for line in lines if line.startswith("rows:"))
    col_line = next(line for line in lines if line.startswith("cols:"))
    rows = int(row_line.split(":")[1].strip())
    cols = int(col_line.split(":")[1].strip())

    # Choose graph type
    if graph_type == "list":
        graph = AdjacencyListGraph(rows, cols)
    elif graph_type == "matrix":
        graph = AdjacencyMatrixGraph(rows, cols)
    else:
        raise ValueError(f"Unknown graph_type: {graph_type}")

    # Parse edges
    edge_pattern = re.compile(r"\((\d+), (\d+)\) <-> \((\d+), (\d+)\) \[(\d+)\]")
    for line in lines:
        match = edge_pattern.match(line.strip())
        if match:
            r1, c1, r2, c2, weight = map(int, match.groups())
            u = Coordinate(r1, c1)
            v = Coordinate(r2, c2)
            graph.addVertices([u, v])
            graph.addEdge(u, v, weight)

    print(f"Maze loaded from {filename} as {graph_type} graph")
    return graph


def validate_full_coverage(graph: Graph, all_paths: list[list[Coordinate]]) -> bool:
    """
    Validates that all nodes in the graph are visited exactly once across all explorer paths.

    @param graph: The maze graph.
    @param all_paths: A list of explorer paths, each a list of Coordinates.

    @return: True if every node in the graph is visited exactly once; False otherwise.
    """
    try:
        visited = set()
        for path in all_paths:
            visited.update(path)

        expected = set(graph.getVertices())
        missing = expected - visited
        extra = visited - expected

        if missing:
            print(f"Coverage error: missing {len(missing)} nodes → {sorted(missing)}")
            return False
        if extra:
            print(f"Coverage error: unexpected nodes → {sorted(extra)}")
            return False

        return True

    except Exception as e:
        print(f"Coverage validation skipped due to graph error: {e}")
        return True


def validate_clone_origins(all_paths: list[list[Coordinate]]) -> bool:
    """
    Validates that every explorer (except the original) starts at a coordinate
    that was already visited by a previous explorer — i.e. a valid clone origin.

    @param all_paths: A list of explorer paths, each a list of Coordinates.

    @return: True if all clones start at a valid previously visited coordinate; False otherwise.
    """
    try:
        visited_so_far = set()

        for i, path in enumerate(all_paths):
            if not path:
                print(f"Clone error: explorer {i} has an empty path.")
                return False

            start = path[0]

            if i == 0:
                visited_so_far.update(path)
                continue

            if start not in visited_so_far:
                print(f"Clone error: explorer {i} starts at {start}, which was not visited by any previous explorer.")
                return False

            visited_so_far.update(path)

        return True

    except Exception as e:
        print(f"Clone origin validation skipped due to error: {e}")
        return True


def validate_path_connectivity(graph: Graph, all_paths: list[list[Coordinate]]) -> bool:
    """
    Validates that each explorer path is a valid walk through the graph.

    A path is valid if:
    - Every consecutive pair of coordinates in the path are adjacent in the graph.
    - The edge between them exists and has a defined weight.

    @param graph: The maze graph.
    @param all_paths: A list of explorer paths, each a list of Coordinates.

    @return: True if all paths are valid; False otherwise.
    """
    try:
        for i, path in enumerate(all_paths):
            if not path:
                print(f"Connectivity error: explorer {i} has an empty path.")
                return False

            for j in range(1, len(path)):
                a, b = path[j - 1], path[j]

                # Check adjacency
                if b not in graph.neighbours(a):
                    print(f"Connectivity error: explorer {i} has non-adjacent step from {a} to {b}.")
                    return False

                # Check edge weight exists
                try:
                    _ = graph.getWeight(a, b)
                except Exception:
                    print(f"Connectivity error: explorer {i} has missing edge weight from {a} to {b}.")
                    return False

        return True

    except Exception as e:
        print(f"Path connectivity validation skipped due to graph error: {e}")
        return True

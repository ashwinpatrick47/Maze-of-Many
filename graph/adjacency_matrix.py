# -------------------------------------------------
# DON'T CHANGE THIS FILE.
# Class for Adjacency Matrix representation of Graph.
#
# __author__ = 'Edward Small'
# __copyright__ = 'Copyright 2025, RMIT University'
# -------------------------------------------------

from typing import List, Dict
from graph.graph import Graph
from graph.coordinate import Coordinate

class AdjacencyMatrixGraph(Graph):
    """
    Graph implementation using an adjacency matrix.
    Vertices are Coordinates (rooms), and edges are weighted paths.
    A weight of 0 means a wall; weight > 0 means traversable with cost.
    """

    def __init__(self, rows: int, cols: int):
        """
        Initializes the graph with a fixed-size adjacency matrix.

        @param rows: Number of rows in the maze.
        @param cols: Number of columns in the maze.
        """
        self.rows = rows
        self.cols = cols
        self.size = rows * cols

        # List of all vertices (rooms)
        self.vertices: List[Coordinate] = []

        # Map from Coordinate to its index in the matrix
        self.vertex_indices: Dict[Coordinate, int] = {}

        # Preallocate the matrix with zeros
        self.matrix: List[List[int]] = [
            [0 for _ in range(self.size)] for _ in range(self.size)
        ]

    def _coord_to_index(self, coord: Coordinate) -> int:
        """
        Converts a Coordinate to its matrix index.

        @param coord: Coordinate to convert.
        @returns Integer index.
        """
        return coord.getRow() * self.cols + coord.getCol()

    def addVertex(self, label: Coordinate):
        """
        Adds a room to the graph.

        @param label: Coordinate of the room.
        """
        if label not in self.vertex_indices:
            index = self._coord_to_index(label)
            self.vertex_indices[label] = index
            self.vertices.append(label)

    def addVertices(self, vertLabels: List[Coordinate]):
        """
        Adds multiple rooms to the graph.

        @param vertLabels: List of Coordinates.
        """
        for label in vertLabels:
            self.addVertex(label)

    def addEdge(self, vert1: Coordinate, vert2: Coordinate, weight: int = 1) -> bool:
        """
        Adds a traversable path between two rooms if:
        1) No edge already exists,
        2) Both rooms are in the graph,
        3) The rooms are adjacent (orthogonally).

        @param vert1: Source room.
        @param vert2: Destination room.
        @param weight: Movement cost. Default is 1.

        @returns True if edge added successfully, otherwise False.
        """
        if vert1 not in self.vertex_indices or vert2 not in self.vertex_indices:
            return False  # Condition 2: both must be in the graph

        if not vert1.isAdjacent(vert2):
            return False  # Condition 3: must be adjacent

        i = self.vertex_indices[vert1]
        j = self.vertex_indices[vert2]

        if self.matrix[i][j] > 0:
            return False  # Condition 1: edge already exists

        self.matrix[i][j] = weight
        self.matrix[j][i] = weight  # Undirected
        return True

    def updateWall(self, vert1: Coordinate, vert2: Coordinate, hasWall: bool, weight: int=1) -> bool:
        """
        Updates wall status between two rooms.

        @param vert1: First room.
        @param vert2: Second room.
        @param hasWall: True to add wall (weight = 0), False to remove wall (weight = 1).
        @param weight: If we are remove a wall, what is the edge weight?

        @returns True if update successful.
        """
        if (
                vert1 not in self.vertex_indices or
                vert2 not in self.vertex_indices or
                not vert1.isAdjacent(vert2)
        ):
            return False  # Invalid update

        i = self.vertex_indices[vert1]
        j = self.vertex_indices[vert2]
        self.matrix[i][j] = 0 if hasWall else weight
        self.matrix[j][i] = 0 if hasWall else weight
        return True

    def print(self):
        """
        Prints the adjacency matrix of the graph to the terminal.

        Each row/column is labelled by its Coordinate.
        Entries show the edge weight (0 = wall, >0 = traversable path).

        Also validates that non-zero entries only occur between adjacent rooms.
        """
        print("Adjacency Matrix:")

        # Sort vertices by (row, col) for display
        sorted_vertices = sorted(self.vertices, key=lambda v: (v.getRow(), v.getCol()))
        labels = [f"({v.getRow()},{v.getCol()})" for v in sorted_vertices]

        # Print header row
        header = "         " + " ".join(f"{lab:>8}" for lab in labels)
        print(header)

        # Print each row
        for i, u in enumerate(sorted_vertices):
            label = labels[i]
            values = []

            for v in sorted_vertices:
                i_idx = self._coord_to_index(u)
                j_idx = self._coord_to_index(v)
                val = self.matrix[i_idx][j_idx]

                if val != 0 and not u.isAdjacent(v):
                    print(f"⚠️ Invalid adjacency: {u} → {v} with weight {val}")

                values.append(f"{val:8}")

            print(f"{label:>8} {' '.join(values)}")

    def removeEdge(self, vert1: Coordinate, vert2: Coordinate) -> bool:
        """
        Removes the path between two rooms.

        @param vert1: First room.
        @param vert2: Second room.

        @returns True if edge removed successfully.
        """
        return self.updateWall(vert1, vert2, hasWall=True)

    def hasVertex(self, label: Coordinate) -> bool:
        """
        Checks if a room exists in the graph.

        @param label: Coordinate of the room.

        @returns True if room exists.
        """
        return label in self.vertex_indices

    def hasEdge(self, vert1: Coordinate, vert2: Coordinate) -> bool:
        """
        Checks if a traversable path exists between two rooms.

        @param vert1: First room.
        @param vert2: Second room.

        @returns True if edge exists and is traversable.
        """
        if vert1 in self.vertex_indices and vert2 in self.vertex_indices:
            i = self.vertex_indices[vert1]
            j = self.vertex_indices[vert2]
            return self.matrix[i][j] > 0
        return False

    def getWallStatus(self, vert1: Coordinate, vert2: Coordinate) -> bool:
        """
        Checks if a wall exists between two rooms.

        @param vert1: First room.
        @param vert2: Second room.

        @returns True if wall exists (weight = 0), False otherwise.
        """
        i = self.vertex_indices[vert1]
        j = self.vertex_indices[vert2]
        return self.matrix[i][j] == 0

    def getWeight(self, vert1: Coordinate, vert2: Coordinate) -> int:
        """
        Returns the weight between two coordinates if an edge exists.

        @returns positive integer if edge exists, 0 otherwise.
        """
        if vert1 in self.vertex_indices and vert2 in self.vertex_indices:
            i = self.vertex_indices[vert1]
            j = self.vertex_indices[vert2]
            return self.matrix[i][j] if self.matrix[i][j] > 0 else 0
        return 0

    def getVertices(self) -> List[Coordinate]:
        return self.vertices

    def neighbours(self, label: Coordinate) -> List[Coordinate]:
        if label not in self.vertex_indices:
            return []

        idx = self.vertex_indices[label]
        index_to_coord = {i: v for v, i in self.vertex_indices.items()}

        return [
            index_to_coord[i]
            for i in range(self.size)
            if self.matrix[idx][i] > 0 and i in index_to_coord
        ]

# -------------------------------------------------
# EDIT THIS FILE TO IMPLEMENT ADJACENCY LIST.
# Class for Adjacency List representation of Graph.
#
# __author__ = 'YOUR NAME HERE'
# __copyright__ = 'Copyright 2025, RMIT University'
# -------------------------------------------------

from typing import List, Dict, Tuple
from graph.graph import Graph
from graph.coordinate import Coordinate


class AdjacencyListGraph(Graph):
    """
    Graph implementation using an adjacency list.
    Vertices are Coordinates (rooms), and edges are weighted paths.
    A weight of 0 between adjacent cells means a wall; weight > 0 means traversable with cost.
    """

    def __init__(self, rows: int, cols: int):
        """
        Initializes the graph with empty adjacency lists.

        @param rows: Number of rows in the maze.
        @param cols: Number of columns in the maze.
        """
        self.rows = rows
        self.cols = cols
        self.size = rows * cols

        # Set of all vertices
        self.vertices: List[Coordinate] = []

        # Adjacency list: Coordinate → List[Tuple[Coordinate, weight]]
        self.adj_list: Dict[Coordinate, List[Tuple[Coordinate, int]]] = {}

    def addVertex(self, label: Coordinate):
        """
        Adds a vertex to the graph.

        @param label: Coordinate of the room.
        """
        if label not in self.adj_list:
            self.adj_list[label] = []
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
        # IMPLEMENT ME
        pass

    def updateWall(self, vert1: Coordinate, vert2: Coordinate, hasWall: bool, weight: int = 1) -> bool:
        """
        Updates wall status between two rooms.

        @param vert1: First room.
        @param vert2: Second room.
        @param hasWall: True to add wall (weight = 0), False to remove wall (weight = 1).
        @param weight: if we are remove a wall, what is the edge weight?

        @returns True if update successful.
        """
        # IMPLEMENT ME
        pass

    def print(self):
        """
        Prints the adjacency list of the graph to the terminal. Like

        (0, 0) -> [(0, 1), 1; (1, 0), 2]
        (0, 1) -> [(0, 0), 1; (1, 1), 3]
        ...

        Useful for debugging.

        @returns None
        """
        for u in self.vertices:
            edges = self.adj_list.get(u, [])
            edge_strs = [f"({v.getRow()}, {v.getCol()}), {w}" for v, w in edges]
            print(f"({u.getRow()}, {u.getCol()}) -> [{'; '.join(edge_strs)}]")

    def removeEdge(self, vert1: Coordinate, vert2: Coordinate) -> bool:
        """
        Removes the path between two rooms.

        @param vert1: First room.
        @param vert2: Second room.

        @returns True if edge removed successfully.
        """
        # IMPLEMENT ME
        pass

    def hasVertex(self, label: Coordinate) -> bool:
        """
        Checks if a room exists in the graph.

        @param label: Coordinate of the room.

        @returns True if room exists.
        """
        # IMPLEMENT ME
        pass

    def hasEdge(self, vert1: Coordinate, vert2: Coordinate) -> bool:
        """
        Checks if a traversable path exists between two rooms.

        @param vert1: First room.
        @param vert2: Second room.

        @returns True if edge exists and is traversable.
        """
        # IMPLEMENT ME
        pass

    def getWallStatus(self, vert1: Coordinate, vert2: Coordinate) -> bool:
        """
        Checks if a wall exists between two rooms.

        @param vert1: First room.
        @param vert2: Second room.

        @returns True if wall exists (weight = 0), False otherwise.
        """
        # IMPLEMENT ME
        pass

    def getWeight(self, vert1: Coordinate, vert2: Coordinate) -> int:
        """
        Returns the weight between two coordinates if an edge exists.

        @returns positive integer if edge exists, 0 otherwise.
        """
        # IMPLEMENT ME
        return 0

    def getVertices(self) -> List[Coordinate]:
        return self.vertices

    def neighbours(self, label: Coordinate) -> List[Coordinate]:
        """
        Retrieves all accessible adjacent rooms.

        @param label: Coordinate of the room.

        @returns List of neighbouring Coordinates.
        """
        # IMPLEMENT ME
        return []

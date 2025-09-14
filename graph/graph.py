# -------------------------------------------------
# DON'T CHANGE THIS FILE.
# Base class for graph implementations.
#
# __author__ = 'Edward Small'
# __copyright__ = 'Copyright 2025, RMIT University'
# -------------------------------------------------


from typing import List
from graph.coordinate import Coordinate

class Graph:
    """
    Base class for a graph representing a maze.
    Each vertex is a room (represented by a Coordinate).
    Each edge represents a traversable path between rooms.
    A weighted edge implies no wall and a movement cost.
    """

    def print(self):
        """
        prints the structure to terminal
        """
        pass
    def addVertex(self, label: Coordinate):
        """
        Adds a room to the maze.

        @param label: The Coordinate representing the room.
        """
        pass

    def addVertices(self, vertLabels: List[Coordinate]):
        """
        Adds multiple rooms to the maze.

        @param vertLabels: List of Coordinates representing rooms.
        """
        pass

    def addEdge(self, vert1: Coordinate, vert2: Coordinate, weight: int = 1) -> bool:
        """
        Adds a traversable path between two rooms.
        A weight > 0 implies no wall and a movement cost.
        A weight of 0 implies a wall (non-traversable).

        @param vert1: Source room.
        @param vert2: Destination room.
        @param weight: Cost of moving between rooms. Default is 1.

        @returns True if edge is successfully added, otherwise False.
        """
        pass

    def updateWall(self, vert1: Coordinate, vert2: Coordinate, hasWall: bool, weight: int) -> bool:
        """
        Updates the wall status between two rooms.
        If hasWall is True, the edge weight is set to 0 (wall exists).
        If hasWall is False, the edge weight is set to a positive value (traversable).

        @param vert1: Source room.
        @param vert2: Destination room.
        @param hasWall: True to add wall, False to remove wall.
        @param weight: cost of moving to this room.

        @returns True if wall status is successfully updated, otherwise False.
        """
        pass

    def removeEdge(self, vert1: Coordinate, vert2: Coordinate) -> bool:
        """
        Removes the path between two rooms.

        @param vert1: Source room.
        @param vert2: Destination room.

        @returns True if edge is successfully removed, otherwise False.
        """
        pass

    def hasVertex(self, label: Coordinate) -> bool:
        """
        Checks if a room exists in the maze.

        @param label: Coordinate of the room.

        @returns True if room exists, otherwise False.
        """
        pass

    def hasEdge(self, vert1: Coordinate, vert2: Coordinate) -> bool:
        """
        Checks if a traversable path exists directly between two rooms.

        @param vert1: Source room.
        @param vert2: Destination room.

        @returns True if edge exists and is traversable, otherwise False.
        """
        pass

    def getWallStatus(self, vert1: Coordinate, vert2: Coordinate) -> bool:
        """
        Checks if a wall exists between two rooms.

        @param vert1: Source room.
        @param vert2: Destination room.

        @returns True if a wall exists (i.e., edge weight is 0), otherwise False.
        """
        pass

    def getWeight(self, vert1: Coordinate, vert2: Coordinate) -> int:
        """
        returns the weight between two coordinates.

        @param vert1: Source room.
        @param vert2: Destination room.

        @returns positive integer if an edge exists.
        """
        pass

    def getVertices(self) -> List[Coordinate]:
        """
        Returns all vertices (rooms) in the graph.

        @returns List of Coordinates.
        """
        pass

    def neighbours(self, label: Coordinate) -> List[Coordinate]:
        """
        Retrieves all adjacent rooms that are accessible (no wall).

        @param label: Coordinate of the room.

        @returns List of accessible neighbouring rooms.
        """
        pass

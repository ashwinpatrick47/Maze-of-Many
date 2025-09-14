# -------------------------------------------------
# DON'T CHANGE THIS FILE.
# Maze wrapper on top of graph.
#
# __author__ = 'Edward Small'
# __copyright__ = 'Copyright 2025, RMIT University'
# -------------------------------------------------

from typing import Optional, Dict, List
from graph.graph import Graph
from graph.coordinate import Coordinate
from maze.room import Room  # Optional: if you're using Room wrappers

class Maze:
    """
    High-level maze wrapper built on a Graph.
    Manages start/end points, room metadata, and maze operations.
    """

    def __init__(self, graph: Graph):
        """
        Initializes the Maze with a given graph structure.

        @param graph: A Graph object representing the maze layout.
        """
        self.graph = graph
        self.start: Optional[Coordinate] = None
        self.end: Optional[Coordinate] = None
        self.room_map: Dict[Coordinate, Room] = {}  # Optional metadata for each room

    def setStart(self, coord: Coordinate):
        """
        Sets the starting room of the maze.

        @param coord: Coordinate of the start room.
        """
        if self.graph.hasVertex(coord):
            self.start = coord

    def setEnd(self, coord: Coordinate):
        """
        Sets the ending room of the maze.

        @param coord: Coordinate of the end room.
        """
        if self.graph.hasVertex(coord):
            self.end = coord

    def addRoom(self, room: Room):
        """
        Adds a Room object to the maze's metadata map.

        @param room: Room object containing description and contents.
        """
        coord = room.getPosition()
        if self.graph.hasVertex(coord):
            self.room_map[coord] = room

    def getRoom(self, coord: Coordinate) -> Optional[Room]:
        """
        Retrieves the Room object for a given coordinate.

        @param coord: Coordinate of the room.
        @returns Room object if found, else None.
        """
        return self.room_map.get(coord)

    def getNeighbours(self, coord: Coordinate) -> List[Coordinate]:
        """
        Returns all accessible neighbouring rooms (no wall).

        @param coord: Coordinate of the room.
        @returns List of Coordinates for accessible neighbours.
        """
        return self.graph.neighbours(coord)

    def isWallBetween(self, coord1: Coordinate, coord2: Coordinate) -> bool:
        """
        Checks if a wall exists between two rooms.

        @param coord1: First room.
        @param coord2: Second room.
        @returns True if a wall exists, False if path is open.
        """
        return self.graph.getWallStatus(coord1, coord2)

    def connectRooms(self, coord1: Coordinate, coord2: Coordinate, weight: int = 1):
        """
        Creates a traversable path between two rooms.

        @param coord1: First room.
        @param coord2: Second room.
        @param weight: Movement cost between rooms.
        """
        self.graph.addEdge(coord1, coord2, weight)

    def blockPath(self, coord1: Coordinate, coord2: Coordinate):
        """
        Adds a wall between two rooms (makes path impassable).

        @param coord1: First room.
        @param coord2: Second room.
        """
        self.graph.updateWall(coord1, coord2, hasWall=True)

    def unblockPath(self, coord1: Coordinate, coord2: Coordinate, weight: int = 1):
        """
        Removes a wall between two rooms (makes path traversable).

        @param coord1: First room.
        @param coord2: Second room.
        @param weight: Movement cost to assign to the path.
        """
        self.graph.updateWall(coord1, coord2, hasWall=False)
        self.graph.addEdge(coord1, coord2, weight)

    def describe(self, coord: Coordinate) -> str:
        """
        Returns a description of the room at the given coordinate.

        @param coord: Coordinate of the room.
        @returns Description string or default message.
        """
        room = self.getRoom(coord)
        return room.description if room else "An empty room."

    def isSolved(self) -> bool:
        """
        Placeholder for maze-solving logic.
        Could check if a path exists from start to end.

        @returns True if maze is solved, False otherwise.
        """
        return False
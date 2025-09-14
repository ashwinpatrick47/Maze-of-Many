# -------------------------------------------------
# DON'T CHANGE THIS FILE.
# Room wrapper on top of coordinate (allows us to populate rooms).
#
# __author__ = 'Edward Small'
# __copyright__ = 'Copyright 2025, RMIT University'
# -------------------------------------------------


from graph.coordinate import Coordinate


class Room:
    """
    Wrapper for a maze cell. Contains a Coordinate and optional room-specific data.
    """

    def __init__(self, coordinate: Coordinate, description: str = "", contents: list = None, visited: bool = False):
        """
        Constructor.

        @param coordinate: The Coordinate object representing the room's position.
        @param description: Optional text describing the room.
        @param contents: Optional list of items or objects in the room.
        @param visited: Whether the room has been visited.
        """
        self.coordinate = coordinate
        self.description = description
        self.contents = contents if contents is not None else []
        self.visited = visited

    def getPosition(self) -> Coordinate:
        return self.coordinate

    def markVisited(self):
        self.visited = True

    def addItem(self, item):
        self.contents.append(item)

    def removeItem(self, item):
        if item in self.contents:
            self.contents.remove(item)

    def __repr__(self):
        return f"Room({self.coordinate}, visited={self.visited}, contents={self.contents})"

# -------------------------------------------------
# DON'T CHANGE THIS FILE.
# Class for Coordinates (vertices) of Graph.
#
# __author__ = 'Edward Small'
# __copyright__ = 'Copyright 2025, RMIT University'
# -------------------------------------------------

class Coordinate:
    """
    Represent coordinates for maze cells.
    """

    def __init__(self, row: int, col: int, obj=None):
        """
        Constructor.

        @param row: Row of coordinates.
        @param col: Column of coordinates.
        """
        self.m_r = row
        self.m_c = col

    def getRow(self) -> int:
        """@returns Row of coordinate."""
        return self.m_r

    def getCol(self) -> int:
        """@returns Column of coordinate."""
        return self.m_c

    def isAdjacent(self, other: 'Coordinate') -> bool:
        """
        Determine if two coordinates are adjacent to each other.
        @param other: the coordinate we wish to know if we are adjacent to
        """
        return (
                abs(self.m_r - other.getRow()) == 1 and self.m_c == other.getCol()
        ) or (
                self.m_r == other.getRow() and abs(self.m_c - other.getCol()) == 1
        )

    def __eq__(self, other: object) -> bool:
        """
        Overload the == operator.
        """
        if isinstance(other, Coordinate):  # check other "thing" is a coordinate
            return self.m_r == other.getRow() and self.m_c == other.getCol()  # check row and column are the same
        return False

    def __hash__(self) -> int:
        """
        Returns hash value of Coordinates. Needed for being a key in dictionaries.
        """
        return hash((self.m_r, self.m_c))

    def __repr__(self):
        return f"Coordinates({self.m_r}, {self.m_c})"

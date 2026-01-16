"""Quad (quadrilateral) geometry type - optimized for 4-vertex shapes like tiles."""

import random
from dataclasses import dataclass
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from escape.types.point import Point


@dataclass
class Quad:
    """Represents a quadrilateral defined by exactly 4 vertices in order."""

    p1: "Point"
    p2: "Point"
    p3: "Point"
    p4: "Point"

    @classmethod
    def fromPoints(cls, points: List["Point"]) -> "Quad":
        """Create a Quad from a list of 4 points."""
        if len(points) != 4:
            raise ValueError(f"Quad requires exactly 4 points, got {len(points)}")
        return cls(points[0], points[1], points[2], points[3])

    @classmethod
    def fromCoords(cls, coords: List[tuple[int, int]]) -> "Quad":
        """Create a Quad from a list of (x, y) coordinate tuples."""
        from escape.types.point import Point

        if len(coords) != 4:
            raise ValueError(f"Quad requires exactly 4 coordinates, got {len(coords)}")
        points = [Point(x, y) for x, y in coords]
        return cls(points[0], points[1], points[2], points[3])

    @classmethod
    def fromArrays(cls, xCoords: List[int], yCoords: List[int]) -> "Quad":
        """Create a Quad from separate x and y coordinate arrays."""
        from escape.types.point import Point

        if len(xCoords) != 4 or len(yCoords) != 4:
            raise ValueError("Quad requires exactly 4 x and 4 y coordinates")
        return cls(
            Point(xCoords[0], yCoords[0]),
            Point(xCoords[1], yCoords[1]),
            Point(xCoords[2], yCoords[2]),
            Point(xCoords[3], yCoords[3]),
        )

    @property
    def vertices(self) -> List["Point"]:
        """Get all 4 vertices as a list."""
        return [self.p1, self.p2, self.p3, self.p4]

    def center(self) -> "Point":
        """Get the centroid (center of mass) of the quad."""
        from escape.types.point import Point

        x = (self.p1.x + self.p2.x + self.p3.x + self.p4.x) // 4
        y = (self.p1.y + self.p2.y + self.p3.y + self.p4.y) // 4
        return Point(x, y)

    def bounds(self) -> tuple[int, int, int, int]:
        """Get the axis-aligned bounding box of this quad."""
        xs = [self.p1.x, self.p2.x, self.p3.x, self.p4.x]
        ys = [self.p1.y, self.p2.y, self.p3.y, self.p4.y]
        return (min(xs), min(ys), max(xs), max(ys))

    def _sign(self, p1x: int, p1y: int, p2x: int, p2y: int, p3x: int, p3y: int) -> float:
        """Helper for cross product sign calculation."""
        return (p1x - p3x) * (p2y - p3y) - (p2x - p3x) * (p1y - p3y)

    def _pointInTriangle(self, px: int, py: int, v1: "Point", v2: "Point", v3: "Point") -> bool:
        """Check if point is in triangle using barycentric coordinates."""
        d1 = self._sign(px, py, v1.x, v1.y, v2.x, v2.y)
        d2 = self._sign(px, py, v2.x, v2.y, v3.x, v3.y)
        d3 = self._sign(px, py, v3.x, v3.y, v1.x, v1.y)

        hasNeg = (d1 < 0) or (d2 < 0) or (d3 < 0)
        hasPos = (d1 > 0) or (d2 > 0) or (d3 > 0)

        return not (hasNeg and hasPos)

    def contains(self, point: "Point") -> bool:
        """Check if a point is within this quad using triangle decomposition."""
        px, py = point.x, point.y

        # Split quad into two triangles: (p1, p2, p3) and (p1, p3, p4)
        # Point is in quad if it's in either triangle
        return self._pointInTriangle(px, py, self.p1, self.p2, self.p3) or self._pointInTriangle(
            px, py, self.p1, self.p3, self.p4
        )

    def area(self) -> float:
        """Calculate the area of the quad using the shoelace formula."""
        # Shoelace formula for quad
        area = 0.0
        vertices = self.vertices
        n = 4
        for i in range(n):
            j = (i + 1) % n
            area += vertices[i].x * vertices[j].y
            area -= vertices[j].x * vertices[i].y
        return abs(area) / 2.0

    def randomPoint(self) -> "Point":
        """Generate a random point within this quad using bilinear interpolation."""
        from escape.types.point import Point

        # Use bilinear interpolation for efficient random point generation
        # This works well for convex quads and reasonably well for mildly concave ones
        u = random.random()
        v = random.random()

        # Bilinear interpolation between the 4 corners
        # P = (1-u)(1-v)*p1 + u*(1-v)*p2 + u*v*p3 + (1-u)*v*p4
        x = int(
            (1 - u) * (1 - v) * self.p1.x
            + u * (1 - v) * self.p2.x
            + u * v * self.p3.x
            + (1 - u) * v * self.p4.x
        )
        y = int(
            (1 - u) * (1 - v) * self.p1.y
            + u * (1 - v) * self.p2.y
            + u * v * self.p3.y
            + (1 - u) * v * self.p4.y
        )

        point = Point(x, y)

        # Verify point is actually inside (handles concave quads)
        # If not, fall back to center or try again
        if self.contains(point):
            return point

        # For concave quads, use rejection sampling as fallback
        minX, minY, maxX, maxY = self.bounds()
        for _ in range(100):
            x = random.randint(minX, maxX)
            y = random.randint(minY, maxY)
            point = Point(x, y)
            if self.contains(point):
                return point

        # Ultimate fallback to center
        return self.center()

    def click(self, button: str = "left", randomize: bool = True) -> None:
        """Click within this quad."""
        point = self.randomPoint() if randomize else self.center()
        point.click(button=button)

    def hover(self, randomize: bool = True) -> bool:
        """Move mouse to hover within this quad."""
        from escape.globals import getClient
        from escape.types.point import Point

        current = Point(*getClient().input.mouse.position)
        if self.contains(current):
            return True
        point = self.randomPoint() if randomize else self.center()
        point.hover()
        return True

    def rightClick(self, randomize: bool = True) -> None:
        """Right-click within this quad."""
        self.click(button="right", randomize=randomize)

    def toPolygon(self) -> "Polygon":
        """Convert this quad to a Polygon."""
        from escape.types.polygon import Polygon

        return Polygon(self.vertices)

    def isConvex(self) -> bool:
        """Check if this quad is convex."""
        vertices = self.vertices

        def crossProduct(o: "Point", a: "Point", b: "Point") -> float:
            return (a.x - o.x) * (b.y - o.y) - (a.y - o.y) * (b.x - o.x)

        signs = []
        for i in range(4):
            o = vertices[i]
            a = vertices[(i + 1) % 4]
            b = vertices[(i + 2) % 4]
            cross = crossProduct(o, a, b)
            if cross != 0:
                signs.append(cross > 0)

        # Convex if all signs are the same
        return len(set(signs)) <= 1

    def __repr__(self) -> str:
        return f"Quad({self.p1}, {self.p2}, {self.p3}, {self.p4})"

    def debug(
        self, argbColor: int = 0xFFFF0000, filled: bool = False, tag: str | None = None
    ) -> None:
        """Draw this quad as an overlay on RuneLite."""
        from escape.input.drawing import drawing

        xPoints = [self.p1.x, self.p2.x, self.p3.x, self.p4.x]
        yPoints = [self.p1.y, self.p2.y, self.p3.y, self.p4.y]
        drawing.addPolygon(xPoints, yPoints, argbColor, filled, tag)

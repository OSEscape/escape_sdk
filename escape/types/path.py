"""
Path and obstacle types for navigation.

Uses numpy arrays for efficient coordinate storage and projection integration.
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict, List

import numpy as np

from .packed_position import PackedPosition

if TYPE_CHECKING:
    from escape.types import Point, Quad
    from escape.world.projection import TileGrid


@dataclass
class PathObstacle:
    """Represents an obstacle along a path with origin, destination, and timing."""

    origin: PackedPosition
    dest: PackedPosition
    type: str
    duration: int
    displayInfo: str | None
    objectInfo: str | None

    @classmethod
    def fromDict(cls, data: Dict[str, Any]) -> "PathObstacle":
        """Create PathObstacle from dict."""
        return cls(
            origin=PackedPosition.fromPacked(data["origin"]),
            dest=PackedPosition.fromPacked(data["dest"]),
            type=data["type"],
            duration=data["duration"],
            displayInfo=data.get("displayInfo"),
            objectInfo=data.get("objectInfo"),
        )

    def __repr__(self) -> str:
        name = self.displayInfo or self.objectInfo or self.type
        return f"PathObstacle({name}, {self.duration} ticks)"


class Path:
    """Navigation path with numpy-backed coordinate storage for efficient vectorized operations."""

    __slots__ = ("_packed", "_obstacles")

    def __init__(self, packed: np.ndarray, obstacles: List[PathObstacle]):
        """Initialize path with packed positions and obstacles."""
        self._packed = packed.astype(np.int32)
        self._obstacles = obstacles

    @classmethod
    def fromDict(cls, data: Dict[str, Any]) -> "Path":
        """Create Path from Java response dict."""
        # Direct numpy conversion - instant for any size
        packed = np.array(data["path"], dtype=np.int32)

        # Obstacles are few, so list comprehension is fine
        obstacles = [PathObstacle.fromDict(obs) for obs in data.get("obstacles", [])]

        return cls(packed, obstacles)

    @property
    def worldX(self) -> np.ndarray:
        """World X coordinates (vectorized). Shape: [length]. X is bits 0-14."""
        return (self._packed & 0x7FFF).astype(np.int32)

    @property
    def worldY(self) -> np.ndarray:
        """World Y coordinates (vectorized). Shape: [length]. Y is bits 15-29."""
        return ((self._packed >> 15) & 0x7FFF).astype(np.int32)

    @property
    def plane(self) -> np.ndarray:
        """Plane values (vectorized). Shape: [length]."""
        return ((self._packed >> 30) & 0x3).astype(np.int32)

    @property
    def packed(self) -> np.ndarray:
        """Raw packed integers. Shape: [length]."""
        return self._packed

    def _getTileGrid(self) -> "TileGrid | None":
        """Get cached TileGrid from projection."""
        from escape.world.projection import projection

        return projection.tiles

    def getSceneCoords(self) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Convert world coords to scene coords, returning (sceneX, sceneY, inSceneMask)."""
        grid = self._getTileGrid()
        if grid is None:
            empty = np.array([], dtype=np.int32)
            return empty, empty, np.array([], dtype=np.bool_)

        sceneX = self.worldX - grid.baseX
        sceneY = self.worldY - grid.baseY

        inScene = (sceneX >= 0) & (sceneX < grid.sizeX) & (sceneY >= 0) & (sceneY < grid.sizeY)

        return sceneX, sceneY, inScene

    def getScreenCoords(self, margin: int = 0) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Get screen coordinates for path tiles, returning (screenX, screenY, visibleMask)."""
        grid = self._getTileGrid()
        if grid is None or len(self._packed) == 0:
            empty = np.array([], dtype=np.int32)
            return empty, empty, np.array([], dtype=np.bool_)

        sceneX, sceneY, inScene = self.getSceneCoords()

        # Initialize output arrays
        n = len(self._packed)
        screenX = np.zeros(n, dtype=np.int32)
        screenY = np.zeros(n, dtype=np.int32)
        visible = np.zeros(n, dtype=np.bool_)

        if not inScene.any():
            return screenX, screenY, visible

        # Get tile indices for in-scene tiles (clip to valid range)
        clippedX = sceneX.clip(0, grid.sizeX - 1)
        clippedY = sceneY.clip(0, grid.sizeY - 1)
        tileIdx = clippedX * grid.sizeY + clippedY

        # Get centers from grid cache
        centerX, centerY = grid.getTileCenters()
        screenX = centerX[tileIdx]
        screenY = centerY[tileIdx]

        # Visibility: in scene + valid tile + on screen
        tileValid = grid.tileValid[tileIdx]

        if margin == 0:
            onScreen = (
                (screenX >= grid.viewMinX)
                & (screenX < grid.viewMaxX)
                & (screenY >= grid.viewMinY)
                & (screenY < grid.viewMaxY)
            )
        else:
            onScreen = (
                (screenX >= grid.viewMinX - margin)
                & (screenX < grid.viewMaxX + margin)
                & (screenY >= grid.viewMinY - margin)
                & (screenY < grid.viewMaxY + margin)
            )

        visible = inScene & tileValid & onScreen

        return screenX, screenY, visible

    def getVisibleIndices(self, margin: int = 0) -> np.ndarray:
        """Get indices of path tiles visible on screen."""
        _, _, visible = self.getScreenCoords(margin=margin)
        return np.where(visible)[0]

    def getVisibleQuads(self) -> List["Quad"]:
        """Get Quads for all visible path tiles."""
        grid = self._getTileGrid()
        if grid is None:
            return []

        sceneX, sceneY, inScene = self.getSceneCoords()
        indices = np.where(inScene)[0]

        quads = []
        for i in indices:
            sx, sy = sceneX[i], sceneY[i]
            tileIdx = sx * grid.sizeY + sy
            if grid.tileOnScreen[tileIdx]:
                quads.append(grid.getTileQuad(tileIdx))

        return quads

    def getScreenPoint(self, i: int) -> "Point | None":
        """Get screen Point for path tile at index, or None if not in scene."""
        from escape.types import Point

        grid = self._getTileGrid()
        if grid is None or i < 0 or i >= len(self._packed):
            return None

        sceneX = int(self.worldX[i]) - grid.baseX
        sceneY = int(self.worldY[i]) - grid.baseY

        if not (0 <= sceneX < grid.sizeX and 0 <= sceneY < grid.sizeY):
            return None

        tileIdx = sceneX * grid.sizeY + sceneY
        if not grid.tileValid[tileIdx]:
            return None

        centerX, centerY = grid.getTileCenters()
        return Point(int(centerX[tileIdx]), int(centerY[tileIdx]))

    def getQuad(self, i: int) -> "Quad | None":
        """Get Quad for path tile at index, or None if not in scene."""
        grid = self._getTileGrid()
        if grid is None or i < 0 or i >= len(self._packed):
            return None

        sceneX = int(self.worldX[i]) - grid.baseX
        sceneY = int(self.worldY[i]) - grid.baseY

        if not (0 <= sceneX < grid.sizeX and 0 <= sceneY < grid.sizeY):
            return None

        tileIdx = sceneX * grid.sizeY + sceneY
        return grid.getTileQuad(tileIdx)

    @property
    def obstacles(self) -> List[PathObstacle]:
        """Get all obstacles in path."""
        return self._obstacles

    def length(self) -> int:
        """Get path length in tiles."""
        return len(self._packed)

    def isEmpty(self) -> bool:
        """Check if path is empty."""
        return len(self._packed) == 0

    def getPosition(self, i: int) -> PackedPosition | None:
        """Get PackedPosition at index, or None if out of bounds."""
        if i < 0 or i >= len(self._packed):
            return None
        return PackedPosition.fromPacked(int(self._packed[i]))

    def getStart(self) -> PackedPosition | None:
        """Get start position."""
        return self.getPosition(0)

    def getEnd(self) -> PackedPosition | None:
        """Get end position (destination)."""
        return self.getPosition(len(self._packed) - 1)

    def getNextTile(self, current: PackedPosition) -> PackedPosition | None:
        """Get next tile from current position, or None if at end."""
        # Vectorized search
        matches = np.where(self._packed == current.packed)[0]
        if len(matches) == 0:
            return None
        idx = matches[0]
        if idx < len(self._packed) - 1:
            return PackedPosition.fromPacked(int(self._packed[idx + 1]))
        return None

    def getObstacleAt(self, position: PackedPosition) -> PathObstacle | None:
        """Get obstacle at position, or None if no obstacle."""
        for obstacle in self._obstacles:
            if obstacle.origin == position:
                return obstacle
        return None

    def hasObstacles(self) -> bool:
        """Check if path has any obstacles."""
        return len(self._obstacles) > 0

    def getTotalDuration(self) -> int:
        """Get total estimated duration in ticks (walking + obstacles)."""
        # Approximate: 1 tile = 1 tick walking
        walk_ticks = len(self._packed)
        obstacle_ticks = sum(obs.duration for obs in self._obstacles)
        return walk_ticks + obstacle_ticks

    def getTotalSeconds(self) -> float:
        """Get total estimated duration in seconds (ticks * 0.6)."""
        return self.getTotalDuration() * 0.6

    def distanceToTile(self, worldX: int, worldY: int) -> np.ndarray:
        """Calculate Chebyshev distance from each path tile to a point."""
        dx = np.abs(self.worldX - worldX)
        dy = np.abs(self.worldY - worldY)
        return np.maximum(dx, dy)

    def findClosestTile(self, worldX: int, worldY: int) -> int:
        """Find index of path tile closest to a point, or -1 if empty."""
        if len(self._packed) == 0:
            return -1
        return int(self.distanceToTile(worldX, worldY).argmin())

    def sliceFrom(self, startIdx: int) -> "Path":
        """Create new Path starting from given index."""
        if startIdx < 0 or startIdx >= len(self._packed):
            return Path(np.array([], dtype=np.int32), [])

        newPacked = self._packed[startIdx:]

        # Filter obstacles that are still ahead
        remainingPositions = set(newPacked.tolist())
        newObstacles = [obs for obs in self._obstacles if obs.origin.packed in remainingPositions]

        return Path(newPacked, newObstacles)

    def __len__(self) -> int:
        """Support len() builtin."""
        return len(self._packed)

    def __iter__(self):
        """Iterate over PackedPosition objects (creates on-demand)."""
        for p in self._packed:
            yield PackedPosition.fromPacked(int(p))

    def __getitem__(self, index) -> PackedPosition:
        """Support indexing (creates PackedPosition on-demand)."""
        return PackedPosition.fromPacked(int(self._packed[index]))

    def __repr__(self) -> str:
        return (
            f"Path({len(self._packed)} tiles, {len(self._obstacles)} obstacles, "
            f"~{self.getTotalSeconds():.1f}s)"
        )

"""Walker module - handles walking from point A to point B with target tracking."""

from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from escape.types import Quad
    from escape.types.path import Path

# Local coordinate units per tile (RuneLite LocalPoint)
LOCAL_UNITS_PER_TILE = 128


class Walker:
    """Walker for navigating with smart target tracking."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance

    def _init(self):
        """Actual initialization, runs once."""
        pass

    def _getPlayerPosition(self) -> tuple[int, int, int] | None:
        """Get player world position (x, y, plane) from cache."""
        from escape.client import client

        pos = client.cache.position
        if pos is None:
            return None
        return (pos.get("x", 0), pos.get("y", 0), pos.get("plane", 0))

    def _getPlayerScenePosition(self) -> tuple[int, int] | None:
        """Get player scene position (sceneX, sceneY) from cache."""
        from escape.client import client

        pos = client.cache.scenePosition
        if pos is None:
            return None
        return (pos.get("sceneX", 0), pos.get("sceneY", 0))

    def _getTargetScenePosition(self) -> tuple[int, int] | None:
        """Get current walk target in scene coordinates."""
        from escape.client import client

        target = client.cache.targetLocation
        if target is None:
            return None

        localX = target.get("x")
        localY = target.get("y")
        if localX is None or localY is None:
            return None

        # Convert local to scene coords (128 local units = 1 tile)
        sceneX = localX // LOCAL_UNITS_PER_TILE
        sceneY = localY // LOCAL_UNITS_PER_TILE

        return (sceneX, sceneY)

    def _distanceToTarget(self) -> int | None:
        """Get Chebyshev distance from player to current walk target."""
        playerPos = self._getPlayerScenePosition()
        targetPos = self._getTargetScenePosition()

        if playerPos is None or targetPos is None:
            return None

        playerX, playerY = playerPos
        targetX, targetY = targetPos

        return max(abs(targetX - playerX), abs(targetY - playerY))

    def hasTarget(self) -> bool:
        """Check if player currently has a walk target."""
        return self._getTargetScenePosition() is not None

    def isNearTarget(self, threshold: int = 2) -> bool:
        """Check if player is near their current walk target (within threshold tiles)."""
        dist = self._distanceToTarget()
        if dist is None:
            return True  # No target = effectively "at" target

        return dist <= threshold

    def shouldClickNewTile(self, threshold: int = 2) -> bool:
        """Determine if we should click a new tile (idle or near target)."""
        return self.isNearTarget(threshold=threshold)

    def _findFirstObstacleIndex(self, path: "Path") -> int:
        """Find the index of the first obstacle on the path."""
        if not path.hasObstacles():
            return path.length()

        # Find the earliest obstacle origin
        firstObstacleIdx = path.length()
        for obstacle in path.obstacles:
            # Find where this obstacle's origin is on the path
            matches = np.where(path.packed == obstacle.origin.packed)[0]
            if len(matches) > 0:
                idx = int(matches[0])
                if idx < firstObstacleIdx:
                    firstObstacleIdx = idx

        return firstObstacleIdx

    def _selectWalkTile(
        self,
        path: "Path",
        visibleIndices: np.ndarray,
        playerX: int,
        playerY: int,
        maxIndex: int,
    ) -> int | None:
        """Select the optimal tile to click for walking (visible, clickable, far enough)."""
        from escape.world.scene import scene

        # Filter to tiles before obstacle
        validIndices = visibleIndices[visibleIndices < maxIndex]

        if len(validIndices) == 0:
            return None

        # Filter by Chebyshev distance <= 19 (same as Java isTileClickable)
        worldX = path.worldX[validIndices]
        worldY = path.worldY[validIndices]
        dist = np.maximum(np.abs(worldX - playerX), np.abs(worldY - playerY))
        withinRange = dist <= 19
        validIndices = validIndices[withinRange]

        if len(validIndices) == 0:
            return None

        # Get tile grid for viewport bounds
        grid = scene._getTileGrid()
        if grid is None:
            return None

        # Filter to tiles whose quad is FULLY inside viewport (all 4 corners)
        clickableIndices = []
        for idx in validIndices:
            quad = path.getQuad(int(idx))
            if quad is not None:
                # Check all 4 vertices are inside viewport
                allInside = all(
                    grid.viewMinX <= p.x <= grid.viewMaxX and grid.viewMinY <= p.y <= grid.viewMaxY
                    for p in quad.vertices
                )
                if allInside:
                    clickableIndices.append(int(idx))

        if len(clickableIndices) == 0:
            return None

        clickableIndices = np.array(clickableIndices)

        # Get world coordinates for clickable tiles
        worldX = path.worldX[clickableIndices]
        worldY = path.worldY[clickableIndices]

        # Calculate distance from player (Chebyshev)
        dist = np.maximum(np.abs(worldX - playerX), np.abs(worldY - playerY))

        # Filter out tiles too close (< 3 tiles away)
        farEnough = dist >= 3
        if not farEnough.any():
            # If all tiles are close, just pick the furthest
            bestLocal = int(np.argmax(dist))
            return int(clickableIndices[bestLocal])

        # Among far enough tiles, pick the one furthest along the path
        # (which is the highest index in clickableIndices)
        farMask = np.array(farEnough)
        farIndices = clickableIndices[farMask]
        return int(farIndices[-1])  # Last one is furthest along path

    def clickTile(self, worldX: int, worldY: int) -> bool:
        """Click a specific world tile to walk to it."""
        from escape.client import client
        from escape.world.scene import scene

        # Get the quad for this tile
        quad = scene.getTileQuad(worldX, worldY)
        if quad is None:
            return False

        # Hover on the tile
        quad.hover()

        # Wait for WALK action to appear in menu
        if not client.interactions.menu.waitHasType("WALK", timeout=0.5):
            return False

        # Click the walk action
        return client.interactions.menu.clickOptionType("WALK")

    def walkTo(
        self,
        destX: int,
        destY: int,
        destPlane: int = 0,
        margin: int = 50,
        nearTargetThreshold: int = 2,
    ) -> bool:
        """Walk towards destination by clicking a tile along the path."""
        from escape.navigation.pathfinder import pathfinder

        # Get player position
        playerPos = self._getPlayerPosition()
        if playerPos is None:
            return False

        playerX, playerY, playerPlane = playerPos

        # Check if already at destination
        if playerX == destX and playerY == destY and playerPlane == destPlane:
            return True  # Already there

        # Check if we should click a new tile or wait
        if not self.shouldClickNewTile(threshold=nearTargetThreshold):
            # Still walking to current target, no need to click
            return True  # Return True because we're making progress

        # Get path to destination
        path = pathfinder.getPath(destX, destY, destPlane)
        if path is None or path.isEmpty():
            return False

        # Find first obstacle (we'll walk up to it)
        obstacleIdx = self._findFirstObstacleIndex(path)

        # Get visible path tiles (with margin to avoid edge clicks)
        visibleIndices = path.getVisibleIndices(margin=margin)

        if len(visibleIndices) == 0:
            # No visible path tiles - might need to turn camera or wait
            return False

        # Select optimal tile to click
        targetIdx = self._selectWalkTile(path, visibleIndices, playerX, playerY, obstacleIdx)

        if targetIdx is None:
            return False

        # Get the quad for this tile
        quad = path.getQuad(targetIdx)
        if quad is None:
            return False

        # Click the tile
        return self._clickWalkQuad(quad)

    def _clickWalkQuad(self, quad: "Quad") -> bool:
        """Hover over quad and click with WALK action."""
        from escape.client import client

        # Hover on the tile
        quad.hover()

        # Wait for WALK action to appear in menu
        if not client.interactions.menu.waitHasType("WALK", timeout=0.5):
            return False

        # Click the walk action
        return client.interactions.menu.clickOptionType("WALK")

    def isMoving(self) -> bool:
        """Check if player is currently moving (has a walk target)."""
        return self.hasTarget()

    def distanceToDestination(self, destX: int, destY: int) -> int:
        """Get Chebyshev distance from player to destination (-1 if unknown)."""
        playerPos = self._getPlayerPosition()
        if playerPos is None:
            return -1

        playerX, playerY, _ = playerPos
        return max(abs(destX - playerX), abs(destY - playerY))


# Module-level instance
walker = Walker()

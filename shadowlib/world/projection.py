"""Projection utilities for converting local coordinates to screen coordinates."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

import numpy as np

from shadowlib.types.point import Point

if TYPE_CHECKING:
    from shadowlib._internal.cache.event_cache import EventCache


@dataclass
class CameraState:
    """Per-frame camera state."""

    cameraX: float
    cameraY: float
    cameraZ: float
    cameraPitch: float  # radians
    cameraYaw: float  # radians
    scale: int


@dataclass
class EntityTransform:
    """Per-frame entity transform data (for WorldEntity instances)."""

    entityX: int  # we.getLocalLocation().getX()
    entityY: int  # we.getLocalLocation().getY()
    orientation: int  # we.getOrientation(), 0-2047 JAU
    groundHeight: int  # Perspective.getTileHeight(topLevel, entityLoc, topLevel.getPlane())


@dataclass
class EntityConfig:
    """Static WorldEntity config - set once on WorldView load."""

    boundsX: int  # config.getBoundsX()
    boundsY: int  # config.getBoundsY()
    boundsWidth: int  # config.getBoundsWidth()
    boundsHeight: int  # config.getBoundsHeight()

    @property
    def centerX(self) -> int:
        """Rotation pivot X in local units."""
        return (self.boundsX + self.boundsWidth // 2) * 128

    @property
    def centerY(self) -> int:
        """Rotation pivot Y in local units."""
        return (self.boundsY + self.boundsHeight // 2) * 128


class Projection:
    """
    Fast projection from local coordinates to canvas coordinates.
    Mirrors RuneLite's Perspective class logic.

    This is a singleton - only one instance is ever created.

    Scene data (tile heights, bridge flags, entity config) is automatically
    configured when world_view_loaded events are received via the EventCache.

    Frame-specific data (camera, entity transform) is refreshed automatically
    from EventCache before each projection call via refreshFromCache().

    Example:
        >>> from shadowlib.world.projection import projection
        >>>
        >>> # Scene data is auto-configured from events - no setup needed!
        >>>
        >>> # Project points (auto-refreshes camera/entity state)
        >>> screenX, screenY = projection.localToCanvasSingle(localX, localY, plane)
        >>>
        >>> # Or manually refresh if needed:
        >>> projection.refreshFromCache()
    """

    LOCAL_COORD_BITS = 7
    LOCAL_TILE_SIZE = 128  # 1 << 7

    # Fixed viewport constants - these don't change
    VIEWPORT_WIDTH = 512
    VIEWPORT_HEIGHT = 334
    VIEWPORT_X_OFFSET = 4
    VIEWPORT_Y_OFFSET = 4

    _instance = None
    _eventCache: "EventCache | None" = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance

    def _init(self):
        # Pre-compute sin/cos lookup tables (JAU units: 0-2047)
        unit = np.pi / 1024
        angles = np.arange(2048) * unit
        self.sinTable = np.sin(angles).astype(np.float32)
        self.cosTable = np.cos(angles).astype(np.float32)

        # Scene data (set on scene load via world_view_loaded event)
        self.tileHeights: np.ndarray | None = None  # [4, sizeX, sizeY]
        self.bridgeFlags: np.ndarray | None = None  # [sizeX, sizeY] bool
        self.baseX: int = 0
        self.baseY: int = 0
        self.sizeX: int = 104
        self.sizeY: int = 104

        # Entity config (set on scene load, None for top-level)
        self.entityConfig: EntityConfig | None = None

        # Camera state (set per frame from EventCache)
        self.camera: CameraState | None = None

        # Entity transform (set per frame from EventCache, None for top-level)
        self.entityTransform: EntityTransform | None = None

        # Pre-computed trig values
        self._pitchSin: float = 0.0
        self._pitchCos: float = 1.0
        self._yawSin: float = 0.0
        self._yawCos: float = 1.0
        self._orientSin: float = 0.0
        self._orientCos: float = 1.0

        # Pre-computed transform values
        self._centerX: int = 0
        self._centerY: int = 0
        self._entityX: int = 0
        self._entityY: int = 0
        self._groundHeight: int = 0

    # -------------------------------------------------------------------------
    # EventCache integration
    # -------------------------------------------------------------------------

    def _getEventCache(self, debug: bool = False) -> "EventCache | None":
        """Get EventCache singleton, lazily imported to avoid circular imports."""
        if Projection._eventCache is None:
            try:
                from shadowlib.globals import getEventCache

                Projection._eventCache = getEventCache()
                if debug:
                    print("  _getEventCache: successfully loaded cache")
            except Exception as e:
                if debug:
                    print(f"  _getEventCache: FAILED with exception: {e}")
                return None
        return Projection._eventCache

    def refreshFromCache(self, debug: bool = False) -> bool:
        """
        Refresh camera and entity transform state from EventCache.

        Called automatically before projection operations. Can also be called
        manually if you need to ensure fresh state.

        Args:
            debug: If True, print debug information

        Returns:
            True if camera state was successfully loaded, False otherwise.
        """
        cache = self._getEventCache(debug=debug)
        if cache is None:
            if debug:
                print("  refreshFromCache: FAILED - cache is None")
            return False

        # Get camera state from EventCache (only need first 6 values)
        cameraData = cache.getCameraState()
        if debug:
            print(f"  refreshFromCache: cameraData={'available' if cameraData else 'None'}")
            if cameraData:
                print(
                    f"  refreshFromCache: cameraX={cameraData[0]}, cameraY={cameraData[1]}, cameraZ={cameraData[2]}"
                )
                print(
                    f"  refreshFromCache: cameraPitch={cameraData[3]}, cameraYaw={cameraData[4]}, scale={cameraData[5]}"
                )
                print(
                    f"  refreshFromCache: viewport={self.VIEWPORT_WIDTH}x{self.VIEWPORT_HEIGHT}, offset=({self.VIEWPORT_X_OFFSET}, {self.VIEWPORT_Y_OFFSET}) [constants]"
                )
        if cameraData:
            cameraX, cameraY, cameraZ, cameraPitch, cameraYaw, scale = cameraData[:6]

            self.camera = CameraState(
                cameraX=cameraX,
                cameraY=cameraY,
                cameraZ=cameraZ,
                cameraPitch=cameraPitch,
                cameraYaw=cameraYaw,
                scale=scale,
            )

            # Pre-compute camera trig values
            self._pitchSin = np.sin(cameraPitch)
            self._pitchCos = np.cos(cameraPitch)
            self._yawSin = np.sin(cameraYaw)
            self._yawCos = np.cos(cameraYaw)
        else:
            return False

        # Get entity transform from EventCache (may be None for top-level)
        entityData = cache.getEntityTransform()
        if entityData:
            entityX, entityY, orientation, groundHeightOffset = entityData

            self.entityTransform = EntityTransform(
                entityX=entityX,
                entityY=entityY,
                orientation=orientation,
                groundHeight=groundHeightOffset,
            )

            # Pre-compute entity trig values
            self._orientSin = self.sinTable[orientation]
            self._orientCos = self.cosTable[orientation]
            self._entityX = entityX
            self._entityY = entityY
            self._groundHeight = groundHeightOffset
        else:
            # Top-level world: identity transform
            self.entityTransform = None
            self._orientSin = 0.0
            self._orientCos = 1.0
            self._entityX = 0
            self._entityY = 0
            self._groundHeight = 0

        return True

    # -------------------------------------------------------------------------
    # Scene load methods
    # -------------------------------------------------------------------------

    def setScene(
        self,
        tileHeights: np.ndarray,
        bridgeFlags: np.ndarray,
        baseX: int,
        baseY: int,
        sizeX: int,
        sizeY: int,
    ):
        """
        Set scene data on WorldView load.

        Args:
            tileHeights: [4, sizeX, sizeY] from worldView.getTileHeights()
            bridgeFlags: [sizeX, sizeY] bool - (tileSettings[1] & 2) != 0
            baseX, baseY: worldView.getBaseX/Y()
            sizeX, sizeY: worldView.getSizeX/Y()
        """
        self.tileHeights = tileHeights.astype(np.int32)
        self.bridgeFlags = bridgeFlags.astype(np.bool_)
        self.baseX = baseX
        self.baseY = baseY
        self.sizeX = sizeX
        self.sizeY = sizeY

    def setEntityConfig(self, config: EntityConfig | None):
        """
        Set WorldEntity config on WorldView load. None for top-level world.

        Args:
            config: EntityConfig from we.getConfig(), or None if top-level
        """
        self.entityConfig = config
        if config:
            self._centerX = config.centerX
            self._centerY = config.centerY
        else:
            self._centerX = 0
            self._centerY = 0

    # -------------------------------------------------------------------------
    # Per-frame methods
    # -------------------------------------------------------------------------

    def setCamera(self, camera: CameraState):
        """Set camera state (every frame)."""
        self.camera = camera
        self._pitchSin = np.sin(camera.cameraPitch)
        self._pitchCos = np.cos(camera.cameraPitch)
        self._yawSin = np.sin(camera.cameraYaw)
        self._yawCos = np.cos(camera.cameraYaw)

    def setEntityTransform(self, transform: EntityTransform | None):
        """
        Set entity transform (every frame). None for top-level world.

        Args:
            transform: EntityTransform with current position/orientation, or None
        """
        self.entityTransform = transform
        if transform:
            self._orientSin = self.sinTable[transform.orientation]
            self._orientCos = self.cosTable[transform.orientation]
            self._entityX = transform.entityX
            self._entityY = transform.entityY
            self._groundHeight = transform.groundHeight
        else:
            self._orientSin = 0.0
            self._orientCos = 1.0
            self._entityX = 0
            self._entityY = 0
            self._groundHeight = 0

    # -------------------------------------------------------------------------
    # Core projection
    # -------------------------------------------------------------------------

    def localToCanvas(
        self,
        localX: np.ndarray,
        localY: np.ndarray,
        plane: int,
        heightOffset: int = 0,
        autoRefresh: bool = True,
        debug: bool = False,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Project local points to canvas coordinates.

        Automatically refreshes camera and entity state from EventCache before
        projection (can be disabled with autoRefresh=False for batch operations).

        Args:
            localX, localY: Arrays of local coordinates (any shape)
            plane: The plane/level
            heightOffset: Optional height offset (e.g., for actor height)
            autoRefresh: If True (default), refresh state from EventCache first
            debug: If True, print debug information

        Returns:
            screenX, screenY, valid: Arrays matching input shape

        Raises:
            RuntimeError: If scene data or camera state is not available
        """
        # Refresh frame-specific state from EventCache
        if autoRefresh:
            refreshed = self.refreshFromCache(debug=debug)
            if debug:
                print(f"  localToCanvas: autoRefresh={autoRefresh}, refreshed={refreshed}")

        # Validate required state
        if self.tileHeights is None or self.bridgeFlags is None:
            if debug:
                print(
                    f"  localToCanvas: FAILED - tileHeights={self.tileHeights is not None}, bridgeFlags={self.bridgeFlags is not None}"
                )
            raise RuntimeError("Scene data not loaded. Waiting for world_view_loaded event.")
        if self.camera is None:
            if debug:
                print("  localToCanvas: FAILED - camera is None")
            raise RuntimeError("Camera state not available. Waiting for camera_changed event.")

        localX = np.atleast_1d(np.asarray(localX, dtype=np.float32))
        localY = np.atleast_1d(np.asarray(localY, dtype=np.float32))
        origShape = localX.shape

        localX = localX.ravel()
        localY = localY.ravel()

        # Get tile heights with bridge correction
        sceneX = (localX.astype(np.int32) >> self.LOCAL_COORD_BITS).clip(0, self.sizeX - 1)
        sceneY = (localY.astype(np.int32) >> self.LOCAL_COORD_BITS).clip(0, self.sizeY - 1)

        tilePlane = np.where((plane < 3) & self.bridgeFlags[sceneX, sceneY], plane + 1, plane)
        z = self.tileHeights[tilePlane, sceneX, sceneY].astype(np.float32)
        z += self._groundHeight - heightOffset

        # Transform local to world (identity when top-level)
        if self.entityConfig is None:
            # Top-level world: no transform needed
            worldX = localX
            worldY = localY
        else:
            # Inside WorldEntity: apply rotation and translation
            cx = localX - self._centerX
            cy = localY - self._centerY
            worldX = self._entityX + cy * self._orientSin + cx * self._orientCos
            worldY = self._entityY + cy * self._orientCos - cx * self._orientSin

        # Camera-relative coordinates
        dx = worldX - self.camera.cameraX
        dy = worldY - self.camera.cameraY
        dz = z - self.camera.cameraZ

        if debug:
            print("  localToCanvas math:")
            print(
                f"    entityConfig={self.entityConfig is not None} (transform applied: {self.entityConfig is not None})"
            )
            print(f"    localX={localX[0]}, localY={localY[0]}, z={z[0]}")
            print(f"    worldX={worldX[0]}, worldY={worldY[0]}")
            print(
                f"    cameraX={self.camera.cameraX}, cameraY={self.camera.cameraY}, cameraZ={self.camera.cameraZ}"
            )
            print(f"    dx={dx[0]}, dy={dy[0]}, dz={dz[0]}")
            print(f"    yawCos={self._yawCos}, yawSin={self._yawSin}")
            print(f"    pitchCos={self._pitchCos}, pitchSin={self._pitchSin}")

        # Rotate by camera yaw and pitch
        x1 = dx * self._yawCos + dy * self._yawSin
        y1 = dy * self._yawCos - dx * self._yawSin
        y2 = dz * self._pitchCos - y1 * self._pitchSin
        depth = y1 * self._pitchCos + dz * self._pitchSin

        if debug:
            print(f"    x1={x1[0]}, y1={y1[0]}, y2={y2[0]}, depth={depth[0]}")

        # Project to screen
        valid = depth >= 50
        safeDepth = np.where(valid, depth, 1.0)

        screenX = (self.VIEWPORT_WIDTH / 2 + x1 * self.camera.scale / safeDepth).astype(np.int32)
        screenY = (self.VIEWPORT_HEIGHT / 2 + y2 * self.camera.scale / safeDepth).astype(np.int32)
        screenX += self.VIEWPORT_X_OFFSET
        screenY += self.VIEWPORT_Y_OFFSET

        return screenX.reshape(origShape), screenY.reshape(origShape), valid.reshape(origShape)

    # -------------------------------------------------------------------------
    # Convenience methods
    # -------------------------------------------------------------------------

    def localToCanvasSingle(
        self, localX: int, localY: int, plane: int, heightOffset: int = 0, debug: bool = False
    ) -> Point | None:
        """
        Project a single local point to screen coordinates.

        Args:
            localX: Local X coordinate (scene tile * 128)
            localY: Local Y coordinate (scene tile * 128)
            plane: The plane/level (0-3)
            heightOffset: Optional height offset above ground
            debug: If True, print debug information

        Returns:
            Point with screen coordinates, or None if behind camera
        """
        sx, sy, valid = self.localToCanvas(
            np.array([localX]), np.array([localY]), plane, heightOffset, debug=debug
        )
        if debug:
            print(f"  localToCanvasSingle: sx={sx[0]}, sy={sy[0]}, valid={valid[0]}")
        return Point(int(sx[0]), int(sy[0])) if valid[0] else None

    def tileToCanvas(
        self, sceneX: int, sceneY: int, plane: int, heightOffset: int = 0, debug: bool = False
    ) -> Point | None:
        """
        Project a scene tile center to screen coordinates.

        Args:
            sceneX: Scene tile X coordinate (0 to sizeX-1)
            sceneY: Scene tile Y coordinate (0 to sizeY-1)
            plane: The plane/level (0-3)
            heightOffset: Optional height offset above ground
            debug: If True, print debug information

        Returns:
            Point with screen coordinates, or None if behind camera/off screen
        """
        localX = (sceneX << self.LOCAL_COORD_BITS) + (self.LOCAL_TILE_SIZE // 2)
        localY = (sceneY << self.LOCAL_COORD_BITS) + (self.LOCAL_TILE_SIZE // 2)
        if debug:
            print(f"  tileToCanvas: localX={localX}, localY={localY}")
        return self.localToCanvasSingle(localX, localY, plane, heightOffset, debug=debug)

    def worldTileToCanvas(
        self, worldX: int, worldY: int, plane: int, heightOffset: int = 0, debug: bool = False
    ) -> Point | None:
        """
        Project a world tile to screen coordinates.

        Convenience method that converts world tile coords to scene coords first.

        Args:
            worldX: World tile X coordinate (absolute map position)
            worldY: World tile Y coordinate (absolute map position)
            plane: The plane/level (0-3)
            heightOffset: Optional height offset above ground
            debug: If True, print debug information

        Returns:
            Point with screen coordinates, or None if off scene/behind camera
        """
        # Ensure scene data is loaded before checking coords
        # This triggers Client initialization which processes world_view_loaded
        if self.tileHeights is None:
            if debug:
                print("[DEBUG] worldTileToCanvas: scene data not loaded, triggering refresh")
            self.refreshFromCache(debug=debug)

        sceneX = worldX - self.baseX
        sceneY = worldY - self.baseY

        if debug:
            print(f"[DEBUG] worldTileToCanvas({worldX}, {worldY}, {plane})")
            print(
                f"  baseX={self.baseX}, baseY={self.baseY}, sizeX={self.sizeX}, sizeY={self.sizeY}"
            )
            print(f"  sceneX={sceneX}, sceneY={sceneY}")
            print(f"  tileHeights loaded: {self.tileHeights is not None}")
            print(f"  camera loaded: {self.camera is not None}")

        # Check if tile is within current scene
        if not (0 <= sceneX < self.sizeX and 0 <= sceneY < self.sizeY):
            if debug:
                print(
                    f"  FAILED: scene coords out of bounds (0 <= {sceneX} < {self.sizeX} and 0 <= {sceneY} < {self.sizeY})"
                )
            return None

        return self.tileToCanvas(sceneX, sceneY, plane, heightOffset, debug=debug)

    def isOnScreen(self, sceneX: int, sceneY: int, plane: int) -> bool:
        """
        Check if a scene tile is visible on screen.

        Args:
            sceneX: Scene tile X coordinate (0 to sizeX-1)
            sceneY: Scene tile Y coordinate (0 to sizeY-1)
            plane: The plane/level (0-3)

        Returns:
            True if tile center projects to a valid screen position
        """
        return self.tileToCanvas(sceneX, sceneY, plane) is not None


# Module-level singleton instance
projection = Projection()

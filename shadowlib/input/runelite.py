"""RuneLite window detection and position management."""

import subprocess
import time
from typing import List, Optional, Tuple


class RuneLite:
    """
    RuneLite window position tracker.
    Manages window detection and automatic position refresh for input operations.
    """

    def __init__(self, window_title: str = "RuneLite", auto_refresh: bool = True):
        """
        Initialize RuneLite window tracker.

        Args:
            window_title: Title of the RuneLite window to track
            auto_refresh: If True, automatically refresh window position when needed
        """
        self.window_title = window_title
        self.window_offset: Tuple[int, int] | None = None
        self.window_size: Tuple[int, int] | None = None
        self.auto_refresh = auto_refresh
        self._last_detection_time = 0.0

        # Try to detect window on initialization
        self.detectWindow()

    def _findWindowIds(self) -> List[str]:
        """
        Find all window IDs for RuneLite using xdotool.

        Returns:
            List of window IDs, empty list if none found
        """
        try:
            result = subprocess.run(
                ['xdotool', 'search', '--name', self.window_title],
                capture_output=True,
                text=True,
                check=False
            )

            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip().split('\n')

            return []

        except (FileNotFoundError, Exception):
            return []

    def detectWindow(self) -> bool:
        """
        Detect RuneLite window and get its position/size (client area without decorations).

        Returns:
            True if window found, False otherwise
        """
        try:
            # Use wmctrl to find the exact RuneLite window
            result = subprocess.run(
                ['wmctrl', '-l', '-G'],
                capture_output=True,
                text=True,
                check=False
            )

            if result.returncode != 0:
                return False

            # Parse wmctrl output to find RuneLite window
            for line in result.stdout.split('\n'):
                if self.window_title in line:
                    parts = line.split()
                    if len(parts) >= 7:
                        # Check if this is actually the RuneLite client window
                        window_name = ' '.join(parts[7:])

                        # Skip if it's not the actual RuneLite window
                        if not window_name.startswith('RuneLite'):
                            continue

                        # Format: window_id desktop x y width height client_machine window_title
                        window_id = parts[0]
                        x = int(parts[2])
                        y = int(parts[3])
                        width = int(parts[4])
                        height = int(parts[5])

                        # Use xwininfo to get the client area (without decorations)
                        geom_result = subprocess.run(
                            ['xwininfo', '-id', window_id],
                            capture_output=True,
                            text=True,
                            check=False
                        )

                        if geom_result.returncode == 0:
                            # Parse xwininfo for more accurate client coordinates
                            for info_line in geom_result.stdout.split('\n'):
                                info_line = info_line.strip()
                                if info_line.startswith('Absolute upper-left X:'):
                                    x = int(info_line.split(':')[1].strip())
                                elif info_line.startswith('Absolute upper-left Y:'):
                                    y = int(info_line.split(':')[1].strip())
                                elif info_line.startswith('Width:'):
                                    width = int(info_line.split(':')[1].strip())
                                elif info_line.startswith('Height:'):
                                    height = int(info_line.split(':')[1].strip())

                        self.window_offset = (x, y)
                        self.window_size = (width, height)
                        self._last_detection_time = time.time()
                        return True

            return False

        except FileNotFoundError:
            return False
        except Exception:
            return False

    def activateWindow(self) -> bool:
        """
        Activate and bring RuneLite window to foreground.
        Uses xdotool to unminimize and activate the window.
        Tries all window IDs since RuneLite has multiple windows.

        Returns:
            True if successful, False otherwise
        """
        window_ids = self._findWindowIds()
        if not window_ids:
            return False

        try:
            # Try to activate each window ID
            for window_id in window_ids:
                # Unminimize the window (if minimized)
                subprocess.run(
                    ['xdotool', 'windowmap', window_id],
                    capture_output=True,
                    check=False
                )

                # Activate the window
                subprocess.run(
                    ['xdotool', 'windowactivate', window_id],
                    capture_output=True,
                    check=False
                )

            # Wait for window to come to foreground
            time.sleep(0.5)

            # Re-detect window position after activation
            self.detectWindow()

            # Verify the window is now active
            return self.isWindowActive()

        except (FileNotFoundError, Exception):
            return False

    def isWindowMinimized(self) -> bool:
        """
        Check if window is minimized.

        RuneLite has multiple window IDs - only consider it minimized if
        ALL windows are unmapped.

        Returns:
            True if minimized, False otherwise
        """
        window_ids = self._findWindowIds()
        if not window_ids:
            return False

        try:
            # Check each window ID - if ANY is viewable, window is not minimized
            for window_id in window_ids:
                state_result = subprocess.run(
                    ['xwininfo', '-id', window_id],
                    capture_output=True,
                    text=True,
                    check=False
                )

                if 'IsViewable' in state_result.stdout:
                    return False

            # All windows are unmapped, so window is minimized
            return True

        except Exception:
            # If we can't determine, assume not minimized
            return False

    def isWindowActive(self) -> bool:
        """
        Check if the window is currently active (in foreground).

        RuneLite may have multiple window IDs (parent/child windows),
        so we check if the active window matches any of them.

        Returns:
            True if window is active, False otherwise
        """
        window_ids = self._findWindowIds()
        if not window_ids:
            return False

        try:
            # Get the currently active window
            active_result = subprocess.run(
                ['xdotool', 'getactivewindow'],
                capture_output=True,
                text=True,
                check=False
            )

            if active_result.returncode != 0 or not active_result.stdout.strip():
                return False

            active_window_id = active_result.stdout.strip()

            # Check if the active window is one of the RuneLite windows
            return active_window_id in window_ids

        except Exception:
            # If we can't determine, assume not active
            return False

    def ensureWindowReady(self) -> bool:
        """
        Ensure window is detected, not minimized, and activated.

        Returns:
            True if window is ready, False otherwise
        """
        # Detect window if not already detected
        if not self.window_offset:
            if not self.detectWindow():
                return False

        # Activate window (this also unminimizes it)
        return self.activateWindow()

    def refreshWindowPosition(self, force: bool = False, max_age: float = 10.0) -> bool:
        """
        Refresh the window position if it's stale or if forced.
        Activates the window if it's minimized or inactive.

        Args:
            force: If True, always refresh regardless of age
            max_age: Maximum age in seconds before considering position stale (default 10.0)

        Returns:
            True if refresh was successful, False otherwise
        """
        # Check window state
        is_minimized = self.isWindowMinimized()
        is_active = self.isWindowActive()

        if is_minimized or not is_active:
            # Activate window (this unminimizes if needed and re-detects position)
            return self.activateWindow()

        # Window state is OK, check if position is stale
        if not force:
            position_age = time.time() - self._last_detection_time
            if position_age < max_age:
                return True  # Position is still fresh

        # Position is stale, re-detect it
        return self.detectWindow()

    def _autoRefresh(self) -> None:
        """Auto-refresh window position if enabled."""
        if self.auto_refresh:
            self.refreshWindowPosition()

    def getWindowOffset(self) -> Tuple[int, int] | None:
        """
        Get current window offset (x, y).

        Returns:
            Tuple of (x, y) or None if window not detected
        """
        self._autoRefresh()
        return self.window_offset

    def getWindowSize(self) -> Tuple[int, int] | None:
        """
        Get current window size (width, height).

        Returns:
            Tuple of (width, height) or None if window not detected
        """
        self._autoRefresh()
        return self.window_size

    def getGameBounds(self) -> Tuple[int, int, int, int] | None:
        """
        Get game window bounds (x, y, width, height).

        Returns:
            Tuple of (x, y, width, height) or None if window not detected
        """
        self._autoRefresh()

        if self.window_offset and self.window_size:
            return (
                self.window_offset[0],
                self.window_offset[1],
                self.window_size[0],
                self.window_size[1]
            )
        return None

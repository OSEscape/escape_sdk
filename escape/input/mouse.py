"""Mouse control with human-like movement."""

import random
import time
from typing import Optional, Tuple

try:
    import pyautogui as pag
except ImportError:
    pag = None


class Mouse:
    """Mouse controller with human-like movement."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance

    def _init(self, speed: float = 1.0):
        """Actual initialization, runs once."""
        from escape.input.runelite import runelite

        if pag is None:
            raise ImportError("pyautogui is required. Install with: pip install pyautogui")

        # Configure pyautogui for instant movement
        pag.PAUSE = 0
        pag.FAILSAFE = False
        pag.MINIMUM_SLEEP = 0
        pag.MINIMUM_DURATION = 0

        self.runelite = runelite
        self.speed = speed

    @property
    def position(self) -> Tuple[int, int]:
        """Get current mouse position relative to game window."""
        screen_x, screen_y = pag.position()
        offset = self.runelite.getWindowOffset()
        return (screen_x - offset[0], screen_y - offset[1])

    def _validateCoordinates(self, x: int, y: int, safe: bool) -> None:
        """Validate that coordinates are within game window bounds."""
        if not safe:
            return  # Skip validation

        bounds = self.runelite.getGameBounds()
        if not bounds:
            raise ValueError("Could not get game window bounds")

        window_width = bounds[2]
        window_height = bounds[3]

        if x < 0 or y < 0 or x >= window_width or y >= window_height:
            raise ValueError(
                f"Coordinates ({x}, {y}) are outside game window bounds "
                f"(0, 0, {window_width}, {window_height}). "
                f"Use safe=False to allow out-of-bounds coordinates."
            )

    def _moveTo(self, x: int, y: int, safe: bool = True) -> None:
        """Core movement function - ONLY access point to pyautogui.moveTo()."""
        # Ensure window is ready
        self.runelite.refreshWindowPosition()
        # temp override for performance testing

        time.perf_counter()
        pag.moveTo(
            x + self.runelite.getWindowOffset()[0],
            y + self.runelite.getWindowOffset()[1],
            _pause=False,
        )
        time.sleep(0.001)  # slight delay to ensure move completes
        return
        # Validate coordinates
        self._validateCoordinates(x, y, safe)

        # Convert to absolute screen coordinates
        offset = self.runelite.getWindowOffset()
        if not offset:
            raise RuntimeError("Could not get window offset")

        abs_x = x + offset[0]
        abs_y = y + offset[1]

        # Get current position
        current_x, current_y = pag.position()

        # Calculate distance
        dx = abs_x - current_x
        dy = abs_y - current_y
        distance = (dx**2 + dy**2) ** 0.5

        if distance == 0:
            return  # Already at target

        # Base step size: ~20 pixels per step at speed=1.0
        base_step_size = 20.0 * self.speed

        # Calculate number of steps (20ms per step)
        num_steps = max(1, int(distance / base_step_size))

        # Move in steps
        for step in range(num_steps):
            # Calculate progress (0.0 to 1.0)
            progress = (step + 1) / num_steps

            # Add randomness to step size (±20% variation)
            step_randomness = random.uniform(0.8, 1.2)

            # Calculate intermediate position
            intermediate_x = current_x + int(dx * progress)
            intermediate_y = current_y + int(dy * progress)

            # Add slight random offset for human-like movement (±2 pixels)
            jitter_x = random.randint(-2, 2) if step < num_steps - 1 else 0
            jitter_y = random.randint(-2, 2) if step < num_steps - 1 else 0

            # Move to intermediate position
            pag.moveTo(
                intermediate_x + jitter_x, intermediate_y + jitter_y, duration=0, _pause=False
            )

            # Wait 20ms (with slight randomness)
            time.sleep(0.020 * step_randomness)

        # Final move to exact target (no jitter)
        pag.moveTo(abs_x, abs_y, duration=0, _pause=False)

    def _clickButton(self, button: str) -> None:
        """Core click function - ONLY access point to pyautogui.click()."""
        # Ensure window is ready (respects 10s cache)
        self.runelite.refreshWindowPosition()

        # Perform click
        pag.click(button=button, _pause=False, tween=None)

    def _hold(self, button: str) -> None:
        """Core hold function - ONLY access point to pyautogui.mouseDown()."""
        # Ensure window is ready (respects 10s cache)
        self.runelite.refreshWindowPosition()

        # Hold button down
        pag.mouseDown(button=button, _pause=False)

    def _release(self, button: str) -> None:
        """Core release function - ONLY access point to pyautogui.mouseUp()."""
        # Ensure window is ready (respects 10s cache)
        self.runelite.refreshWindowPosition()

        # Release button
        pag.mouseUp(button=button, _pause=False)

    def _scroll(self, clicks: int) -> None:
        """Core scroll function - ONLY access point to pyautogui.scroll()."""
        # Ensure window is ready (respects 10s cache)
        self.runelite.refreshWindowPosition()

        # Perform scroll
        pag.scroll(clicks, _pause=False)

    def click(self, button: str = "left") -> None:
        self._clickButton(button)

    def moveTo(self, x: int, y: int, safe: bool = True) -> None:
        """Move mouse to target position with human-like movement."""
        self._moveTo(x, y, safe=safe)

    def leftClick(self, x: int | None = None, y: int | None = None, safe: bool = True) -> None:
        """Perform left click at current position or move to position and click."""
        import time

        time.perf_counter()
        if x is not None and y is not None:
            self._moveTo(x, y, safe=safe)
        self._clickButton("left")
        time.perf_counter()

    def rightClick(self, x: int | None = None, y: int | None = None, safe: bool = True) -> None:
        """Perform right click at current position or move to position and click."""
        if x is not None and y is not None:
            self._moveTo(x, y, safe=safe)

        self._clickButton("right")

    def holdLeft(self, x: int | None = None, y: int | None = None, safe: bool = True) -> None:
        """Hold left mouse button at current position or move to position and hold."""
        if x is not None and y is not None:
            self._moveTo(x, y, safe=safe)

        self._hold("left")

    def holdRight(self, x: int | None = None, y: int | None = None, safe: bool = True) -> None:
        """Hold right mouse button at current position or move to position and hold."""
        if x is not None and y is not None:
            self._moveTo(x, y, safe=safe)

        self._hold("right")

    def releaseLeft(self) -> None:
        """Release left mouse button."""
        self._release("left")

    def releaseRight(self) -> None:
        """Release right mouse button."""
        self._release("right")

    def scroll(self, up: bool = True, count: int = 1) -> None:
        """Scroll the mouse wheel with human-like delays between scrolls."""
        direction = 1 if up else -1

        for i in range(count):
            self._scroll(direction)

            # Add human-like delay between scrolls (~25-50ms)
            if i < count - 1:
                time.sleep(random.uniform(0.025, 0.05))


# Module-level instance
mouse = Mouse()

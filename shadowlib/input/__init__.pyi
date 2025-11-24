"""Type stubs for input namespace."""

from shadowlib.input.mouse import Mouse
from shadowlib.input.runelite import RuneLite

class Input:
    """Namespace for input controls with lazy-loading."""

    runelite: RuneLite
    mouse: Mouse
    # keyboard: Keyboard  # Add when implemented
    def __init__(self, client) -> None: ...

__all__ = ["Input", "Mouse", "RuneLite"]

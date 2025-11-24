"""Type stubs for interactions namespace."""

from shadowlib.interactions.menu import Menu

class Interactions:
    """Namespace for interaction systems with lazy-loading."""

    menu: Menu
    # widgets: Widgets  # Add when implemented
    # hover: Hover  # Add when implemented
    def __init__(self, client) -> None: ...

__all__ = ["Interactions"]

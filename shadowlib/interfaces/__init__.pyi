"""Type stubs for interfaces namespace."""

from shadowlib.interfaces.bank import Bank

class Interfaces:
    """Namespace for overlay interfaces with lazy-loading."""

    bank: Bank
    # grand_exchange: GrandExchange  # Add when implemented
    # shop: Shop  # Add when implemented
    # dialogue: Dialogue  # Add when implemented
    def __init__(self, client) -> None: ...

__all__ = ["Interfaces"]

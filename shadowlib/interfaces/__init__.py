"""Overlay windows - bank, GE, shop, dialogue, etc."""


class Interfaces:
    """Namespace for overlay interfaces with lazy-loading."""

    _modules = {
        "bank": "Bank",
        # Add more as they're created:
        # 'grand_exchange': 'GrandExchange',
        # 'shop': 'Shop',
        # 'dialogue': 'Dialogue',
    }

    def __init__(self, client):
        """
        Initialize interfaces namespace.

        Args:
            client: The Client instance
        """
        self._client = client
        self._cache = {}

    def __getattr__(self, name):
        """Lazy-load interface modules."""
        if name.startswith("_"):
            raise AttributeError(name)

        if name in self._cache:
            return self._cache[name]

        if name not in self._modules:
            raise AttributeError(f"Interfaces has no module '{name}'")

        class_name = self._modules[name]
        module_path = f"shadowlib.interfaces.{name}"
        module = __import__(module_path, fromlist=[class_name])
        cls = getattr(module, class_name)

        instance = cls(client=self._client)
        self._cache[name] = instance
        return instance


__all__ = ["Interfaces"]

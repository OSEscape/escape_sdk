"""
Navigation module.
"""

# Legacy imports for backwards compatibility
from .pathfinder import Pathfinder


class Navigation:
    """Namespace for navigation systems with lazy-loading."""

    _modules = {
        "pathfinder": "Pathfinder",
        # Add more as they're created:
        # 'walker': 'Walker',
        # 'teleports': 'Teleports',
    }

    def __init__(self, client):
        """
        Initialize navigation namespace.

        Args:
            client: The Client instance
        """
        self._client = client
        self._cache = {}

    def __getattr__(self, name):
        """Lazy-load navigation modules."""
        if name.startswith("_"):
            raise AttributeError(name)

        if name in self._cache:
            return self._cache[name]

        if name not in self._modules:
            raise AttributeError(f"Navigation has no module '{name}'")

        class_name = self._modules[name]
        module_path = f"shadowlib.navigation.{name}"
        module = __import__(module_path, fromlist=[class_name])
        cls = getattr(module, class_name)

        instance = cls(client=self._client)
        self._cache[name] = instance
        return instance


__all__ = ["Navigation", "Pathfinder"]

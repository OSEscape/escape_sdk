"""Game viewport entities - NPCs, objects, players, items visible in 3D world."""


class World:
    """Namespace for 3D world entities with lazy-loading."""

    _modules = {
        "ground_items": "GroundItems",
        # Add more as they're created:
        # 'npcs': 'NPCs',
        # 'objects': 'Objects',
        # 'players': 'Players',
    }

    def __init__(self, client):
        """
        Initialize world namespace.

        Args:
            client: The Client instance
        """
        self._client = client
        self._cache = {}

    def __getattr__(self, name):
        """Lazy-load world modules."""
        if name.startswith("_"):
            raise AttributeError(name)

        if name in self._cache:
            return self._cache[name]

        if name not in self._modules:
            raise AttributeError(f"World has no module '{name}'")

        class_name = self._modules[name]
        module_path = f"shadowlib.world.{name}"
        module = __import__(module_path, fromlist=[class_name])
        cls = getattr(module, class_name)

        instance = cls(client=self._client)
        self._cache[name] = instance
        return instance


__all__ = ["World"]

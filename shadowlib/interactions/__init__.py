"""Interaction systems - menu, clicking, hovering, widgets."""


class Interactions:
    """Namespace for interaction systems with lazy-loading."""

    _modules = {
        'menu': 'Menu',
        # Add more as they're created:
        # 'widgets': 'Widgets',
        # 'hover': 'Hover',
    }

    def __init__(self, client):
        """
        Initialize interactions namespace.

        Args:
            client: The Client instance
        """
        self._client = client
        self._cache = {}

    def __getattr__(self, name):
        """Lazy-load interaction modules."""
        if name.startswith('_'):
            raise AttributeError(name)

        if name in self._cache:
            return self._cache[name]

        if name not in self._modules:
            raise AttributeError(f"Interactions has no module '{name}'")

        class_name = self._modules[name]
        module_path = f'shadowlib.interactions.{name}'
        module = __import__(module_path, fromlist=[class_name])
        cls = getattr(module, class_name)

        instance = cls(client=self._client)
        self._cache[name] = instance
        return instance


__all__ = ["Interactions"]

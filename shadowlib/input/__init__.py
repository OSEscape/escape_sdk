"""OS-level input handling - mouse and keyboard."""

# Legacy imports for backwards compatibility
from shadowlib.input.mouse import Mouse
from shadowlib.input.runelite import RuneLite


class Input:
    """Namespace for input controls with lazy-loading."""

    _modules = {
        'runelite': ('RuneLite', lambda cls, ns: cls()),  # No client param
        'mouse': ('Mouse', lambda cls, ns: cls(runelite=ns._getRuneLite())),
        # 'keyboard': ('Keyboard', lambda cls, ns: cls(runelite=ns._getRuneLite())),
    }

    def __init__(self, client):
        """
        Initialize input namespace.

        Args:
            client: The Client instance
        """
        self._client = client
        self._cache = {}
        self._runelite_instance = None

    def _getRuneLite(self):
        """Get or create RuneLite instance."""
        if self._runelite_instance is None:
            self._runelite_instance = self.runelite
        return self._runelite_instance

    def __getattr__(self, name):
        """Lazy-load input modules."""
        if name.startswith('_'):
            raise AttributeError(name)

        if name in self._cache:
            return self._cache[name]

        if name not in self._modules:
            raise AttributeError(f"Input has no module '{name}'")

        entry = self._modules[name]
        if isinstance(entry, tuple):
            class_name, init_fn = entry
        else:
            class_name, init_fn = entry, None

        module_path = f'shadowlib.input.{name}'
        module = __import__(module_path, fromlist=[class_name])
        cls = getattr(module, class_name)

        if init_fn is None:
            instance = cls(client=self._client)
        else:
            instance = init_fn(cls, self)

        self._cache[name] = instance
        return instance


__all__ = ["Input", "Mouse", "RuneLite"]

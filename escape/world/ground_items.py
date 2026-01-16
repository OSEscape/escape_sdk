"""
OSRS ground item handling using event cache.
"""

from ..types.ground_item import GroundItem
from ..types.ground_item_list import GroundItemList
from ..types.packed_position import PackedPosition


class GroundItems:
    """Ground items accessor from event cache."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance

    def _init(self):
        """Actual initialization, runs once."""
        self._cached_list: GroundItemList = GroundItemList([])
        self._cached_tick: int = -1

    def getAllItems(self) -> GroundItemList:
        """Get all ground items from cache."""
        from escape.client import client

        current_tick = client.cache.tick

        # Return cached if same tick
        if self._cached_tick == current_tick and self._cached_list.count() > 0:
            return self._cached_list

        # Refresh cache
        ground_items_dict = client.cache.getGroundItems()
        result = []

        for packed_coord, items_list in ground_items_dict.items():
            position = PackedPosition.fromPacked(packed_coord)
            for item_data in items_list:
                result.append(GroundItem(data=item_data, position=position, client=client))

        self._cached_list = GroundItemList(result)
        self._cached_tick = current_tick

        return self._cached_list


# Module-level instance
groundItems = GroundItems()

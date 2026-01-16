"""
Menu module - handles right-click context menu interactions.
"""

import math
import time
from copy import deepcopy
from typing import List, Tuple

from escape.client import client
from escape.types import Box
from escape.utilities import timing
from escape.utilities.text import stripColorTags


class Menu:
    """Right-click context menu operations."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance

    def _init(self):
        """Actual initialization, runs once."""
        pass  # No initialization needed

    def isOpen(self) -> bool:
        """Check if the right-click context menu is currently open."""
        return client.cache.getMenuOpenState().get("menu_open", False)

    def _getOptions(self, strip_colors: bool = True) -> Tuple[List[str], List[str]]:
        data = deepcopy(client.cache.getMenuOptions())
        types = data["types"]
        options = data["options"]
        targets = data["targets"]

        if not types or not options or not targets:
            return [], []

        # Combine types, options, and targets into formatted strings

        formatted_options = [
            f"{option} {target}".strip() for option, target in zip(options, targets)
        ]
        if strip_colors:
            formatted_options = [stripColorTags(opt) for opt in formatted_options]

        # reverse because they're stored backwards (last item is first option)
        formatted_options.reverse()
        types.reverse()

        return formatted_options, types

    def _getMenuInfo(self) -> dict:
        return client.cache.getMenuOpenState()

    def waitMenuClickEvent(self, max_age: float = 0.2, timeout: float = 0.5) -> bool:
        """Wait for a menu option click event to be registered."""
        current_state = client.cache.getMenuClickedState()
        timestamp = current_state.get("_timestamp", 0)

        if (time.time() - timestamp) < max_age and not client.cache.isMenuOptionClickedConsumed():
            return True

        def checkEvent(ts) -> bool:
            state = client.cache.getMenuClickedState()
            event_time = state.get("_timestamp", 0)
            return (event_time - ts) > 0

        return timing.waitUntil(lambda: checkEvent(timestamp), timeout=timeout, poll_interval=0.001)

    def waitHasType(self, option_type: str, timeout: float = 0.5) -> bool:
        """Wait until menu contains an option of the specified type."""

        def checkType() -> bool:
            return self.hasType(option_type)

        return timing.waitUntil(checkType, timeout=timeout, poll_interval=0.001)

    def waitHasOption(self, option: str, timeout: float = 0.5) -> bool:
        """Wait until menu contains the specified option text."""

        def checkOption() -> bool:
            return self.hasOption(option)

        return timing.waitUntil(checkOption, timeout=timeout, poll_interval=0.001)

    def open(self, timeout: float = 0.5) -> bool:
        """Open the context menu by right-clicking at current mouse position."""
        if self.isOpen():
            return True  # Already open

        # Right-click at current position
        client.input.mouse.rightClick()

        # Wait for menu to open
        return timing.waitUntil(self.isOpen, timeout=timeout, poll_interval=0.001)

    def close(self, use_cancel: bool = True, timeout: float = 1.0) -> bool:
        """Close the context menu by clicking Cancel or moving mouse away."""
        import random

        # Check if menu is open
        if not self.isOpen():
            return True  # Already closed

        state = self._getMenuInfo()
        # Get menu state from cache
        scrollable = state.get("scrollable", False)
        menu_x = state.get("menuX", 0)
        menu_y = state.get("menuY", 0)
        menu_width = state.get("width", 0)
        menu_height = state.get("height", 0)

        # For scrollable menus, always move mouse away
        if scrollable:
            use_cancel = False

        if use_cancel and not scrollable:
            # Click Cancel option
            options = self.getOptions()
            cancel_index = None

            for i, option in enumerate(options):
                if "cancel" in option.lower():
                    cancel_index = i
                    break

            if cancel_index is not None:
                box = self.getOptionBox(cancel_index)
                if box:
                    box.click()
            else:
                # Cancel not found, fall back to mouse move
                use_cancel = False

        if not use_cancel:
            # Move mouse at least 30 pixels away from menu box
            menu_x1 = menu_x
            menu_y1 = menu_y
            menu_x2 = menu_x + menu_width
            menu_y2 = menu_y + menu_height

            # Pick a random direction and move 30-50 pixels away
            distance = random.randint(30, 50)

            # Randomly choose a direction: up, down, left, or right
            direction = random.choice(["up", "down", "left", "right"])

            if direction == "up":
                target_x = random.randint(menu_x1, menu_x2)
                target_y = menu_y1 - distance
            elif direction == "down":
                target_x = random.randint(menu_x1, menu_x2)
                target_y = menu_y2 + distance
            elif direction == "left":
                target_x = menu_x1 - distance
                target_y = random.randint(menu_y1, menu_y2)
            else:  # right
                target_x = menu_x2 + distance
                target_y = random.randint(menu_y1, menu_y2)

            # Move mouse to target position
            client.input.mouse.moveTo(target_x, target_y, safe=False)

            return timing.waitUntil(lambda: not self.isOpen(), timeout=timeout, poll_interval=0.001)

    def getOptions(self, strip_colors: bool = True) -> List[str]:
        """Get all menu options as formatted strings in display order."""
        menu_options, _ = self._getOptions(strip_colors=strip_colors)

        return menu_options

    def getTypes(self) -> List[str]:
        """Get all menu option types in display order."""
        _, menu_types = self._getOptions(strip_colors=True)

        return menu_types

    def getLeftClickOption(self, strip_colors: bool = True) -> str | None:
        """Get the default menu option (accessible with left-click)."""
        options = self.getOptions(strip_colors=strip_colors)
        if not options:
            return None

        return options[0]

    def getLeftClickType(self) -> str | None:
        """Get the action type of the default menu option."""
        types = self.getTypes()
        if not types:
            return None

        return types[0]

    def hasOption(self, option_text: str, strip_colors: bool = True) -> bool:
        """Check if a menu option exists (partial matching, case-insensitive)."""
        options = self.getOptions(strip_colors=strip_colors)
        option_text_lower = option_text.lower()

        return any(option_text_lower in option.lower() for option in options)

    def hasType(self, option_type: str) -> bool:
        """Check if a menu option of a specific type exists."""
        types = self.getTypes()
        option_type_lower = option_type.lower()
        return any(option_type_lower in t.lower() for t in types)

    def getOptionBox(self, option_index: int) -> Box | None:
        """Get the clickable box for a specific menu option by index."""
        if not self.isOpen():
            return None

        state = self._getMenuInfo()

        # Get menu position and dimensions
        menu_x = state.get("menuX", 0)
        menu_y = state.get("menuY", 0)
        menu_width = state.get("width", 0)

        # First option starts at offset (2, 19) from menu position
        option_x1 = menu_x + 2
        option_y1 = menu_y + 19 + (option_index * 15)

        # Each option is (menuWidth - 4) wide and spans 15 pixels
        # Using x2 = x1 + width - 1 to avoid overlap (e.g., 100-114 = 15 pixels)
        option_x2 = option_x1 + (menu_width - 4) - 1
        option_y2 = option_y1 + 14  # 15 pixels total: y1 to y1+14 inclusive

        return Box(option_x1, option_y1, option_x2, option_y2)

    def hoverOption(self, option_text: str) -> bool:
        """Hover over a menu option by matching text. Opens menu if needed."""
        # Ensure menu is open
        if not self.open():
            return False

        options = self.getOptions()
        option_text_lower = option_text.lower()

        for i, option in enumerate(options):
            if option_text_lower in option.lower():
                box = self.getOptionBox(i)
                if box:
                    box.hover()
                    return True

        return False

    def hoverOptionIndex(self, option_index: int) -> bool:
        """Hover over a menu option by its index. Opens menu if needed."""
        # Ensure menu is open
        if not self.open():
            return False

        box = self.getOptionBox(option_index)
        if box:
            box.hover()
            return True
        return False

    def lastOptionClicked(self) -> str:
        latest_click = client.cache.getMenuClickedState()
        option = latest_click.get("menu_option", "")
        target = latest_click.get("menu_target", "")
        full_option = f"{option} {target}".strip()
        return stripColorTags(full_option)

    def waitOptionClicked(
        self, option_text: str, max_age: float = 0.2, timeout: float = 0.5
    ) -> bool:
        if not self.waitMenuClickEvent(max_age=max_age, timeout=timeout):
            return False

        client.cache.consumeMenuClickedState()

        return option_text.lower() in self.lastOptionClicked().lower()

    def waitMenuClosed(self, timeout: float = 0.5) -> bool:
        """Wait until the menu is closed."""
        return timing.waitUntil(lambda: not self.isOpen(), timeout=timeout, poll_interval=0.001)

    def clickOption(self, option_text: str) -> bool:
        """Click a menu option. Left-clicks if default, otherwise opens menu."""
        if self.isOpen():
            self.hoverOption(option_text)
            client.input.mouse.leftClick()
            return self.waitOptionClicked(option_text) and self.waitMenuClosed()

        left_click_option = self.getLeftClickOption()
        if left_click_option is None:
            return False

        if option_text.lower() in left_click_option.lower():
            # It's the default! Just left-click at current position
            client.input.mouse.leftClick()
            return self.waitOptionClicked(option_text)

        if not self.hasOption(option_text):
            return False

        self.open()
        self.hoverOption(option_text)
        client.input.mouse.leftClick()
        return self.waitOptionClicked(option_text) and self.waitMenuClosed()

    def clickOptionIndex(self, option_index: int) -> bool:
        """Click a menu option by its index. Opens menu if needed."""
        # Ensure menu is open
        if not self.open():
            return False

        box = self.getOptionBox(option_index)
        if box:
            box.click()
            return True
        return False

    def clickOptionType(self, option_type: str) -> bool:
        """Click a menu option by its type. Opens menu if needed."""
        options, types = self._getOptions(strip_colors=True)
        for i, t in enumerate(types):
            if option_type.lower() in t.lower():
                return self.clickOption(options[i])
        return False


# Module-level instance
menu = Menu()

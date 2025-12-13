import shadowlib.utilities.timing as timing
from shadowlib.client import client
from shadowlib.types.box import Box
from shadowlib.types.widget import Widget, WidgetFields


class GeneralInterface:
    """
    Interface-type class for the interface that looks like a scroll.

    Supports optional scrollbox for interfaces with scrollable content.
    When scrollbox is set, the interact method will scroll down to find
    options that are not immediately visible.
    """

    def __init__(
        self,
        group: int,
        button_ids: list[int],
        get_children: bool = True,
        wrong_text: str = "5f5f5d",
        menu_text: str | None = None,
        scrollbox: int | None = None,
        max_scroll: int = 10,
    ):
        """
        Initialize a GeneralInterface.

        Args:
            group: The interface group ID
            button_ids: List of widget IDs for the interface buttons
            get_children: If True, get children of widgets. If False, get widgets directly.
            wrong_text: Text color to filter out (default grayed out text)
            menu_text: Optional menu option text to click
            scrollbox: Optional widget ID for the scrollable area
            max_scroll: Maximum scroll attempts when searching (default 10)
        """
        self.group = group
        self.buttons = []
        self.get_children = get_children
        self.wrong_text = wrong_text
        self.menu_text = menu_text
        self.max_scroll = max_scroll

        # Setup scrollbox widget if provided
        if scrollbox:
            self.scrollbox_widget = Widget(scrollbox)
            self.scrollbox_widget.enable(WidgetFields.getBounds)
        else:
            self.scrollbox_widget = None

        for button_id in button_ids:
            button = Widget(button_id)
            button.enable(WidgetFields.getBounds)
            button.enable(WidgetFields.getText)
            self.buttons.append(button)

    def getWidgetInfo(self) -> dict:
        if self.get_children:
            return Widget.getBatchChildren(self.buttons)
        else:
            return Widget.getBatch(self.buttons)

    def isOpen(self) -> bool:
        return self.group in client.interfaces.getOpenInterfaces()

    def isRightOption(self, widget_info: dict, option_text: str = "") -> bool:
        widget_text = widget_info.get("text", "")
        if option_text:
            return option_text in widget_text and self.wrong_text not in widget_text
        return widget_text and self.wrong_text not in widget_text

    def _getScrollboxBounds(self) -> Box | None:
        """
        Get the bounds of the scrollbox as a Box.

        Returns:
            Box representing the scrollbox area, or None if unavailable
        """
        if not self.scrollbox_widget:
            return None
        info = self.scrollbox_widget.get()
        bounds = info.get("bounds", (0, 0, 0, 0))
        if bounds[2] > 0 and bounds[3] > 0:
            return Box.fromRect(*bounds)
        return None

    def _isVisibleInScrollbox(self, widget_bounds: tuple, scrollbox: Box) -> bool:
        """
        Check if widget bounds are visible within the scrollbox area.

        Args:
            widget_bounds: Tuple of (x, y, width, height)
            scrollbox: Box representing the scrollable area

        Returns:
            True if widget center is within the scrollbox
        """
        x, y, w, h = widget_bounds
        if w <= 0 or h <= 0:
            return False
        widget_box = Box.fromRect(x, y, w, h)
        center = widget_box.center()
        return scrollbox.contains(center)

    def _scrollDown(self) -> None:
        """Scroll down once in the scrollbox area."""
        scrollbox = self._getScrollboxBounds()
        if scrollbox:
            scrollbox.hover()
            client.input.mouse.scroll(up=False, count=1)
            timing.sleep(0.1)

    def interact(self, option_text: str = "", index: int = -1) -> bool:
        """
        Interact with an option in the interface.

        If scrollbox is set and the option is not visible, will scroll down
        and retry until the option is found or max_scroll attempts reached.

        Args:
            option_text: Text to search for in widget options
            index: Specific index to interact with (takes priority over option_text)

        Returns:
            True if interaction succeeded, False otherwise
        """
        if not self.isOpen():
            return False

        scroll_attempts = 0

        while scroll_attempts <= self.max_scroll:
            info = self.getWidgetInfo()
            scrollbox = self._getScrollboxBounds() if self.scrollbox_widget else None

            # Handle index-based interaction
            if index >= 0 and index < len(info):
                w = info[index]
                bounds = w.get("bounds", (0, 0, 0, 0))

                # Check if visible when scrollbox is set
                if scrollbox and not self._isVisibleInScrollbox(bounds, scrollbox):
                    if scroll_attempts < self.max_scroll:
                        self._scrollDown()
                        scroll_attempts += 1
                        continue
                    else:
                        print(f"Max scroll attempts ({self.max_scroll}) reached")
                        return False

                b = Box.fromRect(*bounds)
                if self.isRightOption(w, option_text):
                    return b.clickOption(self.menu_text)
                else:
                    return False

            # Handle text-based interaction
            elif option_text:
                for widget_info in info:
                    if self.isRightOption(widget_info, option_text):
                        bounds = widget_info.get("bounds", (0, 0, 0, 0))

                        # Check if visible when scrollbox is set
                        if scrollbox and not self._isVisibleInScrollbox(bounds, scrollbox):
                            continue  # Try next widget

                        b = Box.fromRect(*bounds)
                        return (
                            b.clickOption(self.menu_text)
                            if self.menu_text
                            else b.clickOption(option_text)
                        )

                # Option not found - try scrolling if scrollbox is set
                if scrollbox and scroll_attempts < self.max_scroll:
                    self._scrollDown()
                    scroll_attempts += 1
                    continue
                else:
                    print(f"Option '{option_text}' not found in interface.")
                    return False
            else:
                print("No valid option_text or index provided for interaction.")
                return False

        return False

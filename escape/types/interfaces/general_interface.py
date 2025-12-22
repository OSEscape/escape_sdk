import escape.utilities.timing as timing
from escape.client import client
from escape.types.box import Box
from escape.types.widget import Widget, WidgetFields


class GeneralInterface:
    """Interface class with optional scrollbox support."""

    def __init__(
        self,
        group: int,
        button_ids: list[int],
        get_children: bool = True,
        wrong_text: str = "5f5f5d",
        menu_text: str | None = None,
        scrollbox: int | None = None,
        max_scroll: int = 10,
        use_actions: bool = False,
    ):
        self.group = group
        self.get_children = get_children
        self.wrong_text = wrong_text
        self.menu_text = menu_text
        self.scrollbox = scrollbox
        self.max_scroll = max_scroll
        self.use_actions = use_actions
        self.buttons: list[Widget] = []

        for id in button_ids:
            w = (
                Widget(id)
                .enable(WidgetFields.getBounds)
                .enable(
                    WidgetFields.getActions if use_actions else WidgetFields.getText,
                )
            )
            self.buttons.append(w)

    def getWidgetInfo(self) -> list:
        return (
            Widget.getBatchChildren(self.buttons)
            if self.get_children
            else Widget.getBatch(self.buttons)
        )

    def isOpen(self) -> bool:
        return self.group in client.interfaces.getOpenInterfaces()

    def isRightOption(self, w: dict, text: str = "") -> bool:
        if self.use_actions:
            actions = w.get("actions", []) or []
            if not text:
                return any(actions)
            return any(text in a for a in actions if a)
        t = w.get("text", "")
        return (text in t if text else bool(t)) and self.wrong_text not in t

    def _getScrollbox(self) -> Box | None:
        if not self.scrollbox:
            return None
        b = Widget(self.scrollbox).enable(WidgetFields.getBounds).get().get("bounds", [0, 0, 0, 0])
        return Box.fromRect(*b) if b[2] > 0 and b[3] > 0 else None

    def _scroll(self, sb: Box, up: bool = False) -> None:
        sb.hover()
        client.input.mouse.scroll(up=up, count=1)
        timing.sleep(0.1)

    def _findWidget(self, text: str, idx: int) -> dict | None:
        """Find widget by index or text."""
        info = self.getWidgetInfo()
        if 0 <= idx < len(info):
            w = info[idx]
            return w if not text or self.isRightOption(w, text) else None
        for w in info:
            if self.isRightOption(w, text):
                return w
        return None

    def _makeVisible(self, text: str, idx: int, sb: Box | None) -> Box | None:
        """Find option and scroll until visible. Returns clickable Box or None."""
        w = self._findWidget(text, idx)
        if not w:
            return None

        for _ in range(self.max_scroll + 1):
            b = w.get("bounds", [0, 0, 0, 0])
            if b[2] > 0 and b[3] > 0:
                box = Box.fromRect(*b)
                if not sb or sb.contains(box):
                    return box
                self._scroll(sb, up=box.y1 < sb.y1)
            w = self._findWidget(text, idx)
        return None

    def interact(self, option_text: str = "", index: int = -1) -> bool:
        if not self.isOpen():
            return False
        box = self._makeVisible(option_text, index, self._getScrollbox())
        return box.clickOption(self.menu_text or option_text) if box else False

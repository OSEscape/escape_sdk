from shadowlib.client import client
from shadowlib.types.box import Box
from shadowlib.types.widget import Widget, WidgetFields


class GeneralInterface:
    """
    Interface-type class for the interface that looks like a scroll.
    """

    def __init__(
        self,
        group: int,
        button_ids: list[int],
        get_children: bool = True,
        wrong_text: str = "5f5f5d",
        menu_text: str | None = None,
    ):
        self.group = group
        self.buttons = []
        self.get_children = get_children
        self.wrong_text = wrong_text

        if menu_text:
            self.menu_text = menu_text
        else:
            self.menu_text = None

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

    def interact(self, option_text: str = "", index: int = -1) -> bool:
        if not self.isOpen():
            return False

        info = self.getWidgetInfo()

        if index >= 0 and index < len(info):
            w = info[index]
            b = Box.fromRect(*w.get("bounds", (0, 0, 0, 0)))
            if self.isRightOption(w, option_text):
                return b.clickOption(self.menu_text)
            else:
                return False
        elif option_text:
            for widget_info in info:
                if self.isRightOption(widget_info, option_text):
                    b = Box.fromRect(*widget_info.get("bounds", (0, 0, 0, 0)))
                    return (
                        b.clickOption(self.menu_text)
                        if self.menu_text
                        else b.clickOption(option_text)
                    )
                else:
                    continue
            print(f"Option '{option_text}' not found in interface.")
        else:
            print("No valid option_text or index provided for interaction.")
        return False

"""Overlay windows - bank, GE, shop, dialogue, etc."""

from escape_sdk.client import client
from escape_sdk.interfaces.bank import Bank, bank
from escape_sdk.interfaces.fairy_ring import FairyRingInterface, fairy_ring
from escape_sdk.types.interfaces.general_interface import GeneralInterface
from escape_sdk.types.widget import Widget, WidgetFields

# Lazy-loaded reverse lookup: group_id -> name
_interface_id_to_name: dict[int, str] | None = None


def _getInterfaceIdToNameMap() -> dict[int, str]:
    """
    Build and cache a reverse lookup map from interface group ID to name.

    Lazily loads the InterfaceID class and builds the map once.

    Returns:
        Dict mapping group ID (int) to interface name (str)
    """
    global _interface_id_to_name

    if _interface_id_to_name is not None:
        return _interface_id_to_name

    _interface_id_to_name = {}

    try:
        from escape_sdk.generated.constants.interface_id import InterfaceID

        # Iterate over class attributes that are integers (group IDs)
        for name in dir(InterfaceID):
            if name.startswith("_") and not name.startswith("__"):
                # Handle names like _100GUIDE_EGGS_OVERLAY (start with underscore + digit)
                value = getattr(InterfaceID, name)
                if isinstance(value, int):
                    # Remove leading underscore for display
                    _interface_id_to_name[value] = name[1:]
            elif not name.startswith("_") and name.isupper():
                value = getattr(InterfaceID, name)
                if isinstance(value, int):
                    _interface_id_to_name[value] = name
    except ImportError:
        pass

    return _interface_id_to_name


def getInterfaceName(group_id: int) -> str | None:
    """
    Get the interface name for a group ID.

    Args:
        group_id: The interface group ID

    Returns:
        Interface name string or None if not found

    Example:
        >>> getInterfaceName(12)
        'BANKMAIN'
    """
    return _getInterfaceIdToNameMap().get(group_id)


class ScrollInterface(GeneralInterface):
    """
    Interface-type class for the interface that looks like a scroll.
    """

    def __init__(self):
        super().__init__(
            client.InterfaceID.MENU,
            [client.InterfaceID.Menu.LJ_LAYER1],
            get_children=False,
            menu_text="Continue",
            scrollbox=client.InterfaceID.Menu.LJ_LAYER1,
        )


class GliderInterface(GeneralInterface):
    """
    Interface-type class for the glider interface.
    """

    def __init__(self):
        super().__init__(
            client.InterfaceID.GLIDERMAP,
            [
                client.InterfaceID.Glidermap.GRANDTREE_BUTTON,
                client.InterfaceID.Glidermap.WHITEWOLFMOUNTAIN_BUTTON,
                client.InterfaceID.Glidermap.VARROCK_BUTTON,
                client.InterfaceID.Glidermap.ALKHARID_BUTTON,
                client.InterfaceID.Glidermap.KARAMJA_BUTTON,
                client.InterfaceID.Glidermap.OGREAREA_BUTTON,
                client.InterfaceID.Glidermap.APEATOLL_BUTTON,
            ],
            get_children=False,
        )

        self.names = [
            "Ta Quir Priw",
            "Sindarpos",
            "Lemanto Andra",
            "Kar-Hewo",
            "Gandius",
            "Lemantolly Undri",
            "Ookookolly Undri",
        ]

    def getWidgetInfo(self) -> dict:
        res = Widget.getBatch(self.buttons)

        for i in range(len(res)):
            res[i]["text"] = self.names[i]
        return res

    def isRightOption(self, widget_info, option_text=""):
        b = widget_info.get("bounds", "")
        text = widget_info.get("text", "")
        if option_text:
            return option_text in text and b[0] >= 0


class Interfaces:
    """
    Namespace for overlay interfaces - returns singleton instances.

    Example:
        from escape_sdk.client import client

        client.interfaces.bank.depositAll()
        # Or directly:
        from escape_sdk.interfaces.bank import bank
        bank.depositAll()
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance

    def _init(self):
        self.spirit_tree = ScrollInterface()
        self.mushtree = GeneralInterface(
            client.InterfaceID.FOSSIL_MUSHTREES,
            [
                client.InterfaceID.FossilMushtrees.TREE1,
                client.InterfaceID.FossilMushtrees.TREE2,
                client.InterfaceID.FossilMushtrees.TREE3,
                client.InterfaceID.FossilMushtrees.TREE4,
            ],
            get_children=False,
            wrong_text="Not yet",
            menu_text="Continue",
        )
        self.zeah_minecart = ScrollInterface()
        self.jewellery_box = GeneralInterface(
            client.InterfaceID.POH_JEWELLERY_BOX,
            [
                client.InterfaceID.PohJewelleryBox.DUELING,
                client.InterfaceID.PohJewelleryBox.GAMING,
                client.InterfaceID.PohJewelleryBox.COMBAT,
                client.InterfaceID.PohJewelleryBox.SKILLS,
                client.InterfaceID.PohJewelleryBox.WEALTH,
                client.InterfaceID.PohJewelleryBox.GLORY,
            ],
            get_children=True,
            wrong_text="</str>",
        )
        self.gnome_glider = GliderInterface()
        self.charter_ship = GeneralInterface(
            client.InterfaceID.CHARTERING_MENU_SIDE,
            [client.InterfaceID.CharteringMenuSide.LIST_CONTENT],
            get_children=True,
            scrollbox=client.InterfaceID.CharteringMenuSide.LIST_CONTENT,
        )
        self.quetzal = GeneralInterface(
            client.InterfaceID.QUETZAL_MENU,
            [client.InterfaceID.QuetzalMenu.ICONS],
            get_children=True,
            use_actions=True,
        )

    @property
    def bank(self) -> Bank:
        """Get bank interface singleton."""
        return bank

    @property
    def fairy_ring(self) -> "FairyRingInterface":
        """Get fairy ring interface singleton."""
        return fairy_ring

    def getOpenInterfaces(self) -> list[int]:
        """
        Get a list of currently open interface IDs.

        Returns:
            List of open interface IDs

        Example:
            >>> from escape_sdk.client import client
            >>> open_interfaces = client.interfaces.getOpenInterfaces()
            >>> print(open_interfaces)  # e.g., [12, 15, 162]
        """
        return list(client.cache.getOpenWidgets())

    def getOpenInterfaceNames(self) -> list[str]:
        """
        Get a list of currently open interface names.

        Returns:
            List of open interface names (unknown IDs are formatted as "UNKNOWN_123")

        Example:
            >>> from escape_sdk.client import client
            >>> open_interfaces = client.interfaces.getOpenInterfaceNames()
            >>> print(open_interfaces)  # e.g., ['BANKMAIN', 'BANKSIDE', 'TOPLEVEL']
        """
        names = []
        for group_id in self.getOpenInterfaces():
            name = getInterfaceName(group_id)
            if name:
                names.append(name)
            else:
                names.append(f"UNKNOWN_{group_id}")
        return names


# Module-level singleton instance
interfaces = Interfaces()


__all__ = ["Interfaces", "interfaces", "Bank", "bank", "getInterfaceName"]

import typing
from typing import Literal

import escape.utilities.timing as timing
from escape.globals import getClient

WidgetField = Literal[
    "getActions",
    "getAnimationId",
    "getBorderType",
    "getBounds",
    "getCanvasLocation",
    "getClickMask",
    "getContentType",
    "getDragDeadTime",
    "getDragDeadZone",
    "getDragParent",
    "getFont",
    "getFontId",
    "getHeight",
    "getHeightMode",
    "getId",
    "getIndex",
    "getItemId",
    "getItemQuantity",
    "getItemQuantityMode",
    "getLineHeight",
    "getModelId",
    "getModelType",
    "getModelZoom",
    "getName",
    "getNoClickThrough",
    "getNoScrollThrough",
    "getOnInvTransmitListener",
    "getOnKeyListener",
    "getOnLoadListener",
    "getOnOpListener",
    "getOnVarTransmitListener",
    "getOpacity",
    "getOriginalHeight",
    "getOriginalWidth",
    "getOriginalX",
    "getOriginalY",
    "getParent",
    "getParentId",
    "getRelativeX",
    "getRelativeY",
    "getRotationX",
    "getRotationY",
    "getRotationZ",
    "getScrollHeight",
    "getScrollWidth",
    "getScrollX",
    "getScrollY",
    "getSpriteId",
    "getSpriteTiling",
    "getStaticChildren",
    "getTargetPriority",
    "getTargetVerb",
    "getText",
    "getTextColor",
    "getTextShadowed",
    "getType",
    "getVarTransmitTrigger",
    "getWidth",
    "getWidthMode",
    "getXPositionMode",
    "getXTextAlignment",
    "getYPositionMode",
    "getYTextAlignment",
    "isHidden",
]


class _WidgetFields:
    """Provides autocomplete for widget field names."""

    getActions: WidgetField = "getActions"
    getAnimationId: WidgetField = "getAnimationId"
    getBorderType: WidgetField = "getBorderType"
    getBounds: WidgetField = "getBounds"
    getCanvasLocation: WidgetField = "getCanvasLocation"
    getClickMask: WidgetField = "getClickMask"
    getContentType: WidgetField = "getContentType"
    getDragDeadTime: WidgetField = "getDragDeadTime"
    getDragDeadZone: WidgetField = "getDragDeadZone"
    getDragParent: WidgetField = "getDragParent"
    getFont: WidgetField = "getFont"
    getFontId: WidgetField = "getFontId"
    getHeight: WidgetField = "getHeight"
    getHeightMode: WidgetField = "getHeightMode"
    getId: WidgetField = "getId"
    getIndex: WidgetField = "getIndex"
    getItemId: WidgetField = "getItemId"
    getItemQuantity: WidgetField = "getItemQuantity"
    getItemQuantityMode: WidgetField = "getItemQuantityMode"
    getLineHeight: WidgetField = "getLineHeight"
    getModelId: WidgetField = "getModelId"
    getModelType: WidgetField = "getModelType"
    getModelZoom: WidgetField = "getModelZoom"
    getName: WidgetField = "getName"
    getNoClickThrough: WidgetField = "getNoClickThrough"
    getNoScrollThrough: WidgetField = "getNoScrollThrough"
    getOnInvTransmitListener: WidgetField = "getOnInvTransmitListener"
    getOnKeyListener: WidgetField = "getOnKeyListener"
    getOnLoadListener: WidgetField = "getOnLoadListener"
    getOnOpListener: WidgetField = "getOnOpListener"
    getOnVarTransmitListener: WidgetField = "getOnVarTransmitListener"
    getOpacity: WidgetField = "getOpacity"
    getOriginalHeight: WidgetField = "getOriginalHeight"
    getOriginalWidth: WidgetField = "getOriginalWidth"
    getOriginalX: WidgetField = "getOriginalX"
    getOriginalY: WidgetField = "getOriginalY"
    getParent: WidgetField = "getParent"
    getParentId: WidgetField = "getParentId"
    getRelativeX: WidgetField = "getRelativeX"
    getRelativeY: WidgetField = "getRelativeY"
    getRotationX: WidgetField = "getRotationX"
    getRotationY: WidgetField = "getRotationY"
    getRotationZ: WidgetField = "getRotationZ"
    getScrollHeight: WidgetField = "getScrollHeight"
    getScrollWidth: WidgetField = "getScrollWidth"
    getScrollX: WidgetField = "getScrollX"
    getScrollY: WidgetField = "getScrollY"
    getSpriteId: WidgetField = "getSpriteId"
    getSpriteTiling: WidgetField = "getSpriteTiling"
    getStaticChildren: WidgetField = "getStaticChildren"
    getTargetPriority: WidgetField = "getTargetPriority"
    getTargetVerb: WidgetField = "getTargetVerb"
    getText: WidgetField = "getText"
    getTextColor: WidgetField = "getTextColor"
    getTextShadowed: WidgetField = "getTextShadowed"
    getType: WidgetField = "getType"
    getVarTransmitTrigger: WidgetField = "getVarTransmitTrigger"
    getWidth: WidgetField = "getWidth"
    getWidthMode: WidgetField = "getWidthMode"
    getXPositionMode: WidgetField = "getXPositionMode"
    getXTextAlignment: WidgetField = "getXTextAlignment"
    getYPositionMode: WidgetField = "getYPositionMode"
    getYTextAlignment: WidgetField = "getYTextAlignment"
    isHidden: WidgetField = "isHidden"


# Module-level instance for IDE autocomplete
WidgetFields = _WidgetFields()


class Widget:
    """Python-side mask builder for widget property queries."""

    _FIELDS: list[WidgetField] = list(typing.get_args(WidgetField))  # keeps exact order
    _FIELD_BITS = {name: 1 << i for i, name in enumerate(_FIELDS)}

    def __init__(self, id):
        self._mask = 0
        self.id = id

    @property
    def mask(self) -> int:
        """Return the combined Java bitmask."""
        return self._mask

    def enable(self, field: WidgetField) -> "Widget":
        """Enable a specific getter flag."""
        self._mask |= self._FIELD_BITS[field]
        return self

    def disable(self, field: WidgetField) -> "Widget":
        """Disable a specific getter flag."""
        self._mask &= ~self._FIELD_BITS[field]
        return self

    def clear(self) -> "Widget":
        """Reset to 0."""
        self._mask = 0
        return self

    def enableAll(self) -> "Widget":
        """Enable all fields."""
        self._mask = (1 << len(self._FIELDS)) - 1
        return self

    @classmethod
    def fromNames(cls, *fields: WidgetField) -> "Widget":
        """Build a mask in one line."""
        w = cls()
        for f in fields:
            w.enable(f)
        return w

    def asDict(self) -> dict[str, bool]:
        """Return {field: enabled?}."""
        return {name: bool(self._mask & bit) for name, bit in self._FIELD_BITS.items()}

    def get(self) -> dict[str, typing.Any]:
        client = getClient()
        result = client.api.invokeCustomMethod(
            target="WidgetInspector",
            method="getWidgetProperties",
            signature="(IJ)[B",
            args=[self.id, self.mask],
            async_exec=self.getAsyncMode(),
        )

        return result

    def getChild(self, child_index: int) -> dict[str, typing.Any]:
        client = getClient()
        result = client.api.invokeCustomMethod(
            target="WidgetInspector",
            method="getWidgetChild",
            signature="(IIJ)[B",
            args=[self.id, child_index, self.mask],
            async_exec=self.getAsyncMode(),
        )

        return result

    def getChildren(self) -> list[dict[str, typing.Any]]:
        client = getClient()
        result = client.api.invokeCustomMethod(
            target="WidgetInspector",
            method="getWidgetChildren",
            signature="(IJ)[B",
            args=[self.id, self.mask],
            async_exec=self.getAsyncMode(),
        )

        return result

    def getChildrenMasked(self, childmask: list[int]) -> list[dict[str, typing.Any]]:
        client = getClient()
        result = client.api.invokeCustomMethod(
            target="WidgetInspector",
            method="getWidgetChildrenMasked",
            signature="(I[IJ)[B",
            args=[self.id, childmask, self.mask],
            async_exec=self.getAsyncMode(),
        )

        return result

    def getAsyncMode(self) -> bool:
        """Return False if mask includes getParent/getParentId (requires sync)."""
        parent_fields = self._FIELD_BITS["getParent"] | self._FIELD_BITS["getParentId"]
        return (self._mask & parent_fields) == 0

    @staticmethod
    def getBatch(widgets: list["Widget"]) -> list[dict[str, typing.Any]]:
        """Get properties for multiple widgets in a single batch request."""
        if not widgets:
            return []

        ids = [w.id for w in widgets]
        masks = [w.mask for w in widgets]

        # Check if any widget has parent fields - if so, use sync mode
        parent_fields = Widget._FIELD_BITS["getParent"] | Widget._FIELD_BITS["getParentId"]
        async_safe = all((w.mask & parent_fields) == 0 for w in widgets)

        client = getClient()
        result = client.api.invokeCustomMethod(
            target="WidgetInspector",
            method="getWidgetPropertiesBatch",
            signature="([I[J)[B",
            args=[ids, masks],
            async_exec=async_safe,
        )

        return result if result else []

    @staticmethod
    def getBatchChildren(widgets: list["Widget"]) -> list[dict[str, typing.Any]]:
        """Get children properties for multiple widgets in a single batch request."""
        if not widgets:
            return []

        ids = [w.id for w in widgets]
        masks = [w.mask for w in widgets]

        # Check if any widget has parent fields - if so, use sync mode
        parent_fields = Widget._FIELD_BITS["getParent"] | Widget._FIELD_BITS["getParentId"]
        async_safe = all((w.mask & parent_fields) == 0 for w in widgets)

        client = getClient()
        result = client.api.invokeCustomMethod(
            target="WidgetInspector",
            method="getWidgetChildrenBatch",
            signature="([I[J)[B",
            args=[ids, masks],
            async_exec=async_safe,
        )

        return result if result else []

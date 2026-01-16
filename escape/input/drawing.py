"""Drawing module - renders shapes directly on RuneLite via Java bridge."""

import numpy as np
from PIL import Image


class Drawing:
    """Drawing utility for rendering debug overlays on RuneLite."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance

    def _init(self):
        """Actual initialization, runs once."""
        pass

    def _invoke(self, method: str, signature: str, args: list) -> dict | None:
        """Invoke a method on the Java Drawing class."""
        from escape.client import client

        return client.api.invokeCustomMethod(
            target="drawing",
            method=method,
            signature=signature,
            args=args,
            async_exec=True,
            declaring_class="Drawing",
        )

    def addBox(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        argbColor: int,
        filled: bool,
        tag: str | None = None,
    ) -> None:
        """Draw a rectangle at screen coordinates."""
        if tag is None:
            self._invoke(
                "addBox",
                "(IIIIIZ)V",
                [x, y, width, height, argbColor, filled],
            )
        else:
            self._invoke(
                "addBox",
                "(IIIIIZLjava/lang/String;)V",
                [x, y, width, height, argbColor, filled, tag],
            )

    def addCircle(
        self,
        x: int,
        y: int,
        radius: int,
        argbColor: int,
        filled: bool,
        tag: str | None = None,
    ) -> None:
        """Draw a circle at screen coordinates."""
        if tag is None:
            self._invoke(
                "addCircle",
                "(IIIIZ)V",
                [x, y, radius, argbColor, filled],
            )
        else:
            self._invoke(
                "addCircle",
                "(IIIIZLjava/lang/String;)V",
                [x, y, radius, argbColor, filled, tag],
            )

    def addLine(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        argbColor: int,
        thickness: int,
        tag: str | None = None,
    ) -> None:
        """Draw a line between two points."""
        if tag is None:
            self._invoke(
                "addLine",
                "(IIIIII)V",
                [x1, y1, x2, y2, argbColor, thickness],
            )
        else:
            self._invoke(
                "addLine",
                "(IIIIIILjava/lang/String;)V",
                [x1, y1, x2, y2, argbColor, thickness, tag],
            )

    def addPolygon(
        self,
        xPoints: list[int],
        yPoints: list[int],
        argbColor: int,
        filled: bool,
        tag: str | None = None,
    ) -> None:
        """Draw a polygon from vertex arrays."""
        if tag is None:
            self._invoke(
                "addPolygon",
                "([I[IIZ)V",
                [xPoints, yPoints, argbColor, filled],
            )
        else:
            self._invoke(
                "addPolygon",
                "([I[IIZLjava/lang/String;)V",
                [xPoints, yPoints, argbColor, filled, tag],
            )

    def addText(
        self,
        text: str,
        x: int,
        y: int,
        argbColor: int,
        fontSize: int = 0,
        tag: str | None = None,
    ) -> None:
        """Draw text at screen coordinates."""
        if tag is None and fontSize == 0:
            self._invoke(
                "addText",
                "(Ljava/lang/String;III)V",
                [text, x, y, argbColor],
            )
        else:
            self._invoke(
                "addText",
                "(Ljava/lang/String;IIIILjava/lang/String;)V",
                [text, x, y, argbColor, fontSize, tag],
            )

    def addImage(
        self,
        argbPixels: list[int],
        imgWidth: int,
        imgHeight: int,
        x: int,
        y: int,
        tag: str | None = None,
    ) -> None:
        """Draw an image from ARGB pixel array."""
        if tag is None:
            self._invoke(
                "addImage",
                "([IIIII)V",
                [argbPixels, imgWidth, imgHeight, x, y],
            )
        else:
            self._invoke(
                "addImage",
                "([IIIIILjava/lang/String;)V",
                [argbPixels, imgWidth, imgHeight, x, y, tag],
            )

    def addImageFromPath(
        self,
        path: str,
        x: int,
        y: int,
        tag: str | None = None,
    ) -> None:
        """Draw an image from a file path."""
        img = Image.open(path).convert("RGBA")
        pixels = np.array(img)

        # Convert RGBA to ARGB int array (0xAARRGGBB)
        argb = (
            (pixels[:, :, 3].astype(np.uint32) << 24)
            | (pixels[:, :, 0].astype(np.uint32) << 16)
            | (pixels[:, :, 1].astype(np.uint32) << 8)
            | pixels[:, :, 2].astype(np.uint32)
        )

        # Convert to signed 32-bit integers (Java expects signed ints)
        argbSigned = argb.astype(np.int32)

        width, height = img.size
        pixelList = argbSigned.flatten().tolist()

        self.addImage(pixelList, width, height, x, y, tag)

    def clear(self) -> None:
        """Clear all drawings."""
        self._invoke("clear", "()V", [])

    def clearTag(self, tag: str) -> None:
        """Clear only drawings with a specific tag."""
        self._invoke("clearTag", "(Ljava/lang/String;)V", [tag])

    def getCount(self) -> int:
        """Get the number of active draw commands."""
        result = self._invoke("getCount", "()I", [])
        if result and "value" in result:
            return result["value"]
        return 0


# Module-level instance
drawing = Drawing()

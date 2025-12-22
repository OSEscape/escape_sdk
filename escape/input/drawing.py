"""Drawing module - renders shapes directly on RuneLite via Java bridge."""

import numpy as np
from PIL import Image


class Drawing:
    """
    Singleton drawing utility for rendering overlays on RuneLite.

    Wraps the Java Drawing class to draw shapes at screen coordinates.
    All colors are ARGB format: 0xAARRGGBB (e.g., 0xFFFF0000 = opaque red).
    All commands persist until clear() is called.

    Example:
        >>> from escape._internal.drawing import drawing
        >>> drawing.addBox(100, 100, 50, 50, 0xFFFF0000, False)  # Red outline box
        >>> drawing.addText("Hello", 100, 80, 0xFFFFFFFF)  # White text
        >>> drawing.clear()  # Remove all drawings
    """

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
        """
        Invoke a method on the Java Drawing class.

        Args:
            method: Method name
            signature: Java method signature
            args: Method arguments

        Returns:
            Result dict or None
        """
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
        """
        Draw a rectangle at screen coordinates.

        Args:
            x: X coordinate (left edge)
            y: Y coordinate (top edge)
            width: Width in pixels
            height: Height in pixels
            argbColor: Color in ARGB format (0xAARRGGBB)
            filled: If True, fill the rectangle. If False, outline only.
            tag: Optional tag for selective clearing

        Example:
            >>> drawing.addBox(100, 100, 50, 50, 0xFFFF0000, False)  # Red outline
            >>> drawing.addBox(200, 100, 50, 50, 0x80FF0000, True)  # Semi-transparent red fill
        """
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
        """
        Draw a circle at screen coordinates.

        Args:
            x: X coordinate (center)
            y: Y coordinate (center)
            radius: Radius in pixels
            argbColor: Color in ARGB format (0xAARRGGBB)
            filled: If True, fill the circle. If False, outline only.
            tag: Optional tag for selective clearing

        Example:
            >>> drawing.addCircle(150, 150, 25, 0xFF00FF00, False)  # Green outline
            >>> drawing.addCircle(250, 150, 25, 0x8000FF00, True)  # Semi-transparent green fill
        """
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
        """
        Draw a line between two points.

        Args:
            x1: Start X coordinate
            y1: Start Y coordinate
            x2: End X coordinate
            y2: End Y coordinate
            argbColor: Color in ARGB format (0xAARRGGBB)
            thickness: Line thickness in pixels
            tag: Optional tag for selective clearing

        Example:
            >>> drawing.addLine(0, 0, 100, 100, 0xFFFFFFFF, 2)  # White diagonal line
        """
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
        """
        Draw a polygon from vertex arrays.

        Args:
            xPoints: List of X coordinates
            yPoints: List of Y coordinates
            argbColor: Color in ARGB format (0xAARRGGBB)
            filled: If True, fill the polygon. If False, outline only.
            tag: Optional tag for selective clearing

        Example:
            >>> # Draw a triangle
            >>> drawing.addPolygon([100, 150, 50], [100, 150, 150], 0xFFFF00FF, False)
        """
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
        """
        Draw text at screen coordinates.

        Args:
            text: Text string to draw
            x: X coordinate
            y: Y coordinate
            argbColor: Color in ARGB format (0xAARRGGBB)
            fontSize: Font size (0 = default)
            tag: Optional tag for selective clearing

        Example:
            >>> drawing.addText("Hello World", 100, 100, 0xFFFFFF00)  # Yellow text
            >>> drawing.addText("Big Text", 100, 150, 0xFFFFFFFF, 24)  # Large white text
        """
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
        """
        Draw an image from ARGB pixel array.

        Args:
            argbPixels: Flat array of ARGB pixel values (length = imgWidth * imgHeight)
            imgWidth: Image width in pixels
            imgHeight: Image height in pixels
            x: X coordinate to draw at
            y: Y coordinate to draw at
            tag: Optional tag for selective clearing

        Example:
            >>> # Draw a 2x2 red square
            >>> pixels = [0xFFFF0000] * 4
            >>> drawing.addImage(pixels, 2, 2, 100, 100)
        """
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
        """
        Draw an image from a file path.

        Supports PNG, JPG, and other formats supported by PIL.
        Handles RGBA transparency correctly.

        Args:
            path: Path to the image file
            x: X coordinate to draw at
            y: Y coordinate to draw at
            tag: Optional tag for selective clearing

        Example:
            >>> drawing.addImageFromPath("/path/to/image.png", 100, 100)
            >>> drawing.addImageFromPath("/path/to/icon.png", 50, 50, "icons")
        """
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
        """
        Clear all drawings.

        Example:
            >>> drawing.addBox(100, 100, 50, 50, 0xFFFF0000, False)
            >>> drawing.clear()  # Remove all
        """
        self._invoke("clear", "()V", [])

    def clearTag(self, tag: str) -> None:
        """
        Clear only drawings with a specific tag.

        Args:
            tag: Tag to clear

        Example:
            >>> drawing.addBox(100, 100, 50, 50, 0xFFFF0000, False, "boxes")
            >>> drawing.addCircle(200, 200, 25, 0xFF00FF00, False, "circles")
            >>> drawing.clearTag("boxes")  # Only removes the box
        """
        self._invoke("clearTag", "(Ljava/lang/String;)V", [tag])

    def getCount(self) -> int:
        """
        Get the number of active draw commands.

        Returns:
            Number of draw commands

        Example:
            >>> drawing.addBox(100, 100, 50, 50, 0xFFFF0000, False)
            >>> drawing.getCount()  # Returns 1
        """
        result = self._invoke("getCount", "()I", [])
        if result and "value" in result:
            return result["value"]
        return 0


# Module-level singleton
drawing = Drawing()

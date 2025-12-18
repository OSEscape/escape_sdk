#!/usr/bin/env python3
"""
RuneLite API Wrapper - Data-Driven Universal Bridge Interface
Uses perfect type conversion data from the scraper for zero-maintenance operation
Now with type-safe enum support to prevent int/enum confusion
"""

import json
import logging
import mmap
import os
import struct
import time
from typing import TYPE_CHECKING, Any, Dict, List, Tuple, Type

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    # For type checkers: always import Query (tells VS Code what type to expect)
    from .query_builder import Query

# Import enum support
try:
    from .enums import EnumValue, generateAllEnumClasses
except ImportError:
    logger.warning("runelite_enums module not found - enum support disabled")
    EnumValue = None
    generateAllEnumClasses = None

# Import query builder support (runtime import)
try:
    from .query_builder import Query as RuntimeQuery
except ImportError:
    logger.warning("query_builder module not found - query builder disabled")
    RuntimeQuery = None

# ============================================================================
# Rust Bridge Shared Memory Protocol Constants
# Must match crates/bridge/src/core/shm/header.rs
# ============================================================================

# ShmHeader field offsets
OFFSET_MAGIC = 0x00
OFFSET_VERSION = 0x04
OFFSET_SEQUENCE = 0x08
OFFSET_LENGTH = 0x10
OFFSET_FLAGS = 0x14
OFFSET_PAYLOAD = 0x18

# Magic numbers for region identification
REQUEST_MAGIC = 0x42524551   # "BREQ" in little-endian
RESPONSE_MAGIC = 0x42525350  # "BRSP" in little-endian

# Protocol version
PROTOCOL_VERSION = 1

# Flag values
FLAG_REQUEST_PENDING = 0x01
FLAG_RESPONSE_READY = 0x01
FLAG_ERROR = 0x02


class RuneLiteAPI:
    """
    Smart API wrapper that uses scraped data to provide exact signatures.

    Singleton pattern - use RuneLiteAPI() to get the shared instance.
    """

    _instance = None

    def __new__(cls, api_data_file: str = None, auto_update: bool = True):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __del__(self):
        """Cleanup when API object is destroyed."""
        # Disabled auto-cleanup to prevent issues
        pass

    def __init__(self, api_data_file: str = None, auto_update: bool = True):
        """
        Load API data and connect to bridge.

        Args:
            api_data_file: Path to API data JSON file (auto-detected if None)
            auto_update: If True, check for RuneLite updates on initialization
        """
        # Skip if already initialized (singleton pattern)
        if self._initialized:
            return
        self._initialized = True

        self.api_channel = None
        self.result_buffer = None
        self.cached_objects = {}
        self.enum_classes = {}  # Store generated enum classes
        self.plugin_data = None  # Plugin API data (loaded separately)
        self._sequence = 0  # Request sequence counter for response correlation

        # Always use the JSON file with perfect type conversion data
        if api_data_file is None:
            # Look for data file in cache directory
            from .cache_manager import getCacheManager

            cache_manager = getCacheManager()
            api_data_file = cache_manager.getDataPath("api") / "runelite_api_data.json"

        # Check for updates if enabled
        if auto_update:
            self._checkAndUpdate()

        # Load scraped API data with perfect type conversion
        try:
            # Convert Path to string if needed
            api_data_file = str(api_data_file)

            # Get the full path to the data file
            if not os.path.isabs(api_data_file):
                script_dir = os.path.dirname(os.path.abspath(__file__))
                api_data_file = os.path.join(script_dir, api_data_file)

            if not os.path.exists(api_data_file):
                raise FileNotFoundError(f"API data file not found: {api_data_file}")

            with open(api_data_file) as f:
                self.api_data = json.load(f)

            # Check if we have the perfect type conversion data
            if "type_conversion" in self.api_data:
                type_count = self.api_data["type_conversion"]["conversion_lookup"]["type_count"]
                logger.info(
                    f"Loaded perfect API data: {len(self.api_data['methods'])} methods, {len(self.api_data['enums'])} enums, {type_count} types"
                )
            else:
                logger.info(
                    f"Loaded API data: {len(self.api_data['methods'])} methods, {len(self.api_data['enums'])} enums"
                )
                logger.warning("No type conversion data found - regenerate with latest scraper")

            # Generate enum classes from API data
            if generateAllEnumClasses:
                self.enum_classes = generateAllEnumClasses(self.api_data)
                logger.info(f"Generated {len(self.enum_classes)} enum classes")

                # Make enums accessible as attributes for convenience
                for enum_name, enum_class in self.enum_classes.items():
                    setattr(self, enum_name, enum_class)
            else:
                logger.warning("Enum generation not available")

        except Exception as e:
            logger.error(f"Failed to load API data: {e}")
            logger.error(f"   Current directory: {os.getcwd()}")
            logger.error(f"   Looking for: {api_data_file}")
            self.api_data = {
                "methods": {},
                "enums": {},
                "classes": [],
                "constants": {},
                "type_conversion": {},
            }

        # Load plugin API data (shortest-path plugin, etc.)
        self._loadPluginData()

    def _loadPluginData(self):
        """
        Load plugin API data from scraped plugin files (e.g., shortest-path plugin).
        This allows querying plugin methods through the query builder.
        """
        try:
            from .cache_manager import getCacheManager

            cache_manager = getCacheManager()
            plugin_data_file = cache_manager.getDataPath("api") / "shortestpath_api_data.json"

            if plugin_data_file.exists():
                with open(plugin_data_file) as f:
                    self.plugin_data = json.load(f)
                logger.info(
                    f"Loaded plugin data: {len(self.plugin_data.get('methods', {}))} methods from {len(self.plugin_data.get('classes', []))} classes"
                )
            else:
                logger.warning("Plugin data not found - plugin queries will not be available")
                self.plugin_data = None

        except Exception as e:
            logger.error(f"Failed to load plugin data: {e}")
            self.plugin_data = None

    def _checkAndUpdate(self):
        """
        Check for RuneLite API updates and regenerate if needed.
        If an update is found, regenerates and does NOT exit (continues with new data).
        """
        try:
            # Import auto_updater (absolute import to avoid issues)
            from escape_sdk._internal.updater.api import RuneLiteAPIUpdater

            updater = RuneLiteAPIUpdater()

            # Check if update is needed
            needs_update, reason = updater.shouldUpdate(force=False, max_age_days=7)

            if needs_update:
                logger.info("RuneLite API Update")
                logger.info(f"{reason}")

                # Run the update
                success = updater.update(force=False, max_age_days=7)

                if success:
                    logger.info("API data generated successfully")

                    # Reload query_builder to pick up newly generated proxies
                    import sys

                    if "escape_sdk._internal.query_builder" in sys.modules:
                        logger.info("Reloading query_builder with new proxies...")
                        import importlib

                        from . import query_builder

                        importlib.reload(query_builder)
                        # Update the RuntimeQuery reference
                        global RuntimeQuery
                        RuntimeQuery = query_builder.Query
                        logger.info("Query builder reloaded")
                else:
                    logger.error("API update failed")
                    raise FileNotFoundError("API update failed - cannot continue")

        except ImportError as e:
            # auto_updater not available, skip update check
            logger.warning(f"API updater not available: {e}")
        except FileNotFoundError:
            # Re-raise file not found errors
            raise
        except Exception as e:
            logger.warning(f"Auto-update check failed: {e}")
            import traceback

            traceback.print_exc()

    def __enter__(self):
        """Context manager entry - connect to bridge."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        # Don't suppress exceptions
        return False

    def connect(self) -> bool:
        """Connect to the universal bridge"""
        try:
            self.api_fd = open("/dev/shm/runelite_api_universal", "r+b")
            self.api_channel = mmap.mmap(
                self.api_fd.fileno(), 16 * 1024 * 1024
            )  # 16MB to match C side

            self.result_fd = open("/dev/shm/runelite_results_universal", "r+b")
            self.result_buffer = mmap.mmap(
                self.result_fd.fileno(), 16 * 1024 * 1024
            )  # 16MB to match C side

            logger.info("Connected to bridge")
            return True
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            return False

    def _parseSignatureParams(self, signature: str) -> List[str]:
        """
        Parse JNI signature and extract all parameter types.
        Consolidated parser used by all methods to avoid duplicate parsing logic.

        Args:
            signature: JNI method signature (e.g., "(ILjava/lang/String;)V")

        Returns:
            List of JNI type strings for each parameter
        """
        params_str = signature[signature.index("(") + 1 : signature.index(")")]
        if not params_str:
            return []

        param_types = []
        i = 0
        while i < len(params_str):
            if params_str[i] == "L":
                # Object type - find semicolon
                end = params_str.index(";", i)
                param_types.append(params_str[i : end + 1])
                i = end + 1
            elif params_str[i] == "[":
                # Array type - consume all array dimensions
                j = i
                while j < len(params_str) and params_str[j] == "[":
                    j += 1
                if j < len(params_str) and params_str[j] == "L":
                    end = params_str.index(";", j)
                    param_types.append(params_str[i : end + 1])
                    i = end + 1
                else:
                    param_types.append(params_str[i : j + 1])
                    i = j + 1
            else:
                # Primitive type - single character
                param_types.append(params_str[i])
                i += 1

        return param_types

    def _fixWidgetPath(self, signature: str) -> str:
        """Fix Widget class path in signature (should be in widgets package)."""
        if "Widget" not in signature:
            return signature
        return (
            signature.replace("Lnet/runelite/api/Widget;", "Lnet/runelite/api/widgets/Widget;")
            .replace("[Lnet/runelite/api/Widget;", "[Lnet/runelite/api/widgets/Widget;")
            .replace("[[Lnet/runelite/api/Widget;", "[[Lnet/runelite/api/widgets/Widget;")
        )

    def _normalizeClassName(self, class_name: str) -> str:
        """
        Normalize class name to full JNI path format.

        Args:
            class_name: Simple name (e.g., "WorldPoint") or path (e.g., "net.runelite.api.coords.WorldPoint")

        Returns:
            Normalized JNI path (e.g., "net/runelite/api/coords/WorldPoint")
        """
        # Convert dots to slashes
        normalized = class_name.replace(".", "/")

        # If already a full path, return it
        if "/" in normalized:
            return normalized

        # Look up full path from class_packages
        if "class_packages" in self.api_data:
            package_path = self.api_data["class_packages"].get(normalized)
            if package_path:
                return f"{package_path}/{normalized}"

        # Try common packages as fallback
        if normalized in ["WorldPoint", "LocalPoint", "WorldArea"]:
            return f"net/runelite/api/coords/{normalized}"

        return f"net/runelite/api/{normalized}"

    def _findMethodInHierarchy(self, method_name: str, target_class: str, signatures: List) -> List:
        """
        Find method signatures by walking up the inheritance tree.

        Args:
            method_name: Name of the method to find
            target_class: Normalized class name to start search from
            signatures: Full list of signatures to filter

        Returns:
            Filtered list of (declaring_class, signature, return_type) tuples
        """
        # Extract simple class name for inheritance lookup
        simple_target = target_class.split("/")[-1]

        # Try exact match first
        filtered = [
            (item[0], item[1], item[2] if len(item) > 2 else None)
            for item in signatures
            if item[0] == target_class
        ]

        if filtered or "inheritance" not in self.api_data:
            return filtered

        # Walk up inheritance tree
        inheritance = self.api_data["inheritance"]
        current = simple_target
        seen = set()

        while current and current not in seen:
            seen.add(current)
            if current in inheritance and "extends" in inheritance[current]:
                parent = inheritance[current]["extends"]
                # Handle multiple inheritance - take first parent
                if "," in parent:
                    parent = parent.split(",")[0].strip()

                # Try to find method in parent class
                filtered = [
                    (item[0], item[1], item[2] if len(item) > 2 else None)
                    for item in signatures
                    if item[0].endswith("/" + parent)
                ]

                if filtered:
                    return filtered

                current = parent
            else:
                break

        return []

    def getMethodSignature(
        self, method_name: str, args: List | None = None, target_class: str = "Client"
    ) -> str | None:
        """
        Get the correct JNI signature for a method based on arguments.
        Now delegates to get_method_info for consistency.
        """
        info = self.getMethodInfo(method_name, args, target_class)
        return info["signature"] if info else None

    def getMethodInfo(
        self, method_name: str, args: List | None = None, target_class: str = "Client"
    ) -> dict | None:
        """
        Get both the signature AND declaring class for a method.
        Returns dict with 'signature', 'declaring_class', and 'return_type'.

        If target_class is provided (e.g., "net/runelite/api/GameObject"), will find methods
        declared on that class OR its parent classes (e.g., TileObject).
        Uses actual inheritance data from the scraped API.

        Also checks plugin data for plugin classes (e.g., "shortestpath/Pathfinder").
        """
        # Check if target_class is a plugin class (contains "shortestpath")
        is_plugin_class = target_class and "shortestpath" in target_class

        # Choose which data source to use
        methods_data = (
            self.plugin_data.get("methods", {})
            if is_plugin_class and self.plugin_data
            else self.api_data["methods"]
        )

        if method_name not in methods_data:
            return None

        signatures = methods_data[method_name]

        # Filter by class if specified and not None/empty
        if target_class:
            normalized_target = self._normalizeClassName(target_class)
            filtered = self._findMethodInHierarchy(method_name, normalized_target, signatures)

            if filtered:
                signatures = filtered
            elif target_class:  # Explicitly filtered but found nothing
                return None

        # Find best matching signature based on arguments
        if args is not None:
            best_match = None
            best_score = -1

            for item in signatures:
                cls, sig = item[0], item[1]
                ret_type = item[2] if len(item) > 2 else None
                score = self._scoreSignatureMatch(sig, args)

                if score > best_score:
                    best_score = score
                    best_match = {
                        "signature": self._fixWidgetPath(sig),
                        "declaring_class": cls,
                        "return_type": ret_type,
                    }

            return best_match if best_match and best_score >= 0 else None

        # Fallback to first signature (no args provided)
        if signatures:
            first = signatures[0]
            return {
                "signature": self._fixWidgetPath(first[1]),
                "declaring_class": first[0],
                "return_type": first[2] if len(first) > 2 else None,
            }

        return None

    def _scoreSignatureMatch(self, signature: str, args: List) -> int:
        """
        Score how well arguments match a signature.
        Higher score = better match.
        Returns -1 for no match.
        """
        # Extract parameter types from signature (using consolidated parser)
        param_types = self._parseSignatureParams(signature)

        # Check argument count
        if len(args) != len(param_types):
            return -1

        score = 0
        for arg, param_type in zip(args, param_types, strict=False):
            arg_score = self._scoreArgMatch(arg, param_type)
            if arg_score < 0:
                return -1  # Invalid match
            score += arg_score

        return score

    def _scoreArgMatch(self, arg: Any, param_type: str) -> int:
        """Score how well a single argument matches a parameter type."""
        # Special 'client' proxy
        if hasattr(arg, "ref_id") and arg.ref_id == "client":
            if param_type == "Lnet/runelite/api/Client;":
                return 100  # Perfect match
            elif param_type == "Ljava/lang/Object;":
                return 50  # Compatible
            return -1  # Not compatible

        # QueryRef or proxy object with return_type
        if hasattr(arg, "return_type") and arg.return_type:
            if param_type.startswith("L") and param_type.endswith(";"):
                expected_jni = f"L{arg.return_type.replace('.', '/')};".replace("//", "/")
                if expected_jni == param_type:
                    return 100  # Perfect match
                elif param_type == "Ljava/lang/Object;":
                    return 50  # Object is compatible
                return 20  # Possible subclass/interface match
            return -1  # QueryRef but expecting primitive

        # EnumValue for enum parameter
        if EnumValue and isinstance(arg, EnumValue):
            if param_type.startswith("L") and param_type.endswith(";"):
                expected_enum = param_type[1:-1].split("/")[-1]
                return 100 if arg._enum_name == expected_enum else -1
            return -1  # Not an object type

        # Primitive types
        if isinstance(arg, int):
            if param_type == "I":
                return 100  # Perfect int match
            # Check if int could be enum ordinal (discouraged but allowed)
            if param_type.startswith("Lnet/runelite/api/") and param_type.endswith(";"):
                enum_name = param_type[1:-1].split("/")[-1]
                if enum_name in self.api_data.get("enums", {}):
                    enum_values = self.api_data["enums"][enum_name].get("values", [])
                    return 10 if 0 <= arg < len(enum_values) else -1
                return 5  # Unknown enum, might work
            return -1

        if isinstance(arg, str):
            if param_type == "Ljava/lang/String;":
                return 100  # Perfect string match
            return -1  # String not allowed for other types

        # No match
        return -1

    def convertArgument(
        self, arg_value: Any, signature: str, arg_index: int = 0
    ) -> Tuple[str, str]:
        """
        Perfect type conversion using the scraped data.
        STRICT MODE: Enums must be EnumValue objects, no string shortcuts!
        Returns (type, value) tuple for the bridge
        """
        # FIRST: Check if it's an EnumValue object - this takes priority!
        if EnumValue and isinstance(arg_value, EnumValue):
            return (arg_value._enum_name, str(arg_value._ordinal))

        # Extract the JNI type for this parameter from the signature (using consolidated parser)
        param_types = self._parseSignatureParams(signature)
        if arg_index >= len(param_types):
            return ("int", str(arg_value))

        jni_type = param_types[arg_index]

        # Use the perfect type conversion database if available
        if "type_conversion" in self.api_data and "all_types" in self.api_data["type_conversion"]:
            type_info = self.api_data["type_conversion"]["all_types"].get(jni_type)

            if type_info:
                return self._convertByCategory(arg_value, jni_type, type_info)

        # Fallback for when perfect data isn't available
        return self._convertFallback(arg_value, jni_type)

    def _convertByCategory(self, arg_value: Any, jni_type: str, type_info: dict) -> Tuple[str, str]:
        """Convert argument based on type category from API data."""
        category = type_info["category"]

        if category == "primitive":
            if isinstance(arg_value, int) and jni_type == "I":
                return ("int", str(arg_value))
            return (type_info["bridge_type"], str(arg_value))

        elif category == "enum":
            enum_name = type_info["bridge_type"]
            if isinstance(arg_value, str):
                raise TypeError(
                    f"Expected {enum_name} enum object, got string '{arg_value}'.\n"
                    f"Use: api.{enum_name}.{arg_value.upper()} or api.{enum_name}.from_name('{arg_value}')"
                )
            elif isinstance(arg_value, int):
                raise TypeError(
                    f"Expected {enum_name} enum object, got integer {arg_value}.\n"
                    f"Use: api.{enum_name}.from_ordinal({arg_value}) or api.{enum_name}[{arg_value}]"
                )
            return (type_info["bridge_type"], str(arg_value))

        elif category == "java":
            bridge_type = type_info["bridge_type"]
            if bridge_type == "String":
                return ("String", str(arg_value))
            elif bridge_type == "Boolean":
                return ("Boolean", "true" if arg_value else "false")
            return (bridge_type, str(arg_value))

        elif category == "object":
            if isinstance(arg_value, str) and arg_value.startswith("obj_"):
                return ("object", arg_value)
            return ("object", str(arg_value))

        elif category == "array":
            return ("array", str(arg_value))

        return ("object", str(arg_value))

    def _convertFallback(self, arg_value: Any, jni_type: str) -> Tuple[str, str]:
        """Fallback conversion when type_conversion data isn't available."""
        if isinstance(arg_value, int):
            if jni_type == "I":
                return ("int", str(arg_value))
            elif jni_type == "J":
                return ("long", str(arg_value))
            return ("int", str(arg_value))

        # Map JNI types to bridge types
        type_map = {
            "I": "int",
            "B": "int",
            "S": "int",
            "C": "int",
            "J": "long",
            "Z": "boolean",
            "F": "float",
            "D": "float",
            "Ljava/lang/String;": "String",
        }

        bridge_type = type_map.get(jni_type, "object")

        if bridge_type == "boolean":
            return (bridge_type, "true" if arg_value else "false")

        return (bridge_type, str(arg_value))

    def getStaticMethodSignature(
        self, class_name: str, method_name: str, args: tuple
    ) -> str | None:
        """
        Get static method signature.
        Uses regular method signature lookup since format is the same.
        """
        return self.getMethodSignature(method_name, args, target_class=class_name.split(".")[-1])

    def getEnumValue(self, enum_name: str, ordinal: int) -> str | None:
        """Get enum constant name from ordinal using perfect data"""
        if "type_conversion" in self.api_data:
            # Search for enum in all packages
            for jni_sig, enum_info in self.api_data["type_conversion"]["enums"].items():
                # Check if this is the enum we're looking for (by simple name)
                if jni_sig.endswith(f"/{enum_name};"):
                    return enum_info.get("ordinal_to_name", {}).get(ordinal)
        return None

    def getEnumOrdinal(self, enum_name: str, value_name: str) -> int | None:
        """Get enum ordinal from constant name using perfect data"""
        if "type_conversion" in self.api_data:
            # Search for enum in all packages
            for jni_sig, enum_info in self.api_data["type_conversion"]["enums"].items():
                # Check if this is the enum we're looking for (by simple name)
                if jni_sig.endswith(f"/{enum_name};"):
                    return enum_info.get("name_to_ordinal", {}).get(value_name.upper())
        return None

    def getEnum(self, enum_name: str) -> Type | None:
        """Get an enum class by name"""
        return self.enum_classes.get(enum_name)

    def listEnums(self) -> List[str]:
        """List all available enum names"""
        return sorted(self.enum_classes.keys())

    def query(self) -> "Query":
        """
        Create a new query builder for batch operations.

        Returns:
            Query object for building chained API calls
        """
        if RuntimeQuery is None:
            raise RuntimeError("Query builder not available - missing query_builder module")

        # Create a new Query instance with this API
        return RuntimeQuery(self)

    def _next_sequence(self) -> int:
        """Get the next sequence number for request correlation."""
        self._sequence += 1
        return self._sequence

    def _sendRequest(self, encoded_data: bytes) -> int:
        """
        Send encoded request to bridge via shared memory.

        Args:
            encoded_data: MessagePack-encoded request data

        Returns:
            Sequence number for this request (for response validation)
        """
        seq = self._next_sequence()

        # Wait for bridge to clear pending from previous request (max 10ms)
        wait_start = time.perf_counter()
        while (time.perf_counter() - wait_start) * 1000 < 10:
            self.api_channel.seek(OFFSET_FLAGS)
            old_flags = struct.unpack("<I", self.api_channel.read(4))[0]
            if (old_flags & FLAG_REQUEST_PENDING) == 0:
                break
            time.sleep(0.0001)  # 100μs

        # Clear response buffer header
        self.result_buffer.seek(0)
        self.result_buffer.write(struct.pack("<IIQII", 0, 0, 0, 0, 0))  # Clear 24 bytes

        # Write request header
        self.api_channel.seek(OFFSET_MAGIC)
        self.api_channel.write(struct.pack("<I", REQUEST_MAGIC))

        self.api_channel.seek(OFFSET_VERSION)
        self.api_channel.write(struct.pack("<I", PROTOCOL_VERSION))

        self.api_channel.seek(OFFSET_SEQUENCE)
        self.api_channel.write(struct.pack("<Q", seq))  # uint64

        self.api_channel.seek(OFFSET_LENGTH)
        self.api_channel.write(struct.pack("<I", len(encoded_data)))

        # Write payload
        self.api_channel.seek(OFFSET_PAYLOAD)
        self.api_channel.write(encoded_data)

        # Set pending flag (must be last - signals request is ready)
        self.api_channel.seek(OFFSET_FLAGS)
        self.api_channel.write(struct.pack("<I", FLAG_REQUEST_PENDING))

        return seq

    def _waitForResponse(self, expected_seq: int, timeout_ms: int = 10000) -> bytes | None:
        """
        Wait for response from bridge with exponential backoff polling.

        Args:
            expected_seq: Expected sequence number (from _sendRequest return value)
            timeout_ms: Timeout in milliseconds

        Returns:
            Response data bytes, or None on timeout

        Raises:
            RuntimeError: If response sequence doesn't match expected sequence
        """
        start_time = time.perf_counter()
        poll_count = 0

        while (time.perf_counter() - start_time) * 1000 < timeout_ms:
            # Check flags for response ready
            self.result_buffer.seek(OFFSET_FLAGS)
            flags = struct.unpack("<I", self.result_buffer.read(4))[0]

            if flags & FLAG_RESPONSE_READY:
                elapsed = (time.perf_counter() - start_time) * 1000
                if elapsed > 100:
                    logger.debug(f"Response ready after {elapsed:.2f}ms (polls={poll_count})")

                # Verify magic number
                self.result_buffer.seek(OFFSET_MAGIC)
                magic = struct.unpack("<I", self.result_buffer.read(4))[0]
                if magic != RESPONSE_MAGIC:
                    logger.error(f"Invalid response magic: 0x{magic:08X} (expected 0x{RESPONSE_MAGIC:08X})")
                    self._clearResponseFlags()
                    return None

                # Verify sequence number matches
                self.result_buffer.seek(OFFSET_SEQUENCE)
                response_seq = struct.unpack("<Q", self.result_buffer.read(8))[0]
                if response_seq != expected_seq:
                    raise RuntimeError(
                        f"Sequence mismatch: expected {expected_seq}, got {response_seq}. "
                        "This indicates a protocol desync - bridge may have crashed or restarted."
                    )

                # Read payload length
                self.result_buffer.seek(OFFSET_LENGTH)
                length = struct.unpack("<I", self.result_buffer.read(4))[0]

                if length == 0:
                    logger.debug(f"Ready but length=0 after {elapsed:.2f}ms (seq={response_seq})")
                    self._clearResponseFlags()
                    return None

                # Read payload data
                self.result_buffer.seek(OFFSET_PAYLOAD)
                data = self.result_buffer.read(length)

                # Clear response flags
                self._clearResponseFlags()

                return data

            # Exponential backoff polling
            poll_count += 1
            if poll_count < 5000:
                pass  # Busy wait for ~1.5ms
            elif poll_count < 10000:
                time.sleep(0.00001)  # 10μs sleep
            elif poll_count < 20000:
                time.sleep(0.0001)  # 100μs sleep
            else:
                time.sleep(0.001)  # 1ms sleep

        # Timeout
        elapsed = (time.perf_counter() - start_time) * 1000
        self.api_channel.seek(OFFSET_FLAGS)
        request_flags = struct.unpack("<I", self.api_channel.read(4))[0]
        logger.warning(f"TIMEOUT after {elapsed:.2f}ms waiting for seq={expected_seq} (polls={poll_count}, request_flags=0x{request_flags:02X})")
        return None

    def _clearResponseFlags(self) -> None:
        """Clear response ready flags after reading response."""
        self.result_buffer.seek(OFFSET_FLAGS)
        self.result_buffer.write(struct.pack("<I", 0))

    def _decodeMsgpackResponse(self, data: bytes) -> Any:
        """
        Decode MessagePack response, handling magic header if present.

        Args:
            data: Raw response bytes (already trimmed to exact message size in _wait_for_response)

        Returns:
            Decoded MessagePack data
        """
        import msgpack

        if len(data) >= 8:
            magic = struct.unpack("<I", data[:4])[0]
            if magic == 0xDEADBEEF:
                msg_size = struct.unpack("<I", data[4:8])[0]
                # Data was already trimmed in _wait_for_response, so just decode
                return msgpack.unpackb(data[8 : 8 + msg_size], raw=False, strict_map_key=False)

        # No magic header - decode directly
        # Data was already trimmed in _wait_for_response if it had a magic header
        return msgpack.unpackb(data, raw=False, strict_map_key=False)

    def executeBatchQuery(self, operations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Execute a batch query using MessagePack v2 protocol.

        Args:
            operations: List of operation dicts to execute

        Returns:
            Dictionary with results from the batch execution
        """
        if not self.api_channel or not self.result_buffer:
            raise RuntimeError("Not connected to bridge - call connect() first")

        import msgpack

        # Encode and send request
        encoded = msgpack.packb(operations)
        seq = self._sendRequest(encoded)

        # Wait for and decode response (validates sequence)
        data = self._waitForResponse(expected_seq=seq, timeout_ms=2500)
        if not data:
            return {"error": "Timeout waiting for batch response", "success": False}

        try:
            results = self._decodeMsgpackResponse(data)

            # Handle error responses from bridge
            if isinstance(results, dict) and "error" in results:
                return {"error": results.get("error"), "success": False, "results": None}

            # Normal response - ensure it's a list
            response = {
                "results": results if isinstance(results, list) else [results],
                "success": True,
            }

            # Cache object references
            if response.get("results"):
                for result in response["results"]:
                    if isinstance(result, dict) and "_ref" in result:
                        self.cached_objects[result["_ref"]] = result

            return response

        except Exception as e:
            return {"error": f"Failed to decode response: {e}", "success": False, "results": None}

    def invokeCustomMethod(
        self,
        target: str,
        method: str,
        signature: str,
        args: List[Any] | None = None,
        async_exec: bool = False,
        declaring_class: str | None = None,
    ) -> Any:
        """
        Invoke a custom Java method directly.

        Args:
            target: Target class name (e.g., "HelloWorld", "net.runelite.api.Client")
            method: Method name (e.g., "greetPlayer")
            signature: Java method signature (e.g., "()Ljava/lang/String;")
            args: Optional list of arguments to pass
            async_exec: If False, executes on client thread. If True, executes async.

        Returns:
            Method return value

        Example:
            >>> api.invokeCustomMethod(
            ...     target="HelloWorld",
            ...     method="greetPlayer",
            ...     signature="()Ljava/lang/String;",
            ...     args=[],
            ...     async_exec=False
            ... )
            "Hello, Player123!"
        """
        operation = {
            "async": async_exec,
            "target": target,
            "method": method,
            "signature": signature,
            "args": args if args is not None else [],
        }
        if declaring_class:
            operation["declaring_class"] = declaring_class

        response = self.executeBatchQuery([operation])

        if not response.get("success"):
            error = response.get("error", "Unknown error")
            raise RuntimeError(f"Custom method invocation failed: {error}")

        results = response.get("results", [])
        if not results:
            return None

        return results[0]

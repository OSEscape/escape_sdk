# ShadowLib

A Python SDK for Old School RuneScape (OSRS) bot development that communicates with RuneLite via a high-performance bridge. The architecture mirrors the game's interface, making it intuitive for OSRS developers.

## Requirements

- **Python 3.12+**
- **Linux** with inotify support (required for event system)
- **RuneLite** with ShadowBot plugin running

## Features

- **Game-Native Structure**: Directory layout mirrors OSRS client interface (tabs, interfaces, world)
- **Event-Driven Architecture**: Zero-CPU inotify-based event system for real-time game state
- **Singleton Pattern**: All modules are singletons with lazy initialization
- **Type-Safe**: Full type hints with IDE autocomplete support
- **Auto-Generated Constants**: ItemID, NpcID, ObjectID, InterfaceID, and more
- **3D Projection**: Convert local/world coordinates to screen coordinates

## Installation

```bash
# Clone the repository
git clone https://github.com/shadowbot/shadowlib.git
cd shadowlib

# Install with development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

## Quick Start

```python
from shadowlib.client import client

# Client auto-connects on import and starts event consumer
# All modules are singletons - no instantiation needed

# Access inventory
items = client.tabs.inventory.getItems()
for item in items:
    print(f"{item.name}: {item.quantity}")

# Check player state
pos = client.player.position
print(f"Player at: {pos}")

# Use bank interface
if client.interfaces.bank.isOpen():
    client.interfaces.bank.depositAll()

# Direct module access (alternative pattern)
from shadowlib.tabs.inventory import inventory
from shadowlib.input.mouse import mouse

inventory.clickItem(995)  # Click coins
mouse.leftClick(100, 200)
```

## Architecture

### Module Structure

```
shadowlib/
├── client.py           # Main singleton - auto-connects to RuneLite bridge
├── globals.py          # Global accessors (getClient, getApi, getEventCache)
│
├── tabs/               # Side panel tabs (14 tabs)
│   ├── inventory.py    # Inventory management
│   ├── equipment.py    # Worn equipment
│   ├── skills.py       # Skill levels and XP
│   ├── prayer.py       # Prayer activation
│   ├── magic.py        # Spellbook
│   ├── combat.py       # Combat options
│   └── ...             # friends, settings, logout, etc.
│
├── interfaces/         # Overlay windows
│   ├── bank.py         # Bank interface
│   └── ...             # GE, shop, dialogue (planned)
│
├── world/              # 3D world entities
│   ├── ground_items.py # Items on the ground
│   └── projection.py   # Coordinate projection (local → screen)
│
├── input/              # OS-level input
│   ├── mouse.py        # Mouse control
│   ├── keyboard.py     # Keyboard input
│   └── runelite.py     # RuneLite window management
│
├── interactions/       # Game interactions
│   └── menu.py         # Right-click menu handling
│
├── player/             # Player state
│   └── player.py       # Position, stats, status
│
├── navigation/         # Movement systems
│   └── pathfinder.py   # Pathfinding (planned)
│
├── types/              # Type definitions
│   ├── item.py         # Item dataclass
│   ├── widget.py       # Widget mask builder
│   ├── packed_position.py  # Coordinate packing
│   └── ...
│
├── utilities/          # Helper functions
│   ├── timing.py       # sleep, waitUntil
│   └── text.py         # Text utilities
│
└── _internal/          # Internal implementation
    ├── api.py          # RuneLite bridge API
    ├── query_builder.py # Fluent query interface
    ├── cache/          # Event cache and state builder
    ├── events/         # Inotify event consumer
    └── resources/      # Varps, objects database
```

### Singleton Pattern

All modules use the singleton pattern with `__new__` + `_init()`:

```python
# Two equivalent access patterns:

# Via client namespace
from shadowlib.client import client
client.tabs.inventory.getItems()

# Direct import
from shadowlib.tabs.inventory import inventory
inventory.getItems()
```

### Event System

The SDK uses an inotify-based event system for zero-CPU-usage when idle:

```python
from shadowlib.client import client

# Access cached game state (updated automatically)
tick = client.cache.tick
energy = client.cache.energy
position = client.cache.position

# Get recent events
chats = client.cache.getRecentEvents('chat_message', n=10)
stats = client.cache.getRecentEvents('stat_changed', n=5)

# Access varps/varbits
quest_points = client.cache.getVarp(101)

# Check data freshness
if client.cache.isFresh(max_age=1.0):
    print(f"Data age: {client.cache.getAge():.2f}s")
```

**Event Channels:**

| Channel Type | Channels | Description |
|-------------|----------|-------------|
| Ring Buffer | `varbit_changed`, `chat_message`, `item_container_changed`, `stat_changed`, `animation_changed` | Guaranteed delivery, keeps history |
| Latest State | `gametick`, `camera_changed`, `world_view_loaded`, `world_entity`, `menu_open`, `ground_items` | Current state only |

### Projection System

Convert local/world coordinates to screen coordinates:

```python
from shadowlib.world.projection import projection

# Auto-configured from events - just use it
screen_pos = projection.localToCanvasSingle(localX, localY, plane)
if screen_pos:
    screenX, screenY = screen_pos
    print(f"Screen position: ({screenX}, {screenY})")

# Batch projection
import numpy as np
xs = np.array([1000, 2000, 3000])
ys = np.array([1000, 2000, 3000])
screenX, screenY, valid = projection.localToCanvas(xs, ys, plane=0)
```

### Query Builder

Direct RuneLite API access with fluent interface:

```python
from shadowlib.client import client

# Build and execute queries
q = client.query()
result = q.execute({
    "inventory": q.client.getItemContainer(93),
    "position": q.localPlayer.getWorldLocation(),
    "health": q.localPlayer.getHealthRatio()
})
```

## Code Style

### Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Functions/Methods | camelCase | `getItems()`, `isInventoryFull()` |
| Classes | PascalCase | `Inventory`, `BankInterface` |
| Constants | UPPER_CASE | `MAX_INVENTORY_SIZE` |
| Private | _camelCase | `_internalHelper()` |

### Dependencies

```python
# Use dependency injection with global fallback
class Inventory:
    def __init__(self, client=None):
        self.client = client or getClient()
```

## Development

### Running Tests

```bash
pytest                           # All tests
pytest --cov=shadowlib           # With coverage
pytest tests/test_inventory.py   # Specific file
pytest -k "test_bank"            # Pattern match
```

### Linting and Formatting

```bash
ruff check .           # Lint
ruff check --fix .     # Auto-fix
ruff format .          # Format
python check_naming.py # Verify naming conventions
```

### Pre-commit Hooks

```bash
pre-commit install       # Install hooks
pre-commit run --all-files  # Run manually
```

## Generated Files

On first import, ShadowLib downloads and generates:

```
~/.cache/shadowlib/
├── generated/           # Proxy classes, constants
│   ├── constants/       # ItemID, NpcID, ObjectID, etc.
│   └── proxies/         # API proxy classes
└── data/                # Game data
    ├── api_data.json    # API metadata
    ├── varps.json       # Varp definitions
    └── objects.json     # Object database
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feat/new-feature`)
3. Follow naming conventions and code style
4. Write tests for new functionality
5. Commit with conventional commits (`feat:`, `fix:`, etc.)
6. Open a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## License

MIT License - see LICENSE file for details.

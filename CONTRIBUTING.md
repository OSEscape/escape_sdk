# Contributing to Escape

Thank you for your interest in contributing to Escape! This document provides guidelines and instructions for contributing.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR-USERNAME/escape.git`
3. Install dependencies: `pip install -e ".[dev]"`
4. Install pre-commit hooks: `pre-commit install`
5. Create a branch: `git checkout -b feat/your-feature-name`

## Ruff - Our Code Quality Tool

We use **[Ruff](https://docs.astral.sh/ruff/)** for all linting and formatting. Ruff is an extremely fast Python linter and formatter written in Rust - it's 10-100x faster than traditional tools like flake8/black.

### Why Ruff?

- **Speed**: Lints entire codebase in milliseconds
- **All-in-one**: Replaces flake8, isort, black, pyupgrade, and more
- **Modern**: Native support for Python 3.12+ features
- **Zero config needed**: Works out of the box with our `pyproject.toml`

### Quick Commands

```bash
# Check for linting issues
ruff check .

# Auto-fix linting issues
ruff check --fix .

# Format code
ruff format .

# Check formatting without changing files
ruff format --check .
```

### Pre-commit Integration

Ruff runs automatically on every commit via pre-commit hooks:

```bash
# Install hooks (one-time setup)
pre-commit install

# Now every commit automatically runs ruff
git commit -m "feat: add new feature"  # ruff runs automatically
```

If pre-commit blocks your commit, just run `ruff check --fix . && ruff format .` and commit again.

## Commit Message Convention

We use [Conventional Commits](https://www.conventionalcommits.org/) for automated versioning and changelog generation.

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

| Type | Description | Version Bump |
|------|-------------|--------------|
| `feat` | New feature | Minor |
| `fix` | Bug fix | Patch |
| `docs` | Documentation only | Patch |
| `style` | Code style (formatting) | None |
| `refactor` | Code refactoring | None |
| `perf` | Performance improvement | Patch |
| `test` | Adding/updating tests | None |
| `build` | Build system changes | None |
| `ci` | CI/CD changes | None |
| `chore` | Other changes | None |

### Breaking Changes

Add `!` after type or `BREAKING CHANGE:` in footer for major version bump:

```bash
feat!: redesign inventory API

BREAKING CHANGE: get_items() now returns Item objects instead of IDs
```

### Examples

```bash
# Feature
feat(inventory): add get_items_by_name method

# Bug fix
fix(bank): resolve deposit all items issue

# With body
feat(interfaces): add grand exchange module

Implements buy/sell orders, price checking, and item search.

Closes #123
```

## Code Style

### Naming Conventions (PEP 8)

| Element | Convention | Example |
|---------|------------|---------|
| Functions/Methods | snake_case | `get_items()`, `is_inventory_full()` |
| Classes | PascalCase | `Inventory`, `BankInterface` |
| Constants | UPPER_CASE | `MAX_INVENTORY_SIZE` |
| Private | _snake_case | `_internal_helper()` |

### Type Hints

Use modern Python type hints:

```python
from collections.abc import Sequence

# For parameters, prefer abstract types (Sequence, Mapping, Iterable)
def process_items(items: Sequence[Item]) -> list[Item]:
    return [item for item in items if item.is_valid]

# For return types, use concrete types (list, dict)
def get_all_items() -> list[Item]:
    return self._items.copy()
```

### Singleton Pattern

All major modules use the singleton pattern:

```python
class NewModule:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance

    def _init(self):
        """Actual initialization."""
        pass

# Module-level export
new_module = NewModule()
```

### Property vs Method

- `@property` → Namespace access, singleton access
- Methods → Actions, queries, anything with parameters

```python
# Property for namespace
@property
def tabs(self) -> Tabs:
    return tabs

# Method for action
def get_items(self) -> list[Item]:
    return self._items
```

### Absolute Imports

Always use absolute imports:

```python
# Correct
from escape.globals import get_client
from escape.tabs.inventory import inventory

# Wrong
from ...globals import get_client
```

## Project Structure

```
escape/
├── tabs/           # Side panel tabs (inventory, skills, etc.)
├── interfaces/     # Overlay windows (bank, GE, shop)
├── world/          # 3D world entities (NPCs, objects, ground items)
├── input/          # OS-level input (mouse, keyboard)
├── interactions/   # Game interactions (menu)
├── player/         # Player state
├── navigation/     # Movement and pathfinding
├── types/          # Type definitions and models
├── utilities/      # Helper functions
└── _internal/      # Internal implementation
```

### Placement Rules

1. Visible in 3D world? → `world/`
2. Side panel tab? → `tabs/`
3. Overlay window? → `interfaces/`
4. Movement/pathing? → `navigation/`
5. Interaction primitives? → `interactions/`
6. Low-level input? → `input/`
7. Type/enum/model? → `types/`
8. Helper function? → `utilities/`
9. Internal implementation? → `_internal/`

## Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=escape

# Specific file
pytest tests/test_inventory.py

# Pattern match
pytest -k "test_bank"
```

### Test Pattern

Use dependency injection for testing:

```python
from escape.tabs.inventory import Inventory
from unittest.mock import Mock

def test_get_items():
    mock_client = Mock()
    mock_client.cache.get_item_container.return_value = [...]

    inventory = Inventory.__new__(Inventory)
    inventory.client = mock_client

    items = inventory.get_items()
    assert len(items) == 5
```

## Pull Request Process

1. Update documentation if you changed APIs
2. Add tests for new functionality
3. Ensure all tests pass: `pytest`
4. Ensure linting passes: `ruff check .`
5. Ensure formatting is correct: `ruff format --check .`
6. Use conventional commit format for PR title

### PR Title Examples

```
feat: add support for quest tracking
fix: resolve memory leak in event listener
docs: improve bank interface examples
```

## Pre-commit Checklist

Before submitting:

- [ ] Code follows PEP 8 naming conventions (snake_case for functions)
- [ ] All tests pass
- [ ] Pre-commit hooks pass (`ruff check` and `ruff format`)
- [ ] Commit messages follow conventional commits
- [ ] Type hints are included
- [ ] Docstrings use Google style
- [ ] No breaking changes (or clearly marked with `!`)

## Reporting Bugs

Use GitHub Issues with:

1. **Description**: Clear description of the bug
2. **Reproduction**: Steps to reproduce
3. **Expected behavior**: What should happen
4. **Actual behavior**: What actually happens
5. **Environment**: Python version, OS, escape version

## Feature Requests

Open an issue with:

1. **Use case**: Why is this needed?
2. **Proposed solution**: How should it work?
3. **API design**: Suggested function signatures

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

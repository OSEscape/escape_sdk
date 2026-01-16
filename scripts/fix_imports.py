#!/usr/bin/env python3
"""
Fix import paths to match new escape structure.

Old structure: escape/osrs/*, escape/runeliteBridge/*
New structure: escape/tabs/*, escape/_internal/*, etc.
"""

import re
from pathlib import Path
from typing import List, Tuple

from escape._internal.logger import logger

# Mapping of old import paths to new paths
IMPORT_REPLACEMENTS = {
    # Old relative imports from nested structure
    r"from \.\.\.globals import": "from escape.globals import",
    r"from \.\.\.runeliteBridge import": "from escape._internal import",
    r"from \.\.\.runeliteBridge\.": "from escape._internal.",
    r"from \.\.\.utils\.": "from escape.utilities.",
    r"from \.\.\.resources import": "from escape.resources import",
    r"from \.\.\.resources\.": "from escape.resources.",
    r"from \.\.\.io\.": "from escape.input.",
    r"from \.\.\.osrs\.": "from escape.",  # Remove osrs prefix
    # Fix specific paths
    r"from \.\.globals import": "from escape.globals import",
    r"from \.runeliteBridge import": "from escape._internal import",
    r"from \.runeliteBridge\.": "from escape._internal.",
    # Fix incorrect src imports
    r"from src\.utils\.": "from escape.utilities.",
    # Fix function names (snake_case to camelCase)
    r"\bget_client\b": "getClient",
    r"\bget_api\b": "getApi",
    r"\bget_item_name\b": "getItemName",
    r"\bget_formatted_item_name\b": "getFormattedItemName",
    r"\bgame_state\b": "gameState",
}


def fixImportsInFile(filepath: Path) -> Tuple[int, List[str]]:
    """
    Fix imports in a single Python file.

    Args:
        filepath: Path to Python file

    Returns:
        Tuple of (number of changes, list of change descriptions)
    """
    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.read()

        original_content = content
        changes = []

        # Apply all replacements
        for old_pattern, new_pattern in IMPORT_REPLACEMENTS.items():
            matches = re.findall(old_pattern, content)
            if matches:
                content = re.sub(old_pattern, new_pattern, content)
                changes.append(f"  {old_pattern} → {new_pattern} ({len(matches)} occurrences)")

        # Only write if changes were made
        if content != original_content:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            return (len(changes), changes)

        return (0, [])

    except Exception as e:
        logger.error(f"Error processing {filepath}: {e}")
        return (0, [])


def main():
    """Fix imports across all Python files in escape."""
    escape_dir = Path(__file__).parent.parent / "escape"

    if not escape_dir.exists():
        logger.error(f"Error: {escape_dir} not found")
        return 1

    python_files = list(escape_dir.rglob("*.py"))
    logger.info(f"Found {len(python_files)} Python files")
    print("=" * 60)

    total_files_changed = 0
    total_changes = 0

    for filepath in sorted(python_files):
        num_changes, changes = fixImportsInFile(filepath)

        if num_changes > 0:
            total_files_changed += 1
            total_changes += num_changes
            logger.info(f"\n {filepath.relative_to(escape_dir.parent)}")
            for change in changes:
                print(change)

    print("\n" + "=" * 60)
    logger.success(f"Fixed {total_changes} imports in {total_files_changed} files")

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())

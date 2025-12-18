#!/usr/bin/env python3
"""
Rename escape_sdk SDK to escape_sdk.

Usage:
    python tools/rename_sdk.py --dry-run    # Preview changes
    python tools/rename_sdk.py              # Apply changes
    python tools/rename_sdk.py --verbose    # Show all replacements
"""

import argparse
import os
import shutil
from pathlib import Path
from typing import List, Tuple


# Replacement patterns (longest/most specific first to avoid partial matches)
REPLACEMENTS = [
    # GitHub URLs (most specific first)
    ("https://github.com/osescape/escape_sdk", "https://github.com/osescape/escape_sdk"),
    ("github.com/osescape/escape_sdk", "github.com/osescape/escape_sdk"),
    ("osescape/escape_sdk", "osescape/escape_sdk"),
    # Organization/Team names
    ("Escape Team", "Escape Team"),
    ("Escape", "Escape"),
    # Library name
    ("Escape SDK", "Escape SDK"),
    # Package name (lowercase)
    ("escape_sdk", "escape_sdk"),
]

# Directories and patterns to skip
SKIP_PATTERNS = [
    "/.git/",
    "/__pycache__/",
    ".pyc",
    "/dist/",
    "/build/",
    ".egg-info/",
    "/generated/",
    "/.venv/",
    "/venv/",
    "/.mypy_cache/",
    "/.pytest_cache/",
    "/.ruff_cache/",
]

# File extensions to process
TEXT_EXTENSIONS = {
    ".py", ".pyi", ".toml", ".json", ".yaml", ".yml",
    ".md", ".rst", ".txt", ".in", ".cfg", ".ini",
    ".sh", ".bash",
}

# Files without extensions to process
TEXT_FILES = {
    "Makefile",
    "Dockerfile",
    ".gitignore",
    ".dockerignore",
    ".releaserc.json",
    ".pre-commit-config.yaml",
}


def should_skip(path: Path) -> bool:
    """Check if path should be skipped."""
    path_str = str(path)
    for pattern in SKIP_PATTERNS:
        if pattern in path_str:
            return True
    return False


def is_text_file(path: Path) -> bool:
    """Check if file should be processed."""
    if path.name in TEXT_FILES:
        return True
    if path.suffix in TEXT_EXTENSIONS:
        return True
    return False


def find_project_root() -> Path:
    """Find project root by looking for pyproject.toml."""
    current = Path(__file__).resolve().parent
    while current != current.parent:
        if (current / "pyproject.toml").exists():
            return current
        current = current.parent
    raise RuntimeError("Could not find project root (no pyproject.toml found)")


def find_text_files(root: Path) -> List[Path]:
    """Find all text files to process."""
    files = []
    for path in root.rglob("*"):
        if path.is_file() and not should_skip(path) and is_text_file(path):
            files.append(path)
    return sorted(files)


def apply_replacements(content: str, replacements: List[Tuple[str, str]]) -> Tuple[str, int]:
    """Apply all replacements and return (new_content, count)."""
    total_count = 0
    for old, new in replacements:
        count = content.count(old)
        if count > 0:
            content = content.replace(old, new)
            total_count += count
    return content, total_count


def verify_no_shadow_remaining(root: Path, verbose: bool = False) -> dict:
    """
    Count remaining 'shadow' occurrences (case-insensitive) after rename.

    Returns a dict with:
        - files_with_shadow: number of files containing 'shadow'
        - total_occurrences: total count of 'shadow' matches
        - file_list: list of file paths containing 'shadow'
    """
    import re

    pattern = re.compile(r"shadow", re.IGNORECASE)
    files_with_shadow = []
    total_occurrences = 0

    print("\nVerifying no 'shadow' occurrences remain...")

    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if should_skip(path):
            continue
        if not is_text_file(path):
            continue

        try:
            content = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, PermissionError):
            continue

        matches = pattern.findall(content)
        if matches:
            count = len(matches)
            total_occurrences += count
            rel_path = str(path.relative_to(root))
            files_with_shadow.append(rel_path)
            if verbose:
                print(f"  Found {count} 'shadow' in: {rel_path}")

    return {
        "files_with_shadow": len(files_with_shadow),
        "total_occurrences": total_occurrences,
        "file_list": files_with_shadow,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Rename escape_sdk SDK to escape_sdk",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview changes without modifying files")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Show each file being modified")
    parser.add_argument("--backup", action="store_true",
                        help="Create .bak files before modifying")

    args = parser.parse_args()

    project_root = find_project_root()
    print(f"Project root: {project_root}")

    if args.verbose:
        print("\nReplacement patterns:")
        for old, new in REPLACEMENTS:
            print(f"  {old} -> {new}")

    # Phase 1: Find all files to process
    files = find_text_files(project_root)
    print(f"\nFound {len(files)} text files to scan")

    # Phase 2: Process each file
    stats = {"files_modified": 0, "replacements": 0, "files_scanned": 0}

    for file_path in files:
        stats["files_scanned"] += 1
        try:
            content = file_path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, PermissionError) as e:
            if args.verbose:
                print(f"  Skipped (error): {file_path} - {e}")
            continue

        new_content, count = apply_replacements(content, REPLACEMENTS)

        if count > 0:
            stats["files_modified"] += 1
            stats["replacements"] += count

            rel_path = file_path.relative_to(project_root)
            if args.verbose:
                print(f"  {rel_path}: {count} replacement(s)")

            if not args.dry_run:
                if args.backup:
                    backup_path = file_path.with_suffix(file_path.suffix + ".bak")
                    shutil.copy2(file_path, backup_path)
                file_path.write_text(new_content, encoding="utf-8")

    # Phase 3: Rename package directory (escape_sdk/ -> escape_sdk/)
    old_pkg_dir = project_root / "escape_sdk"
    new_pkg_dir = project_root / "escape_sdk"

    print("\nDirectory renames:")
    if old_pkg_dir.exists():
        print(f"  escape_sdk/ -> escape_sdk/")
        if not args.dry_run:
            old_pkg_dir.rename(new_pkg_dir)
    else:
        print(f"  escape_sdk/ directory not found (already renamed?)")

    # Phase 4: Verify no 'shadow' occurrences remain
    shadow_stats = verify_no_shadow_remaining(project_root, args.verbose)

    # Phase 5: Print summary
    print("\n" + "=" * 50)
    if args.dry_run:
        print("DRY RUN - No changes made")
    else:
        print("Changes applied")
    print("=" * 50)
    print(f"Files scanned:  {stats['files_scanned']}")
    print(f"Files modified: {stats['files_modified']}")
    print(f"Replacements:   {stats['replacements']}")

    # Print shadow verification results
    print(f"\n'shadow' verification:")
    print(f"  Files with 'shadow': {shadow_stats['files_with_shadow']}")
    print(f"  Total occurrences:   {shadow_stats['total_occurrences']}")
    if shadow_stats['files_with_shadow'] > 0 and args.verbose:
        print("  Files:")
        for f in shadow_stats['file_list'][:20]:  # Show first 20
            print(f"    - {f}")
        if len(shadow_stats['file_list']) > 20:
            print(f"    ... and {len(shadow_stats['file_list']) - 20} more")

    if not args.dry_run:
        print("\nNext steps:")
        print("  1. Rename project directory manually: mv escape_sdk escape_sdk")
        print("  2. cd escape_sdk")
        print("  3. python -c 'import escape_sdk'  # Verify import works")
        print("  4. Run tests if available")


if __name__ == "__main__":
    main()

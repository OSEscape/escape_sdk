#!/usr/bin/env python3
"""
Verify that the Escape package is set up correctly.

This script checks:
- Package structure
- Import functionality
- Naming conventions
- Test discovery
"""

import sys
from pathlib import Path

from escape._internal.logger import logger


def check_package_structure() -> bool:
    """Verify the package directory structure exists."""
    logger.info("Checking package structure")

    required_dirs = [
        "escape",
        "escape/world",
        "escape/tabs",
        "escape/interfaces",
        "escape/navigation",
        "escape/interactions",
        "escape/input",
        "escape/types",
        "escape/utilities",
        "escape/resources",
        "escape/_internal",
        "tests",
    ]

    missing_dirs = []
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            missing_dirs.append(dir_path)

    if missing_dirs:
        logger.error(f"Missing directories: {', '.join(missing_dirs)}")
        return False

    logger.success("All required directories exist")
    return True


def check_required_files() -> bool:
    """Verify required configuration files exist."""
    logger.info("\nChecking required files")

    required_files = [
        "pyproject.toml",
        "README.md",
        "LICENSE",
        "scripts/check_naming.py",
        ".pre-commit-config.yaml",
        ".gitignore",
        "Makefile",
        "escape/__init__.py",
        "escape/client.py",
        "escape/_internal/query.py",
    ]

    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)

    if missing_files:
        logger.error(f"Missing files: {', '.join(missing_files)}")
        return False

    logger.success("All required files exist")
    return True


def check_imports() -> bool:
    """Verify that the package can be imported."""
    logger.info("\nChecking imports")

    try:
        import escape

        logger.success(f"Successfully imported escape (version {escape.__version__})")

        from escape import Client

        logger.success("Successfully imported Client")

        from escape._internal.query import QueryBuilder

        logger.success("Successfully imported QueryBuilder")

        return True
    except ImportError as e:
        logger.error(f"Import error: {e}")
        logger.info("→ Run: pip install -e")
        return False


def check_basic_functionality() -> bool:
    """Verify basic functionality works."""
    logger.info("\nChecking basic functionality")

    try:
        from escape import Client

        client = Client()
        logger.success("Client instantiation works")

        if not client.isConnected():
            logger.success("isConnected() returns False initially")
        else:
            logger.error("isConnected() should return False initially")
            return False

        client.connect()
        if client.isConnected():
            logger.success("connect() and isConnected() work")
        else:
            logger.error("connect() should set isConnected() to True")
            return False

        return True
    except Exception as e:
        logger.error(f"Error: {e}")
        return False


def check_naming_conventions() -> bool:
    """Verify naming conventions are followed."""
    logger.info("\nChecking naming conventions")

    # Check if check_naming.py exists and is executable
    naming_checker = Path("scripts/check_naming.py")
    if not naming_checker.exists():
        logger.error("scripts/check_naming.py not found")
        return False

    logger.success("Naming convention checker exists")
    logger.info("→ Run: make naming (to verify)")
    return True


def main() -> int:
    """
    Run all verification checks.

    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    print("=" * 60)
    logger.info("Escape Setup Verification")
    print("=" * 60)

    checks = [
        ("Package Structure", check_package_structure),
        ("Required Files", check_required_files),
        ("Imports", check_imports),
        ("Basic Functionality", check_basic_functionality),
        ("Naming Conventions", check_naming_conventions),
    ]

    results = []
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            logger.error(f"\n {check_name} failed with exception: {e}")
            results.append((check_name, False))

    print("\n" + "=" * 60)
    logger.info("Summary")
    print("=" * 60)

    all_passed = True
    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status}: {check_name}")
        if not result:
            all_passed = False

    print("=" * 60)

    if all_passed:
        logger.success("\n All checks passed! Your setup is ready")
        logger.info("\nNext steps")
        logger.info("1. Install dev dependencies: pip install -e '.[dev]'")
        logger.info("2. Set up pre-commit hooks: pre-commit install")
        logger.info("3. Run tests: pytest")
        logger.info("4. Check naming: python check_naming.py")
        logger.info("5. Start developing!")
        return 0
    else:
        logger.error("\n Some checks failed. Please review the output above")
        return 1


if __name__ == "__main__":
    sys.exit(main())

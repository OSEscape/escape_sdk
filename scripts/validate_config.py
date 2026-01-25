#!/usr/bin/env python3
"""Validate linter config integrity.

Prevents drift in ruff, basedpyright, and skylos configurations.
If CI fails here, fix the actual code - don't modify the linter rules.

Industry practice: config drift detection in CI/CD pipelines.
References: dev.to/dev264, validate-pyproject, policyascode.dev
"""

import hashlib
import sys
import tomllib
from pathlib import Path

# Approved configuration hashes - update only with team approval
APPROVED_RUFF_IGNORE_HASH = "198550b4d663"
APPROVED_BASEDPYRIGHT_MODE = "basic"
APPROVED_SKYLOS_STRICT = False


def main() -> int:
    """Validate pyproject.toml linter sections haven't drifted."""
    config = tomllib.loads(Path("pyproject.toml").read_text())
    errors = []

    # Validate ruff ignore list
    ruff_ignore = config.get("tool", {}).get("ruff", {}).get("lint", {}).get("ignore", [])
    current_hash = hashlib.sha256(str(sorted(ruff_ignore)).encode()).hexdigest()[:12]
    if current_hash != APPROVED_RUFF_IGNORE_HASH:
        errors.append(
            f"ruff ignore rules modified!\n"
            f"  Expected hash: {APPROVED_RUFF_IGNORE_HASH}\n"
            f"  Current hash:  {current_hash}\n"
            f"  Current rules: {sorted(ruff_ignore)}"
        )

    # Validate basedpyright mode
    bp_mode = config.get("tool", {}).get("basedpyright", {}).get("typeCheckingMode", "")
    if bp_mode != APPROVED_BASEDPYRIGHT_MODE:
        errors.append(
            f"basedpyright mode modified!\n"
            f"  Expected: {APPROVED_BASEDPYRIGHT_MODE}\n"
            f"  Current:  {bp_mode}"
        )

    # Validate skylos strict mode
    skylos_strict = config.get("tool", {}).get("skylos", {}).get("gate", {}).get("strict", None)
    if skylos_strict != APPROVED_SKYLOS_STRICT:
        errors.append(
            f"skylos strict mode modified!\n"
            f"  Expected: {APPROVED_SKYLOS_STRICT}\n"
            f"  Current:  {skylos_strict}"
        )

    if errors:
        print("ERROR: Linter config validation failed!\n")
        print("Fix the actual code issues - don't modify linter rules.\n")
        for error in errors:
            print(f"  {error}\n")
        print("If config change is intentional, update scripts/validate_config.py")
        return 1

    print("Linter config validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())

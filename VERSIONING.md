# Versioning and Release Process

ShadowLib uses automated semantic versioning with conventional commits.

## How It Works

### Commit Format Determines Version Bump

```bash
# PATCH bump (1.0.0 → 1.0.1)
fix: resolve inventory crash
perf: optimize cache lookups
docs: update API documentation

# MINOR bump (1.0.0 → 1.1.0)
feat: add new equipment module
feat(bank): implement deposit all

# MAJOR bump (1.0.0 → 2.0.0)
feat!: redesign API structure
# OR with footer:
feat: redesign API

BREAKING CHANGE: getItems() now returns Item objects instead of IDs
```

### Automated Release Workflow

When you push to `main`:

1. **Semantic-release analyzes commits** - determines version bump
2. **Updates version files** - `pyproject.toml`, `shadowlib/__init__.py`, `CHANGELOG.md`
3. **Creates git tag and GitHub release** - with release notes
4. **Builds and publishes to PyPI** - automatically

## Workflow

```bash
# 1. Make changes
git checkout -b feat/new-feature

# 2. Commit with conventional format
git commit -m "feat(module): add new functionality"

# 3. Push to main (via PR or directly)
git push origin main

# 4. Automation handles the rest!
```

## Version Synchronization

The release workflow ensures versions are synchronized:

1. Commit triggers workflow
2. Semantic-release determines new version
3. Updates pyproject.toml and __init__.py
4. Builds package with new version
5. Publishes to PyPI

## Best Practices

1. **Always use conventional commits** on main branch
2. **Test locally** before pushing to main
3. **Let automation handle versioning** - don't manually edit version numbers
4. **Monitor GitHub Actions** after pushing to main

## References

- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)
- [Semantic Release](https://github.com/semantic-release/semantic-release)

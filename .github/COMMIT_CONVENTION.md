# Commit Message Convention - Quick Reference

## Format

```
<type>(<scope>): <subject>
```

## Types & Version Impact

| Type | Version Bump | Use When |
|------|--------------|----------|
| `feat` | **Minor** (0.1.0 → 0.2.0) | Adding new features |
| `fix` | **Patch** (0.1.0 → 0.1.1) | Fixing bugs |
| `perf` | **Patch** (0.1.0 → 0.1.1) | Performance improvements |
| `docs` | **Patch** (0.1.0 → 0.1.1) | Documentation changes |
| `refactor` | **Patch** (0.1.0 → 0.1.1) | Code refactoring |
| `style` | **Patch** (0.1.0 → 0.1.1) | Code formatting |
| `test` | None | Adding/updating tests |
| `build` | None | Build system changes |
| `ci` | None | CI/CD changes |
| `chore` | None | Maintenance tasks |
| `revert` | Depends | Reverting changes |

## Breaking Changes

Add `!` after type or `BREAKING CHANGE:` in footer → **Major** (0.1.0 → 1.0.0)

```bash
feat!: redesign API
# or
feat: redesign API

BREAKING CHANGE: API completely redesigned
```

## Examples

```bash
# Feature (minor bump)
feat(inventory): add getItemsByName method
feat(bank): implement deposit all functionality

# Bug fix (patch bump)
fix(navigation): resolve pathfinding crash
fix(client): prevent memory leak in event listener

# Performance (patch bump)
perf(cache): optimize ground item lookups

# Documentation (patch bump)
docs(readme): add installation guide
docs(api): improve docstrings for inventory module

# Refactor (patch bump)
refactor(types): simplify Position class

# Style (patch bump)
style: format code with ruff

# No version bump
test(inventory): add tests for isEmpty method
ci: update GitHub Actions workflow
chore: update dependencies

# Breaking change (major bump)
feat(client)!: make connect() async

BREAKING CHANGE: connect() now returns Promise and must be awaited

# With scope
fix(bank): correct item counting logic
feat(tabs/skills): add experience tracking

# Multi-line
feat(ge): add Grand Exchange support

Implements buy/sell orders, price checking, and
item search for the Grand Exchange interface.

Closes #42
```

## Scopes (Optional)

Use the module/area being changed:

- `inventory`, `bank`, `equipment`, `skills`
- `navigation`, `pathfinding`
- `client`, `api`, `cache`
- `types`, `utilities`, `geometry`
- `tests`, `docs`, `ci`

## Rules

✅ **DO:**
- Start subject with lowercase
- Use present tense ("add" not "added")
- Keep subject under 100 characters
- Add body for complex changes
- Reference issues (`Closes #123`)

❌ **DON'T:**
- End subject with period
- Use past tense
- Be vague ("fix stuff", "update code")
- Commit unrelated changes together

## Automation

Commits trigger automatic:
- ✅ Version bumping
- ✅ CHANGELOG.md generation
- ✅ GitHub release creation
- ✅ PyPI publishing (on main branch)

## Validation

Commits are validated by:
- Pre-commit hooks (on local commits)
- Commitlint workflow (on push/PR)
- PR title checker (for pull requests)

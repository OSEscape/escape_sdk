# Changelog

All notable changes to this project will be documented in this file. See [Conventional Commits](https://conventionalcommits.org) for commit guidelines.

## [3.4.0](https://github.com/osescape/escape_sdk/compare/v3.3.0...v3.4.0) (2025-12-16)

### Features

* add drawing module, geometry enhancements, and GeneralInterface ([292154a](https://github.com/osescape/escape_sdk/commit/292154a024aa6f3aa37dfb5bc889deacb18cc59a))
* Add Quad geometry type and projection utilities ([c9aa6eb](https://github.com/osescape/escape_sdk/commit/c9aa6eb75b46f814d90746ca2b4950aefe5f0bff))
* **interfaces:** add scrollbox support to GeneralInterface ([1bfe2d7](https://github.com/osescape/escape_sdk/commit/1bfe2d7b6b0ee47c3be0713dbc8397b51c5adeca))
* **navigation:** implement Walker class for smart pathfinding and tile clicking ([105cb60](https://github.com/osescape/escape_sdk/commit/105cb6022f42f59e58f3ab11a1ebc535b0e2b4e2))
* update EventCache to retrieve active interfaces and refactor StateBuilder for widget management ([0351a0d](https://github.com/osescape/escape_sdk/commit/0351a0d8d08f608efee535fcc5d21d4d27737ad8))

### Bug Fixes

* format code and fix consumeMenuClickedState bug ([fd7b4bd](https://github.com/osescape/escape_sdk/commit/fd7b4bddf10906818461a03bb3e768d9493a9c1d))

### Refactoring

* **interfaces:** simplify scrollbox and add Box.contains(Box) ([a967e2d](https://github.com/osescape/escape_sdk/commit/a967e2d52a68d5e5aeff36b46ff6007370c4c17c))

## [3.3.0](https://github.com/osescape/escape_sdk/compare/v3.2.1...v3.3.0) (2025-12-04)

### Features

* unify item lookup methods to accept ID or name ([d78e213](https://github.com/osescape/escape_sdk/commit/d78e2131c83e46ea2b4885f4aa7da5c7467c1893))

## [3.2.1](https://github.com/osescape/escape_sdk/compare/v3.2.0...v3.2.1) (2025-12-04)

### Bug Fixes

* prevent ItemContainer.__init__ from running in Bank singleton ([0978036](https://github.com/osescape/escape_sdk/commit/0978036263a4946c178b358e6f07690a34fb631c))

## [3.2.0](https://github.com/osescape/escape_sdk/compare/v3.1.1...v3.2.0) (2025-12-04)

### Features

* implement singleton pattern for RuneLiteAPI and add getOpenWidgets method to EventCache ([412613f](https://github.com/osescape/escape_sdk/commit/412613f3cc60a0e9c2ced9928c9295dc952b71a5))

### Bug Fixes

* remove debug prints from state_builder that may cause import issues ([7c367ed](https://github.com/osescape/escape_sdk/commit/7c367ed061cfaf4ffec793b0503f53909640e13e))

## [3.1.1](https://github.com/osescape/escape_sdk/compare/v3.1.0...v3.1.1) (2025-12-04)

### Bug Fixes

* resolve warmup deadlock by pre-importing constants ([2bc52c8](https://github.com/osescape/escape_sdk/commit/2bc52c8fe972b87f0519a83230e1d4e2c96188dc))

## [3.1.0](https://github.com/osescape/escape_sdk/compare/v3.0.0...v3.1.0) (2025-12-04)

### Features

* add lazy-loaded interface ID to name lookup ([0aca0a0](https://github.com/osescape/escape_sdk/commit/0aca0a0a023517ac9b96478650fc26cc573e85dd))

### Bug Fixes

* wait for event cache warmup after singleton creation ([4e844a4](https://github.com/osescape/escape_sdk/commit/4e844a43cb0b61c0b23087b647792504304b4e82))

## [3.0.0](https://github.com/osescape/escape_sdk/compare/v2.2.2...v3.0.0) (2025-12-04)

### BREAKING CHANGES

* Module access patterns have changed significantly.

- Convert Client, all tabs, Bank, Menu, Mouse, Keyboard, RuneLite,
  GroundItems, Pathfinder, and Player to singletons using __new__ + _init()
- Add module-level singleton exports (e.g., `from escape_sdk.tabs.inventory import inventory`)
- Update namespace classes (Tabs, Interfaces, etc.) to return singleton instances
- Replace self.client pattern with `from escape_sdk.client import client` imports
- Fix circular import issue by duplicating SKILL_NAMES constant
- Fix event consumer deadlock by not waiting for warmup during module import

Migration guide:
- Old: `client = Client(); client.tabs.inventory.getItems()`
- New: `from escape_sdk.tabs.inventory import inventory; inventory.getItems()`
- Or: `from escape_sdk.client import client; client.tabs.inventory.getItems()`

### Features

* enhance event cache initialization and menu interaction methods; improve inventory slot handling and timing utilities ([9848daa](https://github.com/osescape/escape_sdk/commit/9848daa42d52a98493e00c4d1929295e4f5b38bf))

### Refactoring

* convert modules to singleton pattern ([2e48446](https://github.com/osescape/escape_sdk/commit/2e484464daa6d03a4182fb7eba3e9d345387c621))

## [2.2.2](https://github.com/osescape/escape_sdk/compare/v2.2.1...v2.2.2) (2025-11-25)

### Bug Fixes

* add type stubs for varps and objects modules ([d06696b](https://github.com/osescape/escape_sdk/commit/d06696befee34325727de299ff3bce2ee4f57605))
* update client.pyi stub to include resources namespace ([b0b3e45](https://github.com/osescape/escape_sdk/commit/b0b3e454075b5ed53077d28a6c71c29682944797))
* use module imports for resources type hints ([3a06dd3](https://github.com/osescape/escape_sdk/commit/3a06dd39b378f968802cd350a70fd7773009f503))

### Styles

* fix linting and formatting issues ([0d4fe16](https://github.com/osescape/escape_sdk/commit/0d4fe164d109fdaa87acb169eb7f38c1914978a6))

### Refactoring

* streamline resources module and merge cache utilities ([0280441](https://github.com/osescape/escape_sdk/commit/0280441b41c0b82105a6d052050d21bf6598142f))

## [2.2.1](https://github.com/osescape/escape_sdk/compare/v2.2.0...v2.2.1) (2025-11-25)

### Refactoring

* streamline resources module and merge cache utilities ([3e619c6](https://github.com/osescape/escape_sdk/commit/3e619c64dbc92efdc87c7fdcf2ceaccfb54ee882))

## [2.2.0](https://github.com/osescape/escape_sdk/compare/v2.1.0...v2.2.0) (2025-11-24)

### Features

* add namespace architecture and input system ([6c6b5fc](https://github.com/osescape/escape_sdk/commit/6c6b5fcc44925ad9b429e2e6095abad974a97d97))

### Styles

* apply ruff formatting and fix type hints ([88475e7](https://github.com/osescape/escape_sdk/commit/88475e7e9e5cce9614238dd69c64082b0e156c85))
* fix linting issues in input modules ([6beeacc](https://github.com/osescape/escape_sdk/commit/6beeaccbd3bece4e69fc656ae9e60ad655bfaa0d))
* merge formatting fixes from development ([ffb5e0e](https://github.com/osescape/escape_sdk/commit/ffb5e0ebd7a360a5032b93bb4b15f08084922ace))

## [2.1.0](https://github.com/osescape/escape_sdk/compare/v2.0.7...v2.1.0) (2025-11-24)

### Features

* **types:** add Widget mask builder with IDE autocomplete support ([1535e5e](https://github.com/osescape/escape_sdk/commit/1535e5eccae2ca6d7b3076d89073916cc5792822))

### Styles

* format check_naming.py with ruff ([26f7d1a](https://github.com/osescape/escape_sdk/commit/26f7d1a724778f88ad798e5b7ffeeee1b94728ef))

### Refactoring

* consolidate packed position utilities and improve event consumer warmup ([97e952e](https://github.com/osescape/escape_sdk/commit/97e952e66829a5190041153a2ca02c0000b42da7))

## [2.0.7](https://github.com/osescape/escape_sdk/compare/v2.0.6...v2.0.7) (2025-11-23)

### Refactoring

* **resources:** unify varps and objects into single GameDataResource ([46ce387](https://github.com/osescape/escape_sdk/commit/46ce3874e0d3295cd0507846026b5b9023c963e7))

## [2.0.6](https://github.com/osescape/escape_sdk/compare/v2.0.5...v2.0.6) (2025-11-23)

### Bug Fixes

* **resources:** prevent duplicate downloads of shared files ([3abcb56](https://github.com/osescape/escape_sdk/commit/3abcb56c1a4432fbf6132e916dd2c05d03e1dfc4))

## [2.0.5](https://github.com/osescape/escape_sdk/compare/v2.0.4...v2.0.5) (2025-11-23)

### Bug Fixes

* **query:** correct variable name in QueryRef.__getattr__ ([08e1021](https://github.com/osescape/escape_sdk/commit/08e10211073a95412c041623e67d8dac447720bc))

## [2.0.4](https://github.com/osescape/escape_sdk/compare/v2.0.3...v2.0.4) (2025-11-23)

### Refactoring

* remove escape_sdk/generated/ folder completely ([5a0a2ab](https://github.com/osescape/escape_sdk/commit/5a0a2ab41b47cc08a34b0011387f90f7b33036c9))

## [2.0.3](https://github.com/osescape/escape_sdk/compare/v2.0.2...v2.0.3) (2025-11-23)

### Documentation

* add release notes for v2.0.2 clean slate ([4e494c1](https://github.com/osescape/escape_sdk/commit/4e494c18222d1d7c20abd28a9f75a57365fd0d4b))

## 1.0.0 (2025-11-23)

### BREAKING CHANGES

* Generated files and resources now stored in user cache
directory instead of package directory. Old data/ folder no longer used.

Changes:
- Add centralized CacheManager for path management
- Add dynamic loader for generated modules from cache
- Update all components to use cache paths (resources, scraper, updater)
- Fix circular imports with lazy-loading in query_builder
- Update proxy generator to use absolute imports
- Remove 7.5MB of generated files from package (84% size reduction)
- Package size: 1.8MB -> 296KB

Cache structure:
~/.cache/escape_sdk/
├── generated/ (proxy classes, constants)
└── data/ (objects DB, varps, API data)

First import automatically downloads and generates all required files.

Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>

### Features

* migrate to XDG cache directory for generated files and resources ([c369c31](https://github.com/osescape/escape_sdk/commit/c369c319b83c87112a4619060f70b7a782604073))

### Bug Fixes

* **ci:** correct version sync in release workflow ([5b7c794](https://github.com/osescape/escape_sdk/commit/5b7c794edd34866344889040e95f814ae62bff27))
* **ci:** enable tag fetching for semantic-release ([6bc83f1](https://github.com/osescape/escape_sdk/commit/6bc83f194220c30bb3a872961cfa1cb5d9cb5d3b))
* **ci:** prevent sed from modifying ruff target-version ([08b4b07](https://github.com/osescape/escape_sdk/commit/08b4b07179f8150ae77887629935011ad923f018))
* **lint:** add ignores for Python 3.12+ upgrade compatibility ([25bc9b3](https://github.com/osescape/escape_sdk/commit/25bc9b33ff373493c0b57005fd5419876cbc2df6))
* update project URLs and ruff version ([077da2d](https://github.com/osescape/escape_sdk/commit/077da2d47fbd56128ef3e8bb007c102444e08fe5))
* **version:** restore version to 2.0.1 after incorrect release ([1253aad](https://github.com/osescape/escape_sdk/commit/1253aada19d4e235dc4db14ad35548b791658298))

### Documentation

* add commit convention quick reference guide ([f23d39e](https://github.com/osescape/escape_sdk/commit/f23d39e7f12daaa9fdc887dc550d3495cb522970))

### Refactoring

* **ci:** consolidate workflows and upgrade to Python 3.12+ ([c3283b5](https://github.com/osescape/escape_sdk/commit/c3283b536478f8d3c612f2f16fcd58f6dd37e784))

### CI/CD

* add semantic-release and quality check workflows ([51d420c](https://github.com/osescape/escape_sdk/commit/51d420c36510d7d3c54f573ee32bea64dfaf45e1))

## [1.0.1](https://github.com/osescape/escape_sdk/compare/v1.0.0...v1.0.1) (2025-11-23)

### Bug Fixes

* **ci:** enable tag fetching for semantic-release ([6bc83f1](https://github.com/osescape/escape_sdk/commit/6bc83f194220c30bb3a872961cfa1cb5d9cb5d3b))

## 1.0.0 (2025-11-23)

### BREAKING CHANGES

* Generated files and resources now stored in user cache
directory instead of package directory. Old data/ folder no longer used.

Changes:
- Add centralized CacheManager for path management
- Add dynamic loader for generated modules from cache
- Update all components to use cache paths (resources, scraper, updater)
- Fix circular imports with lazy-loading in query_builder
- Update proxy generator to use absolute imports
- Remove 7.5MB of generated files from package (84% size reduction)
- Package size: 1.8MB -> 296KB

Cache structure:
~/.cache/escape_sdk/
├── generated/ (proxy classes, constants)
└── data/ (objects DB, varps, API data)

First import automatically downloads and generates all required files.

Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>

### Features

* migrate to XDG cache directory for generated files and resources ([c369c31](https://github.com/osescape/escape_sdk/commit/c369c319b83c87112a4619060f70b7a782604073))

### Bug Fixes

* **ci:** correct version sync in release workflow ([5b7c794](https://github.com/osescape/escape_sdk/commit/5b7c794edd34866344889040e95f814ae62bff27))
* **ci:** prevent sed from modifying ruff target-version ([08b4b07](https://github.com/osescape/escape_sdk/commit/08b4b07179f8150ae77887629935011ad923f018))
* **lint:** add ignores for Python 3.12+ upgrade compatibility ([25bc9b3](https://github.com/osescape/escape_sdk/commit/25bc9b33ff373493c0b57005fd5419876cbc2df6))
* update project URLs and ruff version ([077da2d](https://github.com/osescape/escape_sdk/commit/077da2d47fbd56128ef3e8bb007c102444e08fe5))

### Documentation

* add commit convention quick reference guide ([f23d39e](https://github.com/osescape/escape_sdk/commit/f23d39e7f12daaa9fdc887dc550d3495cb522970))

### Refactoring

* **ci:** consolidate workflows and upgrade to Python 3.12+ ([c3283b5](https://github.com/osescape/escape_sdk/commit/c3283b536478f8d3c612f2f16fcd58f6dd37e784))

### CI/CD

* add semantic-release and quality check workflows ([51d420c](https://github.com/osescape/escape_sdk/commit/51d420c36510d7d3c54f573ee32bea64dfaf45e1))

## 1.0.0 (2025-11-23)

### BREAKING CHANGES

* Generated files and resources now stored in user cache
directory instead of package directory. Old data/ folder no longer used.

Changes:
- Add centralized CacheManager for path management
- Add dynamic loader for generated modules from cache
- Update all components to use cache paths (resources, scraper, updater)
- Fix circular imports with lazy-loading in query_builder
- Update proxy generator to use absolute imports
- Remove 7.5MB of generated files from package (84% size reduction)
- Package size: 1.8MB -> 296KB

Cache structure:
~/.cache/escape_sdk/
├── generated/ (proxy classes, constants)
└── data/ (objects DB, varps, API data)

First import automatically downloads and generates all required files.

Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>

### Features

* migrate to XDG cache directory for generated files and resources ([c369c31](https://github.com/osescape/escape_sdk/commit/c369c319b83c87112a4619060f70b7a782604073))

### Bug Fixes

* **ci:** correct version sync in release workflow ([5b7c794](https://github.com/osescape/escape_sdk/commit/5b7c794edd34866344889040e95f814ae62bff27))
* **ci:** prevent sed from modifying ruff target-version ([08b4b07](https://github.com/osescape/escape_sdk/commit/08b4b07179f8150ae77887629935011ad923f018))
* **lint:** add ignores for Python 3.12+ upgrade compatibility ([25bc9b3](https://github.com/osescape/escape_sdk/commit/25bc9b33ff373493c0b57005fd5419876cbc2df6))
* update project URLs and ruff version ([077da2d](https://github.com/osescape/escape_sdk/commit/077da2d47fbd56128ef3e8bb007c102444e08fe5))

### Documentation

* add commit convention quick reference guide ([f23d39e](https://github.com/osescape/escape_sdk/commit/f23d39e7f12daaa9fdc887dc550d3495cb522970))

### Refactoring

* **ci:** consolidate workflows and upgrade to Python 3.12+ ([c3283b5](https://github.com/osescape/escape_sdk/commit/c3283b536478f8d3c612f2f16fcd58f6dd37e784))

### CI/CD

* add semantic-release and quality check workflows ([51d420c](https://github.com/osescape/escape_sdk/commit/51d420c36510d7d3c54f573ee32bea64dfaf45e1))

## 1.0.0 (2025-11-23)

### BREAKING CHANGES

* Generated files and resources now stored in user cache
directory instead of package directory. Old data/ folder no longer used.

Changes:
- Add centralized CacheManager for path management
- Add dynamic loader for generated modules from cache
- Update all components to use cache paths (resources, scraper, updater)
- Fix circular imports with lazy-loading in query_builder
- Update proxy generator to use absolute imports
- Remove 7.5MB of generated files from package (84% size reduction)
- Package size: 1.8MB -> 296KB

Cache structure:
~/.cache/escape_sdk/
├── generated/ (proxy classes, constants)
└── data/ (objects DB, varps, API data)

First import automatically downloads and generates all required files.

Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>

### Features

* migrate to XDG cache directory for generated files and resources ([c369c31](https://github.com/osescape/escape_sdk/commit/c369c319b83c87112a4619060f70b7a782604073))

### Bug Fixes

* **ci:** correct version sync in release workflow ([5b7c794](https://github.com/osescape/escape_sdk/commit/5b7c794edd34866344889040e95f814ae62bff27))
* **ci:** prevent sed from modifying ruff target-version ([08b4b07](https://github.com/osescape/escape_sdk/commit/08b4b07179f8150ae77887629935011ad923f018))
* update project URLs and ruff version ([077da2d](https://github.com/osescape/escape_sdk/commit/077da2d47fbd56128ef3e8bb007c102444e08fe5))

### Documentation

* add commit convention quick reference guide ([f23d39e](https://github.com/osescape/escape_sdk/commit/f23d39e7f12daaa9fdc887dc550d3495cb522970))

### CI/CD

* add semantic-release and quality check workflows ([51d420c](https://github.com/osescape/escape_sdk/commit/51d420c36510d7d3c54f573ee32bea64dfaf45e1))

## 1.0.0 (2025-11-23)

### BREAKING CHANGES

* Generated files and resources now stored in user cache
directory instead of package directory. Old data/ folder no longer used.

Changes:
- Add centralized CacheManager for path management
- Add dynamic loader for generated modules from cache
- Update all components to use cache paths (resources, scraper, updater)
- Fix circular imports with lazy-loading in query_builder
- Update proxy generator to use absolute imports
- Remove 7.5MB of generated files from package (84% size reduction)
- Package size: 1.8MB -> 296KB

Cache structure:
~/.cache/escape_sdk/
├── generated/ (proxy classes, constants)
└── data/ (objects DB, varps, API data)

First import automatically downloads and generates all required files.

Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>

### Features

* migrate to XDG cache directory for generated files and resources ([c369c31](https://github.com/osescape/escape_sdk/commit/c369c319b83c87112a4619060f70b7a782604073))

### Bug Fixes

* **ci:** correct version sync in release workflow ([5b7c794](https://github.com/osescape/escape_sdk/commit/5b7c794edd34866344889040e95f814ae62bff27))
* update project URLs and ruff version ([077da2d](https://github.com/osescape/escape_sdk/commit/077da2d47fbd56128ef3e8bb007c102444e08fe5))

### Documentation

* add commit convention quick reference guide ([f23d39e](https://github.com/osescape/escape_sdk/commit/f23d39e7f12daaa9fdc887dc550d3495cb522970))

### CI/CD

* add semantic-release and quality check workflows ([51d420c](https://github.com/osescape/escape_sdk/commit/51d420c36510d7d3c54f573ee32bea64dfaf45e1))

## [2.0.0](https://github.com/osescape/escape_sdk/compare/v1.0.1...v2.0.0) (2025-11-23)

### BREAKING CHANGES

* Generated files and resources now stored in user cache
directory instead of package directory. Old data/ folder no longer used.

Changes:
- Add centralized CacheManager for path management
- Add dynamic loader for generated modules from cache
- Update all components to use cache paths (resources, scraper, updater)
- Fix circular imports with lazy-loading in query_builder
- Update proxy generator to use absolute imports
- Remove 7.5MB of generated files from package (84% size reduction)
- Package size: 1.8MB -> 296KB

Cache structure:
~/.cache/escape_sdk/
├── generated/ (proxy classes, constants)
└── data/ (objects DB, varps, API data)

First import automatically downloads and generates all required files.

Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>

### Features

* migrate to XDG cache directory for generated files and resources ([c369c31](https://github.com/osescape/escape_sdk/commit/c369c319b83c87112a4619060f70b7a782604073))

## [1.0.1](https://github.com/osescape/escape_sdk/compare/v1.0.0...v1.0.1) (2025-11-22)

### Bug Fixes

* update project URLs and ruff version ([077da2d](https://github.com/osescape/escape_sdk/commit/077da2d47fbd56128ef3e8bb007c102444e08fe5))

## 1.0.0 (2025-11-22)

### Documentation

* add commit convention quick reference guide ([f23d39e](https://github.com/osrs-chroma/escape_sdk/commit/f23d39e7f12daaa9fdc887dc550d3495cb522970))

### CI/CD

* add semantic-release and quality check workflows ([51d420c](https://github.com/osrs-chroma/escape_sdk/commit/51d420c36510d7d3c54f573ee32bea64dfaf45e1))

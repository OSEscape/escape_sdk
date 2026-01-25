# Changelog

All notable changes to this project will be documented in this file. See [Conventional Commits](https://conventionalcommits.org) for commit guidelines.

## [2.1.0](https://github.com/OSEscape/escape_sdk/compare/v2.0.1...v2.1.0) (2026-01-25)

### ✨ Features

* add unified linting pipeline (ruff, basedpyright, skylos) ([9e32115](https://github.com/OSEscape/escape_sdk/commit/9e321155424bc80073e2f8da75e6e4eb38913b52))

### 📚 Documentation

* update README with new make commands and linting stack ([b9b9527](https://github.com/OSEscape/escape_sdk/commit/b9b95274692dafb26423dc9f0001bda9454f1dbe))

### 💄 Styles

* auto-fix docstrings to PEP 257 one-line format ([f6f9aff](https://github.com/OSEscape/escape_sdk/commit/f6f9aff0b269822ecc4697d36f65c56ccaf9bc7a))
* auto-fix ruff violations ([1823495](https://github.com/OSEscape/escape_sdk/commit/182349565f5aab4b1e2ffa752f1d38b63f5eb29c))
* fix remaining D205, D401, and RUF012 violations ([2a20480](https://github.com/OSEscape/escape_sdk/commit/2a2048090c654b861177c396c821fddfb3954f16))

### 🔨 Build

* add make format target for auto-formatting ([6a72877](https://github.com/OSEscape/escape_sdk/commit/6a72877f952c6bea14127f0914cd4d604d70732a))

## [2.0.1](https://github.com/OSEscape/escape_sdk/compare/v2.0.0...v2.0.1) (2026-01-17)

### 🐛 Bug Fixes

* configure basedpyright to exclude generated files and warn on missing imports ([f5ca72c](https://github.com/OSEscape/escape_sdk/commit/f5ca72cb585c3e9a15fbc9ddb08c7b185cdbc6f3))

## [2.0.0](https://github.com/OSEscape/escape_sdk/compare/v1.0.3...v2.0.0) (2026-01-17)

### ⚠ BREAKING CHANGES

* All public method names now use snake_case

### 💄 Styles

* apply ruff formatting to merged code ([66b11a2](https://github.com/OSEscape/escape_sdk/commit/66b11a2dbb69df4662a59c7422eae3335d9172d2))

### ♻️ Refactoring

* adopt PEP 257 docstrings and add typed package support ([fe2e0f9](https://github.com/OSEscape/escape_sdk/commit/fe2e0f9f07da7889135491f60fe23ba324c50b62))
* adopt PEP 8 conventions and fix static analysis issues ([98c7882](https://github.com/OSEscape/escape_sdk/commit/98c788203f15dbfff0011a5baeb03b2c609e9456))
* align naming to PEP 8 across modules ([264304f](https://github.com/OSEscape/escape_sdk/commit/264304f58572342cca58e7b798b2ddfb351a9e53))
* standardize naming to PEP 8 snake_case ([e7dcb7c](https://github.com/OSEscape/escape_sdk/commit/e7dcb7cdf9164b3f4196cd2174448716627cb010))

### 👷 CI/CD

* update workflow to use basedpyright, remove deleted check_naming.py ([11fddff](https://github.com/OSEscape/escape_sdk/commit/11fddff1031ab73de2d514910212bfeee8fa7f4f))

## [1.0.3](https://github.com/OSEscape/escape_sdk/compare/v1.0.2...v1.0.3) (2026-01-17)

### 🐛 Bug Fixes

* url fix and graph.zip download ([58e7602](https://github.com/OSEscape/escape_sdk/commit/58e7602bb8d9a53ac293640e0b09e76452d2aaa9))

## [1.0.2](https://github.com/OSEscape/escape_sdk/compare/v1.0.1...v1.0.2) (2026-01-03)

### 📚 Documentation

* add PyPI install command with --upgrade flag ([984438c](https://github.com/OSEscape/escape_sdk/commit/984438cadad57e6b1815c24e26c76813b5434f7c))

## [1.0.1](https://github.com/OSEscape/escape_sdk/compare/v1.0.0...v1.0.1) (2026-01-03)

### 🐛 Bug Fixes

* revert version to 0.1.0 and improve resource loading checks ([4f468ae](https://github.com/OSEscape/escape_sdk/commit/4f468ae59e10dffe7c686a967bffae2952412712))

## 1.0.0 (2026-01-02)

### ⚠ BREAKING CHANGES

* Module access patterns have changed significantly.

- Convert Client, all tabs, Bank, Menu, Mouse, Keyboard, RuneLite,
  GroundItems, Pathfinder, and Player to singletons using __new__ + _init()
- Add module-level singleton exports (e.g., `from shadowlib.tabs.inventory import inventory`)
- Update namespace classes (Tabs, Interfaces, etc.) to return singleton instances
- Replace self.client pattern with `from shadowlib.client import client` imports
- Fix circular import issue by duplicating SKILL_NAMES constant
- Fix event consumer deadlock by not waiting for warmup during module import

Migration guide:
- Old: `client = Client(); client.tabs.inventory.getItems()`
- New: `from shadowlib.tabs.inventory import inventory; inventory.getItems()`
- Or: `from shadowlib.client import client; client.tabs.inventory.getItems()`
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
~/.cache/shadowlib/
├── generated/ (proxy classes, constants)
└── data/ (objects DB, varps, API data)

First import automatically downloads and generates all required files.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>

### ✨ Features

* add drawing module, geometry enhancements, and GeneralInterface ([292154a](https://github.com/OSEscape/escape_sdk/commit/292154a024aa6f3aa37dfb5bc889deacb18cc59a))
* add lazy-loaded interface ID to name lookup ([0aca0a0](https://github.com/OSEscape/escape_sdk/commit/0aca0a0a023517ac9b96478650fc26cc573e85dd))
* add namespace architecture and input system ([6c6b5fc](https://github.com/OSEscape/escape_sdk/commit/6c6b5fcc44925ad9b429e2e6095abad974a97d97))
* Add Quad geometry type and projection utilities ([c9aa6eb](https://github.com/OSEscape/escape_sdk/commit/c9aa6eb75b46f814d90746ca2b4950aefe5f0bff))
* enhance event cache initialization and menu interaction methods; improve inventory slot handling and timing utilities ([9848daa](https://github.com/OSEscape/escape_sdk/commit/9848daa42d52a98493e00c4d1929295e4f5b38bf))
* implement singleton pattern for RuneLiteAPI and add getOpenWidgets method to EventCache ([412613f](https://github.com/OSEscape/escape_sdk/commit/412613f3cc60a0e9c2ced9928c9295dc952b71a5))
* **interfaces:** add scrollbox support to GeneralInterface ([1bfe2d7](https://github.com/OSEscape/escape_sdk/commit/1bfe2d7b6b0ee47c3be0713dbc8397b51c5adeca))
* migrate to XDG cache directory for generated files and resources ([c369c31](https://github.com/OSEscape/escape_sdk/commit/c369c319b83c87112a4619060f70b7a782604073))
* **navigation:** implement Walker class for smart pathfinding and tile clicking ([105cb60](https://github.com/OSEscape/escape_sdk/commit/105cb6022f42f59e58f3ab11a1ebc535b0e2b4e2))
* rename package from shadowlib to escape ([3f87d04](https://github.com/OSEscape/escape_sdk/commit/3f87d04025fc5ed2cfcce16f01454c6f0569a528))
* rename package to escape-sdk v0.1.0 and fix linting ([654ccdd](https://github.com/OSEscape/escape_sdk/commit/654ccdd3323369e9a18ecc73fde8650e75240015))
* **types:** add Widget mask builder with IDE autocomplete support ([1535e5e](https://github.com/OSEscape/escape_sdk/commit/1535e5eccae2ca6d7b3076d89073916cc5792822))
* unify item lookup methods to accept ID or name ([d78e213](https://github.com/OSEscape/escape_sdk/commit/d78e2131c83e46ea2b4885f4aa7da5c7467c1893))
* update EventCache to retrieve active interfaces and refactor StateBuilder for widget management ([0351a0d](https://github.com/OSEscape/escape_sdk/commit/0351a0d8d08f608efee535fcc5d21d4d27737ad8))

### 🐛 Bug Fixes

* add type stubs for varps and objects modules ([d06696b](https://github.com/OSEscape/escape_sdk/commit/d06696befee34325727de299ff3bce2ee4f57605))
* **ci:** correct version sync in release workflow ([5b7c794](https://github.com/OSEscape/escape_sdk/commit/5b7c794edd34866344889040e95f814ae62bff27))
* **ci:** enable tag fetching for semantic-release ([6bc83f1](https://github.com/OSEscape/escape_sdk/commit/6bc83f194220c30bb3a872961cfa1cb5d9cb5d3b))
* **ci:** prevent sed from modifying ruff target-version ([08b4b07](https://github.com/OSEscape/escape_sdk/commit/08b4b07179f8150ae77887629935011ad923f018))
* format code and fix consumeMenuClickedState bug ([fd7b4bd](https://github.com/OSEscape/escape_sdk/commit/fd7b4bddf10906818461a03bb3e768d9493a9c1d))
* **lint:** add ignores for Python 3.12+ upgrade compatibility ([25bc9b3](https://github.com/OSEscape/escape_sdk/commit/25bc9b33ff373493c0b57005fd5419876cbc2df6))
* prevent ItemContainer.__init__ from running in Bank singleton ([0978036](https://github.com/OSEscape/escape_sdk/commit/0978036263a4946c178b358e6f07690a34fb631c))
* **query:** correct variable name in QueryRef.__getattr__ ([08e1021](https://github.com/OSEscape/escape_sdk/commit/08e10211073a95412c041623e67d8dac447720bc))
* remove debug prints from state_builder that may cause import issues ([7c367ed](https://github.com/OSEscape/escape_sdk/commit/7c367ed061cfaf4ffec793b0503f53909640e13e))
* resolve warmup deadlock by pre-importing constants ([2bc52c8](https://github.com/OSEscape/escape_sdk/commit/2bc52c8fe972b87f0519a83230e1d4e2c96188dc))
* **resources:** prevent duplicate downloads of shared files ([3abcb56](https://github.com/OSEscape/escape_sdk/commit/3abcb56c1a4432fbf6132e916dd2c05d03e1dfc4))
* update client.pyi stub to include resources namespace ([b0b3e45](https://github.com/OSEscape/escape_sdk/commit/b0b3e454075b5ed53077d28a6c71c29682944797))
* update project URLs and ruff version ([077da2d](https://github.com/OSEscape/escape_sdk/commit/077da2d47fbd56128ef3e8bb007c102444e08fe5))
* use module imports for resources type hints ([3a06dd3](https://github.com/OSEscape/escape_sdk/commit/3a06dd39b378f968802cd350a70fd7773009f503))
* **version:** restore version to 2.0.1 after incorrect release ([1253aad](https://github.com/OSEscape/escape_sdk/commit/1253aada19d4e235dc4db14ad35548b791658298))
* wait for event cache warmup after singleton creation ([4e844a4](https://github.com/OSEscape/escape_sdk/commit/4e844a43cb0b61c0b23087b647792504304b4e82))
* workflow file ([1a0d70b](https://github.com/OSEscape/escape_sdk/commit/1a0d70b84a0e3bb0e6317268a24cc4db4fc887de))

### 📚 Documentation

* add commit convention quick reference guide ([f23d39e](https://github.com/OSEscape/escape_sdk/commit/f23d39e7f12daaa9fdc887dc550d3495cb522970))
* add release notes for v2.0.2 clean slate ([4e494c1](https://github.com/OSEscape/escape_sdk/commit/4e494c18222d1d7c20abd28a9f75a57365fd0d4b))

### 💄 Styles

* apply ruff formatting and fix type hints ([88475e7](https://github.com/OSEscape/escape_sdk/commit/88475e7e9e5cce9614238dd69c64082b0e156c85))
* fix linting and formatting issues ([0d4fe16](https://github.com/OSEscape/escape_sdk/commit/0d4fe164d109fdaa87acb169eb7f38c1914978a6))
* fix linting issues in input modules ([6beeacc](https://github.com/OSEscape/escape_sdk/commit/6beeaccbd3bece4e69fc656ae9e60ad655bfaa0d))
* format check_naming.py with ruff ([26f7d1a](https://github.com/OSEscape/escape_sdk/commit/26f7d1a724778f88ad798e5b7ffeeee1b94728ef))
* merge formatting fixes from development ([ffb5e0e](https://github.com/OSEscape/escape_sdk/commit/ffb5e0ebd7a360a5032b93bb4b15f08084922ace))

### ♻️ Refactoring

* **ci:** consolidate workflows and upgrade to Python 3.12+ ([c3283b5](https://github.com/OSEscape/escape_sdk/commit/c3283b536478f8d3c612f2f16fcd58f6dd37e784))
* consolidate packed position utilities and improve event consumer warmup ([97e952e](https://github.com/OSEscape/escape_sdk/commit/97e952e66829a5190041153a2ca02c0000b42da7))
* convert modules to singleton pattern ([2e48446](https://github.com/OSEscape/escape_sdk/commit/2e484464daa6d03a4182fb7eba3e9d345387c621))
* **interfaces:** simplify scrollbox and add Box.contains(Box) ([a967e2d](https://github.com/OSEscape/escape_sdk/commit/a967e2d52a68d5e5aeff36b46ff6007370c4c17c))
* remove shadowlib/generated/ folder completely ([5a0a2ab](https://github.com/OSEscape/escape_sdk/commit/5a0a2ab41b47cc08a34b0011387f90f7b33036c9))
* **resources:** unify varps and objects into single GameDataResource ([46ce387](https://github.com/OSEscape/escape_sdk/commit/46ce3874e0d3295cd0507846026b5b9023c963e7))
* streamline resources module and merge cache utilities ([3e619c6](https://github.com/OSEscape/escape_sdk/commit/3e619c64dbc92efdc87c7fdcf2ceaccfb54ee882))
* streamline resources module and merge cache utilities ([0280441](https://github.com/OSEscape/escape_sdk/commit/0280441b41c0b82105a6d052050d21bf6598142f))

### 👷 CI/CD

* add semantic-release and quality check workflows ([51d420c](https://github.com/OSEscape/escape_sdk/commit/51d420c36510d7d3c54f573ee32bea64dfaf45e1))

## [3.3.0](https://github.com/escape/escape/compare/v3.2.1...v3.3.0) (2025-12-04)

### ✨ Features

* unify item lookup methods to accept ID or name ([d78e213](https://github.com/escape/escape/commit/d78e2131c83e46ea2b4885f4aa7da5c7467c1893))

## [3.2.1](https://github.com/escape/escape/compare/v3.2.0...v3.2.1) (2025-12-04)

### 🐛 Bug Fixes

* prevent ItemContainer.__init__ from running in Bank singleton ([0978036](https://github.com/escape/escape/commit/0978036263a4946c178b358e6f07690a34fb631c))

## [3.2.0](https://github.com/escape/escape/compare/v3.1.1...v3.2.0) (2025-12-04)

### ✨ Features

* implement singleton pattern for RuneLiteAPI and add getOpenWidgets method to EventCache ([412613f](https://github.com/escape/escape/commit/412613f3cc60a0e9c2ced9928c9295dc952b71a5))

### 🐛 Bug Fixes

* remove debug prints from state_builder that may cause import issues ([7c367ed](https://github.com/escape/escape/commit/7c367ed061cfaf4ffec793b0503f53909640e13e))

## [3.1.1](https://github.com/escape/escape/compare/v3.1.0...v3.1.1) (2025-12-04)

### 🐛 Bug Fixes

* resolve warmup deadlock by pre-importing constants ([2bc52c8](https://github.com/escape/escape/commit/2bc52c8fe972b87f0519a83230e1d4e2c96188dc))

## [3.1.0](https://github.com/escape/escape/compare/v3.0.0...v3.1.0) (2025-12-04)

### ✨ Features

* add lazy-loaded interface ID to name lookup ([0aca0a0](https://github.com/escape/escape/commit/0aca0a0a023517ac9b96478650fc26cc573e85dd))

### 🐛 Bug Fixes

* wait for event cache warmup after singleton creation ([4e844a4](https://github.com/escape/escape/commit/4e844a43cb0b61c0b23087b647792504304b4e82))

## [3.0.0](https://github.com/escape/escape/compare/v2.2.2...v3.0.0) (2025-12-04)

### ⚠ BREAKING CHANGES

* Module access patterns have changed significantly.

- Convert Client, all tabs, Bank, Menu, Mouse, Keyboard, RuneLite,
  GroundItems, Pathfinder, and Player to singletons using __new__ + _init()
- Add module-level singleton exports (e.g., `from escape.tabs.inventory import inventory`)
- Update namespace classes (Tabs, Interfaces, etc.) to return singleton instances
- Replace self.client pattern with `from escape.client import client` imports
- Fix circular import issue by duplicating SKILL_NAMES constant
- Fix event consumer deadlock by not waiting for warmup during module import

Migration guide:
- Old: `client = Client(); client.tabs.inventory.getItems()`
- New: `from escape.tabs.inventory import inventory; inventory.getItems()`
- Or: `from escape.client import client; client.tabs.inventory.getItems()`

### ✨ Features

* enhance event cache initialization and menu interaction methods; improve inventory slot handling and timing utilities ([9848daa](https://github.com/escape/escape/commit/9848daa42d52a98493e00c4d1929295e4f5b38bf))

### ♻️ Refactoring

* convert modules to singleton pattern ([2e48446](https://github.com/escape/escape/commit/2e484464daa6d03a4182fb7eba3e9d345387c621))

## [2.2.2](https://github.com/escape/escape/compare/v2.2.1...v2.2.2) (2025-11-25)

### 🐛 Bug Fixes

* add type stubs for varps and objects modules ([d06696b](https://github.com/escape/escape/commit/d06696befee34325727de299ff3bce2ee4f57605))
* update client.pyi stub to include resources namespace ([b0b3e45](https://github.com/escape/escape/commit/b0b3e454075b5ed53077d28a6c71c29682944797))
* use module imports for resources type hints ([3a06dd3](https://github.com/escape/escape/commit/3a06dd39b378f968802cd350a70fd7773009f503))

### 💄 Styles

* fix linting and formatting issues ([0d4fe16](https://github.com/escape/escape/commit/0d4fe164d109fdaa87acb169eb7f38c1914978a6))

### ♻️ Refactoring

* streamline resources module and merge cache utilities ([0280441](https://github.com/escape/escape/commit/0280441b41c0b82105a6d052050d21bf6598142f))

## [2.2.1](https://github.com/escape/escape/compare/v2.2.0...v2.2.1) (2025-11-25)

### ♻️ Refactoring

* streamline resources module and merge cache utilities ([3e619c6](https://github.com/escape/escape/commit/3e619c64dbc92efdc87c7fdcf2ceaccfb54ee882))

## [2.2.0](https://github.com/escape/escape/compare/v2.1.0...v2.2.0) (2025-11-24)

### ✨ Features

* add namespace architecture and input system ([6c6b5fc](https://github.com/escape/escape/commit/6c6b5fcc44925ad9b429e2e6095abad974a97d97))

### 💄 Styles

* apply ruff formatting and fix type hints ([88475e7](https://github.com/escape/escape/commit/88475e7e9e5cce9614238dd69c64082b0e156c85))
* fix linting issues in input modules ([6beeacc](https://github.com/escape/escape/commit/6beeaccbd3bece4e69fc656ae9e60ad655bfaa0d))
* merge formatting fixes from development ([ffb5e0e](https://github.com/escape/escape/commit/ffb5e0ebd7a360a5032b93bb4b15f08084922ace))

## [2.1.0](https://github.com/escape/escape/compare/v2.0.7...v2.1.0) (2025-11-24)

### ✨ Features

* **types:** add Widget mask builder with IDE autocomplete support ([1535e5e](https://github.com/escape/escape/commit/1535e5eccae2ca6d7b3076d89073916cc5792822))

### 💄 Styles

* format check_naming.py with ruff ([26f7d1a](https://github.com/escape/escape/commit/26f7d1a724778f88ad798e5b7ffeeee1b94728ef))

### ♻️ Refactoring

* consolidate packed position utilities and improve event consumer warmup ([97e952e](https://github.com/escape/escape/commit/97e952e66829a5190041153a2ca02c0000b42da7))

## [2.0.7](https://github.com/escape/escape/compare/v2.0.6...v2.0.7) (2025-11-23)

### ♻️ Refactoring

* **resources:** unify varps and objects into single GameDataResource ([46ce387](https://github.com/escape/escape/commit/46ce3874e0d3295cd0507846026b5b9023c963e7))

## [2.0.6](https://github.com/escape/escape/compare/v2.0.5...v2.0.6) (2025-11-23)

### 🐛 Bug Fixes

* **resources:** prevent duplicate downloads of shared files ([3abcb56](https://github.com/escape/escape/commit/3abcb56c1a4432fbf6132e916dd2c05d03e1dfc4))

## [2.0.5](https://github.com/escape/escape/compare/v2.0.4...v2.0.5) (2025-11-23)

### 🐛 Bug Fixes

* **query:** correct variable name in QueryRef.__getattr__ ([08e1021](https://github.com/escape/escape/commit/08e10211073a95412c041623e67d8dac447720bc))

## [2.0.4](https://github.com/escape/escape/compare/v2.0.3...v2.0.4) (2025-11-23)

### ♻️ Refactoring

* remove escape/generated/ folder completely ([5a0a2ab](https://github.com/escape/escape/commit/5a0a2ab41b47cc08a34b0011387f90f7b33036c9))

## [2.0.3](https://github.com/escape/escape/compare/v2.0.2...v2.0.3) (2025-11-23)

### 📚 Documentation

* add release notes for v2.0.2 clean slate ([4e494c1](https://github.com/escape/escape/commit/4e494c18222d1d7c20abd28a9f75a57365fd0d4b))

## 1.0.0 (2025-11-23)

### ⚠ BREAKING CHANGES

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
~/.cache/escape/
├── generated/ (proxy classes, constants)
└── data/ (objects DB, varps, API data)

First import automatically downloads and generates all required files.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>

### ✨ Features

* migrate to XDG cache directory for generated files and resources ([c369c31](https://github.com/escape/escape/commit/c369c319b83c87112a4619060f70b7a782604073))

### 🐛 Bug Fixes

* **ci:** correct version sync in release workflow ([5b7c794](https://github.com/escape/escape/commit/5b7c794edd34866344889040e95f814ae62bff27))
* **ci:** enable tag fetching for semantic-release ([6bc83f1](https://github.com/escape/escape/commit/6bc83f194220c30bb3a872961cfa1cb5d9cb5d3b))
* **ci:** prevent sed from modifying ruff target-version ([08b4b07](https://github.com/escape/escape/commit/08b4b07179f8150ae77887629935011ad923f018))
* **lint:** add ignores for Python 3.12+ upgrade compatibility ([25bc9b3](https://github.com/escape/escape/commit/25bc9b33ff373493c0b57005fd5419876cbc2df6))
* update project URLs and ruff version ([077da2d](https://github.com/escape/escape/commit/077da2d47fbd56128ef3e8bb007c102444e08fe5))
* **version:** restore version to 2.0.1 after incorrect release ([1253aad](https://github.com/escape/escape/commit/1253aada19d4e235dc4db14ad35548b791658298))

### 📚 Documentation

* add commit convention quick reference guide ([f23d39e](https://github.com/escape/escape/commit/f23d39e7f12daaa9fdc887dc550d3495cb522970))

### ♻️ Refactoring

* **ci:** consolidate workflows and upgrade to Python 3.12+ ([c3283b5](https://github.com/escape/escape/commit/c3283b536478f8d3c612f2f16fcd58f6dd37e784))

### 👷 CI/CD

* add semantic-release and quality check workflows ([51d420c](https://github.com/escape/escape/commit/51d420c36510d7d3c54f573ee32bea64dfaf45e1))

## [1.0.1](https://github.com/escape/escape/compare/v1.0.0...v1.0.1) (2025-11-23)

### 🐛 Bug Fixes

* **ci:** enable tag fetching for semantic-release ([6bc83f1](https://github.com/escape/escape/commit/6bc83f194220c30bb3a872961cfa1cb5d9cb5d3b))

## 1.0.0 (2025-11-23)

### ⚠ BREAKING CHANGES

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
~/.cache/escape/
├── generated/ (proxy classes, constants)
└── data/ (objects DB, varps, API data)

First import automatically downloads and generates all required files.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>

### ✨ Features

* migrate to XDG cache directory for generated files and resources ([c369c31](https://github.com/escape/escape/commit/c369c319b83c87112a4619060f70b7a782604073))

### 🐛 Bug Fixes

* **ci:** correct version sync in release workflow ([5b7c794](https://github.com/escape/escape/commit/5b7c794edd34866344889040e95f814ae62bff27))
* **ci:** prevent sed from modifying ruff target-version ([08b4b07](https://github.com/escape/escape/commit/08b4b07179f8150ae77887629935011ad923f018))
* **lint:** add ignores for Python 3.12+ upgrade compatibility ([25bc9b3](https://github.com/escape/escape/commit/25bc9b33ff373493c0b57005fd5419876cbc2df6))
* update project URLs and ruff version ([077da2d](https://github.com/escape/escape/commit/077da2d47fbd56128ef3e8bb007c102444e08fe5))

### 📚 Documentation

* add commit convention quick reference guide ([f23d39e](https://github.com/escape/escape/commit/f23d39e7f12daaa9fdc887dc550d3495cb522970))

### ♻️ Refactoring

* **ci:** consolidate workflows and upgrade to Python 3.12+ ([c3283b5](https://github.com/escape/escape/commit/c3283b536478f8d3c612f2f16fcd58f6dd37e784))

### 👷 CI/CD

* add semantic-release and quality check workflows ([51d420c](https://github.com/escape/escape/commit/51d420c36510d7d3c54f573ee32bea64dfaf45e1))

## 1.0.0 (2025-11-23)

### ⚠ BREAKING CHANGES

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
~/.cache/escape/
├── generated/ (proxy classes, constants)
└── data/ (objects DB, varps, API data)

First import automatically downloads and generates all required files.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>

### ✨ Features

* migrate to XDG cache directory for generated files and resources ([c369c31](https://github.com/escape/escape/commit/c369c319b83c87112a4619060f70b7a782604073))

### 🐛 Bug Fixes

* **ci:** correct version sync in release workflow ([5b7c794](https://github.com/escape/escape/commit/5b7c794edd34866344889040e95f814ae62bff27))
* **ci:** prevent sed from modifying ruff target-version ([08b4b07](https://github.com/escape/escape/commit/08b4b07179f8150ae77887629935011ad923f018))
* **lint:** add ignores for Python 3.12+ upgrade compatibility ([25bc9b3](https://github.com/escape/escape/commit/25bc9b33ff373493c0b57005fd5419876cbc2df6))
* update project URLs and ruff version ([077da2d](https://github.com/escape/escape/commit/077da2d47fbd56128ef3e8bb007c102444e08fe5))

### 📚 Documentation

* add commit convention quick reference guide ([f23d39e](https://github.com/escape/escape/commit/f23d39e7f12daaa9fdc887dc550d3495cb522970))

### ♻️ Refactoring

* **ci:** consolidate workflows and upgrade to Python 3.12+ ([c3283b5](https://github.com/escape/escape/commit/c3283b536478f8d3c612f2f16fcd58f6dd37e784))

### 👷 CI/CD

* add semantic-release and quality check workflows ([51d420c](https://github.com/escape/escape/commit/51d420c36510d7d3c54f573ee32bea64dfaf45e1))

## 1.0.0 (2025-11-23)

### ⚠ BREAKING CHANGES

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
~/.cache/escape/
├── generated/ (proxy classes, constants)
└── data/ (objects DB, varps, API data)

First import automatically downloads and generates all required files.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>

### ✨ Features

* migrate to XDG cache directory for generated files and resources ([c369c31](https://github.com/escape/escape/commit/c369c319b83c87112a4619060f70b7a782604073))

### 🐛 Bug Fixes

* **ci:** correct version sync in release workflow ([5b7c794](https://github.com/escape/escape/commit/5b7c794edd34866344889040e95f814ae62bff27))
* **ci:** prevent sed from modifying ruff target-version ([08b4b07](https://github.com/escape/escape/commit/08b4b07179f8150ae77887629935011ad923f018))
* update project URLs and ruff version ([077da2d](https://github.com/escape/escape/commit/077da2d47fbd56128ef3e8bb007c102444e08fe5))

### 📚 Documentation

* add commit convention quick reference guide ([f23d39e](https://github.com/escape/escape/commit/f23d39e7f12daaa9fdc887dc550d3495cb522970))

### 👷 CI/CD

* add semantic-release and quality check workflows ([51d420c](https://github.com/escape/escape/commit/51d420c36510d7d3c54f573ee32bea64dfaf45e1))

## 1.0.0 (2025-11-23)

### ⚠ BREAKING CHANGES

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
~/.cache/escape/
├── generated/ (proxy classes, constants)
└── data/ (objects DB, varps, API data)

First import automatically downloads and generates all required files.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>

### ✨ Features

* migrate to XDG cache directory for generated files and resources ([c369c31](https://github.com/escape/escape/commit/c369c319b83c87112a4619060f70b7a782604073))

### 🐛 Bug Fixes

* **ci:** correct version sync in release workflow ([5b7c794](https://github.com/escape/escape/commit/5b7c794edd34866344889040e95f814ae62bff27))
* update project URLs and ruff version ([077da2d](https://github.com/escape/escape/commit/077da2d47fbd56128ef3e8bb007c102444e08fe5))

### 📚 Documentation

* add commit convention quick reference guide ([f23d39e](https://github.com/escape/escape/commit/f23d39e7f12daaa9fdc887dc550d3495cb522970))

### 👷 CI/CD

* add semantic-release and quality check workflows ([51d420c](https://github.com/escape/escape/commit/51d420c36510d7d3c54f573ee32bea64dfaf45e1))

## [2.0.0](https://github.com/escape/escape/compare/v1.0.1...v2.0.0) (2025-11-23)

### ⚠ BREAKING CHANGES

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
~/.cache/escape/
├── generated/ (proxy classes, constants)
└── data/ (objects DB, varps, API data)

First import automatically downloads and generates all required files.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>

### ✨ Features

* migrate to XDG cache directory for generated files and resources ([c369c31](https://github.com/escape/escape/commit/c369c319b83c87112a4619060f70b7a782604073))

## [1.0.1](https://github.com/escape/escape/compare/v1.0.0...v1.0.1) (2025-11-22)

### 🐛 Bug Fixes

* update project URLs and ruff version ([077da2d](https://github.com/escape/escape/commit/077da2d47fbd56128ef3e8bb007c102444e08fe5))

## 1.0.0 (2025-11-22)

### 📚 Documentation

* add commit convention quick reference guide ([f23d39e](https://github.com/osrs-chroma/escape/commit/f23d39e7f12daaa9fdc887dc550d3495cb522970))

### 👷 CI/CD

* add semantic-release and quality check workflows ([51d420c](https://github.com/osrs-chroma/escape/commit/51d420c36510d7d3c54f573ee32bea64dfaf45e1))

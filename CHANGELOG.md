# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `__all__` now defines the public surface, and `CommandoptException`,
  `NoCommandFoundError`, `CommandCollisionError` are importable directly from the
  `commandopt` package.
- Structured exception attributes: `NoCommandFoundError.opts` and
  `CommandCollisionError.opts` / `.existing` / `.new`, so error data can be
  inspected programmatically instead of parsing the message.
- Full type hints across the public API (the `commandopt` decorator, `Command`
  methods, and the `CommandsOpts` / internal record), making the shipped
  `py.typed` marker meaningful.
- README "API reference" section documenting the full public surface and the
  exception hierarchy.

### Changed
- **Breaking:** `Command.add_command`'s first parameter is renamed from `opts`
  to `mandatory` for consistency with the `@commandopt(mandopts, opts)`
  decorator (where `opts` means *optional*). Positional callers are unaffected.
- Exception messages are now deterministic: the offending options are listed
  sorted instead of in arbitrary set order.

## [0.5.0] - 2026-06-24

### Changed
- Command registration no longer expands every subset of the optional options
  (`2**len(opts)` entries per command). Each command is now stored as a single
  `(mandatory, optional)` record and matched by range
  (`mandatory ⊆ truthy ⊆ mandatory ∪ optional`). Public matching and collision
  behaviour are unchanged; collisions are now detected as overlapping accepted
  ranges. `Command.list_commands()` returns one entry per command (its mandatory
  options) instead of one per subset.
- README documents the range-based matching and a new "Limitations / gotchas"
  section about exact truthy-argument matching (counters, non-`False` defaults).

### Added
- `docopt` and `test` optional extras (`pip install commandopt[docopt]`),
  pulling in `docopt-ng` without making it a hard dependency.
- Integration tests (`tests/test_docopt_integration.py`) that feed a real
  `ParsedOptions` produced by docopt-ng to `Command.run`, locking in the
  "dict subclass" compatibility guarantee. They are skipped when docopt-ng is
  not installed.

### Changed
- Migrated packaging to a PEP 621 `pyproject.toml` (build backend
  `setuptools.build_meta`). The version is now read **statically** from
  `commandopt.__version__` via `tool.setuptools.dynamic`, so the package is no
  longer imported at build time. `ruff` and `mypy` configuration moved into
  `pyproject.toml` as well.
- README now targets the maintained **docopt-ng** instead of the unmaintained
  original docopt, documents the drop-in backward compatibility (`from docopt
  import docopt` still works), and fixes the `commandopt` signature to match the
  code (`list` instead of `List`).
- CI test job and `tox.ini` install the `test` extra so the docopt-ng
  integration tests actually run.

### Removed
- Legacy `setup.py`, `setup.cfg`, and `ruff.toml`, now superseded by
  `pyproject.toml`.

## [0.4.0] - 2026-06-24

### Added
- `Command.run(arguments, call=False)`, an explicit classmethod entry point for
  selecting (and optionally executing) the registered command.

### Changed
- **Breaking:** command selection now goes through `Command.run(...)` instead of
  the overloaded `Command(...)` constructor. `Command(arguments)` no longer
  returns the matching function.

### Removed
- **Breaking:** the `Command.__new__` overload and its dead code, along with the
  never-implemented `give_kwargs` parameter (tracked for a future release).

## [0.3.0] - 2026-06-23

### Added
- GitHub Actions CI: pytest matrix (Python 3.9–3.13) plus a lint job running
  `ruff` and `mypy`.
- Minimal `ruff` configuration (`ruff.toml`) and a `[mypy]` section in
  `setup.cfg`.
- `Command.reset()` to clear the global registry, and a `conftest.py` fixture
  that isolates `Command.COMMANDS` between tests.
- Tests covering the `NoCommandFoundError` message, the `call=True` execution
  path, and the `give_kwargs=True` `NotImplementedError`.
- `CLAUDE.md` documenting the project conventions (TDD, branch naming, English,
  changelog, commit hygiene).
- `CommandCollisionError`, raised when two different functions are registered
  for the same set of options, instead of silently keeping one at random.
- README "Command matching" section documenting the set-based matching and the
  new collision behaviour.

### Changed
- `Command.COMMANDS` is now a `dict` indexed by `frozenset(opts)` instead of a
  `set` of `CommandsOpts`. This gives O(1) command lookup in `choose_command`,
  makes selection independent of the options' declaration order, and detects
  duplicate registrations deterministically.
- Align the advertised Python support with the PEP 585 type hints actually in
  use: `python_requires` is now `>=3.9`, `tox.ini` targets py39–py313, and
  version classifiers are declared accordingly. A `tests/test_packaging.py`
  guard locks this consistency.

### Fixed
- `NoCommandFoundError` now calls `super().__init__`, so its message is no
  longer empty when the exception is stringified.

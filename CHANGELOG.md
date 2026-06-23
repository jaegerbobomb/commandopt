# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

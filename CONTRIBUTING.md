# Contributing to commandopt

Thanks for your interest in improving commandopt! A few conventions keep the
project consistent — they are described in full in [`CLAUDE.md`](CLAUDE.md).

## Workflow

1. **Test-driven development (red → green).** Write the failing test first, watch
   it fail, then write the minimal code to make it pass. Keep the two steps in
   distinct commits where practical.
2. **Branch naming.** Use a kebab-case name with a type prefix, e.g.
   `feat/<description>`, `fix/<description>`, `chore/<description>`.
3. **English** for all code, comments, documentation and commit messages.
4. **Changelog.** Record every change in `CHANGELOG.md` under `[Unreleased]`,
   following [Keep a Changelog](https://keepachangelog.com/).

## Running the checks

```sh
pip install -e ".[test]"
pytest --cov=commandopt --cov-report=term-missing   # tests + coverage
ruff check .                                         # lint
mypy commandopt                                      # type-check
```

CI runs the test suite on Python 3.9–3.13, the linters, and a build +
`twine check` of the distribution. Please make sure all of these pass locally
before opening a pull request.

## Reporting bugs

Open an issue at <https://github.com/jaegerbobomb/commandopt/issues> with a
minimal reproduction (the docopt usage string and the arguments dict are usually
enough).

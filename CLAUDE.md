# Project conventions

These rules are required for every change in this repository.

## Test-driven development (red → green)

Tests are written **before** the implementation:

1. **Red** — write the test first and run it; confirm it *fails*.
2. **Green** — write the minimal code needed to make it *pass*; run again.

Keep the two phases distinct. Do not write production code and its test in the
same step.

## Branch naming

Use a descriptive, kebab-case name with a type prefix:

- `test/setup-ci-and-test-suite`
- `feat/<description>`
- `fix/<description>`

## Language

All code, identifiers, comments, documentation, and commit messages are written
in **English**.

## Changelog

Every change is recorded in `CHANGELOG.md` under the `[Unreleased]` section,
following the [Keep a Changelog](https://keepachangelog.com/) format
(`Added` / `Changed` / `Fixed` / ...). Update it in the same commit as the
change itself.

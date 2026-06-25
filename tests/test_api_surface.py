"""Lock the public API surface and the structured exception data for 1.0."""
import pytest

import commandopt
from commandopt import Command, commandopt as commandopt_decorator
from commandopt.exceptions import (
    CommandCollisionError,
    CommandoptException,
    NoCommandFoundError,
)


EXPECTED_PUBLIC = {
    "commandopt",
    "Command",
    "CommandsOpts",
    "CommandoptException",
    "NoCommandFoundError",
    "CommandCollisionError",
}


def test_all_lists_the_public_surface():
    assert set(commandopt.__all__) == EXPECTED_PUBLIC


def test_star_import_binds_only_the_public_surface():
    namespace = {}
    exec("from commandopt import *", namespace)
    bound = {name for name in namespace if not name.startswith("__")}
    assert bound == EXPECTED_PUBLIC


def test_internal_names_are_not_exported():
    # Implementation details must not leak through ``import *``.
    for leaked in ("_Command", "functools", "namedtuple"):
        assert leaked not in commandopt.__all__


def test_no_command_found_error_keeps_opts_attribute():
    error = NoCommandFoundError({"b", "a"})
    assert error.opts == frozenset({"a", "b"})
    assert isinstance(error, CommandoptException)


def test_no_command_found_error_message_is_deterministic():
    # Whatever the set ordering, the message lists the opts sorted.
    assert NoCommandFoundError({"b", "a"}).message == NoCommandFoundError(
        {"a", "b"}
    ).message
    assert "['a', 'b']" in NoCommandFoundError({"b", "a"}).message


def test_collision_error_exposes_structured_data():
    def existing(arguments):
        return "existing"

    def new(arguments):
        return "new"

    error = CommandCollisionError({"b", "a"}, existing, new)
    assert error.opts == frozenset({"a", "b"})
    assert error.existing is existing
    assert error.new is new
    assert "['a', 'b']" in error.message


def test_choose_command_error_carries_the_input_opts():
    @commandopt_decorator(["known"])
    def handler(arguments):
        return "ok"

    with pytest.raises(NoCommandFoundError) as excinfo:
        Command.choose_command({"unknown": True})
    assert excinfo.value.opts == frozenset({"unknown"})

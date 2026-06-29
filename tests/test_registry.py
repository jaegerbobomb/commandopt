"""Instance-based Registry and the application-level ``ignore`` mechanism."""
import pytest

import commandopt as pkg
from commandopt import Command, Registry, commandopt
from commandopt.exceptions import NoCommandFoundError


def test_registry_is_part_of_the_public_surface():
    assert "Registry" in pkg.__all__


def test_two_registries_are_isolated():
    cli_a = Registry()
    cli_b = Registry()

    @commandopt(["go"], registry=cli_a)
    def go_a(arguments):
        return "a"

    @commandopt(["go"], registry=cli_b)
    def go_b(arguments):
        return "b"

    assert cli_a.run({"go": True}) == "a"
    assert cli_b.run({"go": True}) == "b"
    # Neither leaked into the global default registry.
    with pytest.raises(NoCommandFoundError):
        Command.find({"go": True})


def test_registry_ignore_matches_and_command_still_receives_the_arg():
    cli = Registry(ignore={"--config"})

    @commandopt(["add", "<item>"], registry=cli)
    def add(arguments):
        return ("added", arguments["<item>"], arguments.get("--config"))

    args = {"add": True, "<item>": "foo", "--config": "/etc/app.cfg"}
    # --config is truthy but ignored for selection; the command still sees it.
    assert cli.run(args) == ("added", "foo", "/etc/app.cfg")


def test_per_call_ignore_overrides():
    cli = Registry()

    @commandopt(["add", "<item>"], registry=cli)
    def add(arguments):
        return "added"

    args = {"add": True, "<item>": "foo", "-v": True}
    with pytest.raises(NoCommandFoundError):
        cli.find(args)  # -v breaks matching
    assert cli.run(args, ignore={"-v"}) == "added"  # ignored for this call


def test_command_facade_global_ignore():
    @commandopt(["add", "<item>"])
    def add(arguments):
        return "added"

    Command.ignored = {"--config"}
    try:
        args = {"add": True, "<item>": "foo", "--config": "x"}
        assert Command.run(args) == "added"
    finally:
        Command.ignored = frozenset()


def test_command_facade_reflects_registry_state():
    @commandopt(["x"])
    def x(arguments):
        return "x"

    assert len(Command.COMMANDS) == 1
    assert {c.opts for c in Command.list_commands()} == {("x",)}
    Command.reset()
    assert len(Command.COMMANDS) == 0

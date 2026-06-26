"""Edge cases that lock down current behaviour for 1.0 confidence."""
import pytest

from commandopt import Command, Registry, commandopt
from commandopt.exceptions import NoCommandFoundError


def test_empty_mandopts_registers_a_default_command():
    @commandopt([])
    def default(arguments):
        return "default"

    # No truthy argument selects the empty-mandatory command.
    assert Command.run({}) == "default"
    assert Command.run({"--flag": False}) == "default"


def test_falsy_values_are_ignored_in_selection():
    @commandopt(["cmd"])
    def cmd(arguments):
        return "cmd"

    arguments = {
        "cmd": True,
        "--flag": False,
        "<x>": None,
        "n": 0,
        "s": "",
        "lst": [],
    }
    # Only "cmd" is truthy, so the falsy keys never affect matching.
    assert Command.run(arguments) == "cmd"


def test_empty_arguments_with_no_default_raises():
    @commandopt(["cmd"])
    def cmd(arguments):
        return "cmd"

    with pytest.raises(NoCommandFoundError):
        Command.find({})


def test_unicode_keys_match():
    @commandopt(["café", "<naïve>"])
    def accented(arguments):
        return arguments["<naïve>"]

    assert Command.run({"café": True, "<naïve>": "résumé"}) == "résumé"


def test_command_ignored_is_readable_and_defaults_empty():
    assert Command.ignored == frozenset()
    Command.ignored = {"--config"}
    try:
        assert Command.ignored == frozenset({"--config"})
    finally:
        Command.ignored = frozenset()


def test_registry_reset_clears_commands():
    cli = Registry()

    @commandopt(["x"], registry=cli)
    def x(arguments):
        return "x"

    assert len(cli.list_commands()) == 1
    cli.reset()
    assert cli.list_commands() == set()

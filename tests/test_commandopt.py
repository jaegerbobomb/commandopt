import pytest

from commandopt import commandopt, Command, CommandsOpts
from commandopt.exceptions import NoCommandFoundError


def test_commandopt_decorator_only_mandatory_opts():
    @commandopt(["command", "--mandatory1", "<mandatory2>"])
    @commandopt(["command", "--mandatory1"])
    def function(*args, **kwargs):
        pass

    assert (
        CommandsOpts(
            opts=tuple(["command", "--mandatory1", "<mandatory2>"]), f=function
        )
        in Command.list_commands()
    )
    assert (
        Command.choose_command({"command": True, "--mandatory1": True}).__wrapped__
        == function.__wrapped__.__wrapped__
    )

    with pytest.raises(NoCommandFoundError):
        Command.choose_command({"command": True, "<mandatory2>": True})


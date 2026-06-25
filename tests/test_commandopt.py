from itertools import chain, combinations

import pytest

from commandopt import commandopt, Command, CommandsOpts
from commandopt.exceptions import CommandCollisionError, NoCommandFoundError


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


def test_commandopt_decorator_mandatory_and_optional_opts():
    @commandopt(["command2"], ["--option1", "--option2"])
    def function(*args, **kwargs):
        pass

    arguments = [
        {"command2": True},
        {"command2": True, "--option1": True},
        {"command2": True, "--option2": True},
        {"command2": True, "--option1": True, "--option2": True},
    ]
    for args in arguments:
        assert Command.choose_command(args).__wrapped__ == function.__wrapped__

    with pytest.raises(NoCommandFoundError):
        Command.choose_command({"--option1": True})


def test_no_command_found_error_has_message():
    error = NoCommandFoundError({"x"})
    assert "No command found" in str(error)


def test_run_call_true_executes_function():
    @commandopt(["run"])
    def function(arguments):
        return "executed"

    assert Command.run({"run": True}, call=True) == "executed"


def test_run_without_call_returns_the_function():
    @commandopt(["run"])
    def function(arguments):
        return "executed"

    selected = Command.run({"run": True})
    assert callable(selected)
    assert selected({"run": True}) == "executed"


def test_command_is_not_callable_as_selector():
    # The overloaded __new__ has been removed: Command(...) no longer doubles
    # as a command selector. Command.run(...) is the only entry point.
    @commandopt(["run"])
    def function(arguments):
        return "executed"

    with pytest.raises(TypeError):
        Command({"run": True})


def test_duplicate_opts_with_different_functions_raises_collision():
    @commandopt(["dup"])
    def first(arguments):
        return "first"

    with pytest.raises(CommandCollisionError):

        @commandopt(["dup"])
        def second(arguments):
            return "second"


def test_duplicate_opts_same_function_is_idempotent():
    @commandopt(["idem"])
    def function(arguments):
        return "ok"

    # Re-registering the very same function under the same opts must not raise.
    Command.add_command(["idem"], function)
    assert Command.choose_command({"idem": True}) is function


def test_command_selection_is_independent_of_opts_order():
    @commandopt(["a", "b"])
    def function(arguments):
        return "ok"

    # The registry must match regardless of the order the opts were declared in.
    assert Command.choose_command({"b": True, "a": True}) is function


def test_optional_opts_do_not_explode_the_registry():
    # A command with N optionals must register a SINGLE command, not 2**N
    # entries (the historical "option explosion").
    @commandopt(["base"], ["o1", "o2", "o3", "o4", "o5"])
    def function(arguments):
        return "ok"

    assert len(Command.list_commands()) == 1
    assert len(Command.COMMANDS) == 1


def test_all_optional_subsets_still_resolve_to_the_command():
    optionals = ["o1", "o2", "o3"]

    @commandopt(["base"], optionals)
    def function(arguments):
        return "ok"

    subsets = chain.from_iterable(
        combinations(optionals, r) for r in range(len(optionals) + 1)
    )
    for subset in subsets:
        arguments = {"base": True, **{opt: True for opt in subset}}
        assert Command.choose_command(arguments) is function


def test_undeclared_truthy_argument_does_not_match():
    # Any truthy argument outside mandatory ∪ optional makes matching fail
    # (e.g. a docopt counter like -vvv or an option with a non-False default).
    @commandopt(["base"], ["o1"])
    def function(arguments):
        return "ok"

    with pytest.raises(NoCommandFoundError):
        Command.choose_command({"base": True, "--undeclared": True})


def test_overlapping_optional_ranges_collide():
    # Two different functions whose accepted argument sets overlap must be
    # rejected, even when their mandatory parts differ. Here {a, x} is accepted
    # by both, so they collide.
    @commandopt(["a"], ["x"])
    def first(arguments):
        return "first"

    with pytest.raises(CommandCollisionError):

        @commandopt(["a", "x"])
        def second(arguments):
            return "second"



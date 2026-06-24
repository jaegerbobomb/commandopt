# -*- coding: utf-8 -*-
import functools
from collections import namedtuple
from itertools import chain, combinations

from commandopt.exceptions import CommandCollisionError, NoCommandFoundError

__version__ = "0.4.0"
CommandsOpts = namedtuple("CommandsOpts", ["opts", "f"])


def commandopt(mandopts: list[str], opts=None):
    """Decorator to register commands given docopt arguments.

    :param mandopts:  List of mandatory arguments
    :param opts:      List of optional arguments
    """
    opts = [] if opts is None else opts

    def inner_decorator(f):
        @functools.wraps(f)
        def wrapped(*args, **kwargs):
            return f(*args, **kwargs)

        # register wrapped function in Command.COMMANDS mapping
        Command.add_command(mandopts, wrapped)
        # get all combinations of optionals arguments
        # ex : (opt1,), (opt2,), (opt1, opt2) ...
        opts_combinations = [combinations(opts, r) for r in range(len(opts) + 1)]
        for combination in chain.from_iterable(opts_combinations):
            # register wrapped function with optional arguments
            Command.add_command(mandopts + list(combination), wrapped)
        return wrapped

    return inner_decorator


class Command(object):
    """Dumb class to keep all the registered commands."""

    # Indexed by the frozenset of options for O(1) lookup and natural
    # duplicate detection (the order of the options is irrelevant when
    # matching, so two declarations with the same options collide).
    COMMANDS: dict[frozenset[str], CommandsOpts] = {}

    @classmethod
    def run(cls, arguments, call=False):
        """Return the command registered for ``arguments``.

        :param arguments:  The docopt arguments mapping.
        :param call:       When ``True``, invoke the matching function with
                           ``arguments`` and return its result instead of the
                           function itself.
        """
        f = cls.choose_command(arguments)
        if call:
            return f(arguments)
        return f

    @classmethod
    def reset(cls):
        """Clear the global registry (useful for test isolation)."""
        cls.COMMANDS = {}

    @classmethod
    def add_command(cls, opts: list[str], f):
        key = frozenset(opts)
        existing = cls.COMMANDS.get(key)
        if existing is not None and existing.f is not f:
            raise CommandCollisionError(set(opts), existing.f, f)
        cls.COMMANDS[key] = CommandsOpts(opts=tuple(opts), f=f)

    @classmethod
    def list_commands(cls) -> set[CommandsOpts]:
        return set(cls.COMMANDS.values())

    @classmethod
    def choose_command(cls, arguments):
        # First get all "True" arguments from docopt
        opts_input = frozenset(opt for opt in arguments.keys() if arguments[opt])
        command = cls.COMMANDS.get(opts_input)
        if command is not None:
            return command.f
        raise NoCommandFoundError(set(opts_input))

# -*- coding: utf-8 -*-
import functools
from collections import namedtuple

from commandopt.exceptions import CommandCollisionError, NoCommandFoundError

__version__ = "0.4.0"
CommandsOpts = namedtuple("CommandsOpts", ["opts", "f"])

# Internal registry record: the mandatory options (both as an ordered tuple for
# display and as a frozenset for matching) plus the set of accepted optional
# options and the registered function.
_Command = namedtuple("_Command", ["mandatory", "optional", "opts", "f"])


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

        # Register a single command describing the whole [mandatory,
        # mandatory + optional] range, instead of one entry per optional
        # subset (which used to be 2**len(opts) registrations).
        Command.add_command(mandopts, wrapped, optional=opts)
        return wrapped

    return inner_decorator


class Command(object):
    """Dumb class to keep all the registered commands."""

    # Indexed by the frozenset of mandatory options. A command accepts any
    # argument set ``S`` with ``mandatory <= S <= mandatory | optional``, so a
    # single record replaces the historical per-subset expansion.
    COMMANDS: dict[frozenset[str], _Command] = {}

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
    def add_command(cls, opts: list[str], f, optional=()):
        """Register ``f`` for the mandatory ``opts`` and the given ``optional``.

        Two *different* functions collide when their accepted argument sets
        overlap, i.e. when some argument set is accepted by both. For commands
        ``(M1, O1)`` and ``(M2, O2)`` this happens iff ``M2 \\ M1 <= O1`` and
        ``M1 \\ M2 <= O2``.
        """
        mandatory = frozenset(opts)
        optional = frozenset(optional)

        existing = cls.COMMANDS.get(mandatory)
        if existing is not None and existing.f is not f:
            raise CommandCollisionError(set(opts), existing.f, f)

        for other in cls.COMMANDS.values():
            if other.mandatory == mandatory or other.f is f:
                continue
            if (
                other.mandatory - mandatory <= optional
                and mandatory - other.mandatory <= other.optional
            ):
                witness = set(mandatory | other.mandatory)
                raise CommandCollisionError(witness, other.f, f)

        cls.COMMANDS[mandatory] = _Command(
            mandatory=mandatory, optional=optional, opts=tuple(opts), f=f
        )

    @classmethod
    def list_commands(cls) -> set[CommandsOpts]:
        return {CommandsOpts(opts=c.opts, f=c.f) for c in cls.COMMANDS.values()}

    @classmethod
    def choose_command(cls, arguments):
        # The set of "truthy" arguments returned by docopt.
        opts_input = frozenset(opt for opt in arguments.keys() if arguments[opt])

        # Fast path: an input made of exactly a command's mandatory options.
        command = cls.COMMANDS.get(opts_input)
        if command is not None:
            return command.f

        # General case: find the command whose accepted range contains the
        # input (mandatory <= input <= mandatory | optional). Collision
        # detection guarantees at most one such command.
        for command in cls.COMMANDS.values():
            if command.mandatory <= opts_input <= command.mandatory | command.optional:
                return command.f

        raise NoCommandFoundError(set(opts_input))

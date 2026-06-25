# -*- coding: utf-8 -*-
from __future__ import annotations

import functools
from collections.abc import Callable, Iterable, Mapping
from typing import Any, NamedTuple, Optional, TypeVar, cast

from commandopt.exceptions import (
    CommandCollisionError,
    CommandoptException,
    NoCommandFoundError,
)

__all__ = [
    "commandopt",
    "Command",
    "CommandsOpts",
    "CommandoptException",
    "NoCommandFoundError",
    "CommandCollisionError",
]

__version__ = "0.5.0"

# A decorated command function; the decorator returns the same callable type.
F = TypeVar("F", bound=Callable[..., Any])


class CommandsOpts(NamedTuple):
    """One registered command: its mandatory options and the handler function."""

    opts: tuple[str, ...]
    f: Callable[..., Any]


class _Command(NamedTuple):
    """Internal registry record.

    ``mandatory`` is kept both as a ``frozenset`` (for matching) and as an
    ordered ``opts`` tuple (for display in :meth:`Command.list_commands`).
    """

    mandatory: frozenset[str]
    optional: frozenset[str]
    opts: tuple[str, ...]
    f: Callable[..., Any]


def commandopt(
    mandopts: list[str], opts: Optional[list[str]] = None
) -> Callable[[F], F]:
    """Register the decorated function as the command for ``mandopts``.

    :param mandopts:  Mandatory argument keys; all must be truthy to match.
    :param opts:      Optional argument keys that may also be truthy.
    :returns:         A decorator returning the function unchanged.
    """
    optional = [] if opts is None else opts

    def inner_decorator(f: F) -> F:
        @functools.wraps(f)
        def wrapped(*args: Any, **kwargs: Any) -> Any:
            return f(*args, **kwargs)

        # The wrapper gives each (possibly stacked) decorator a distinct
        # function object, so stacking @commandopt registers independent
        # commands that all dispatch to the same underlying function.
        Command.add_command(mandopts, wrapped, optional=optional)
        return cast(F, wrapped)

    return inner_decorator


class Command:
    """Process-global registry of commands, keyed by their mandatory options.

    A command accepts any truthy-argument set ``S`` with
    ``mandatory <= S <= mandatory | optional``; a single record per command
    replaces the historical per-optional-subset expansion.
    """

    COMMANDS: dict[frozenset[str], _Command] = {}

    @classmethod
    def run(cls, arguments: Mapping[str, Any], call: bool = False) -> Any:
        """Return the command registered for ``arguments``.

        :param arguments:  The docopt arguments mapping.
        :param call:       When ``True``, invoke the matching function with
                           ``arguments`` and return its result instead of the
                           function itself.
        :raises NoCommandFoundError:  If no registered command matches.
        """
        f = cls.choose_command(arguments)
        if call:
            return f(arguments)
        return f

    @classmethod
    def reset(cls) -> None:
        """Clear the global registry (useful for test isolation)."""
        cls.COMMANDS = {}

    @classmethod
    def add_command(
        cls,
        mandatory: Iterable[str],
        f: Callable[..., Any],
        optional: Iterable[str] = (),
    ) -> None:
        """Register ``f`` for the ``mandatory`` options and the given ``optional``.

        Two *different* functions collide when their accepted argument sets
        overlap, i.e. when some argument set is accepted by both. For commands
        ``(M1, O1)`` and ``(M2, O2)`` this happens iff ``M2 \\ M1 <= O1`` and
        ``M1 \\ M2 <= O2``.

        :raises CommandCollisionError:  If a different function already accepts
                                        an overlapping argument set.
        """
        mandatory_opts = tuple(mandatory)
        mandatory_set = frozenset(mandatory_opts)
        optional_set = frozenset(optional)

        existing = cls.COMMANDS.get(mandatory_set)
        if existing is not None and existing.f is not f:
            raise CommandCollisionError(mandatory_set, existing.f, f)

        for other in cls.COMMANDS.values():
            if other.mandatory == mandatory_set or other.f is f:
                continue
            if (
                other.mandatory - mandatory_set <= optional_set
                and mandatory_set - other.mandatory <= other.optional
            ):
                witness = mandatory_set | other.mandatory
                raise CommandCollisionError(witness, other.f, f)

        cls.COMMANDS[mandatory_set] = _Command(
            mandatory=mandatory_set,
            optional=optional_set,
            opts=mandatory_opts,
            f=f,
        )

    @classmethod
    def list_commands(cls) -> set[CommandsOpts]:
        """Return one :class:`CommandsOpts` per registered command."""
        return {CommandsOpts(opts=c.opts, f=c.f) for c in cls.COMMANDS.values()}

    @classmethod
    def choose_command(cls, arguments: Mapping[str, Any]) -> Callable[..., Any]:
        """Return the function whose accepted range matches ``arguments``.

        :param arguments:  The docopt arguments mapping.
        :raises NoCommandFoundError:  If no registered command matches.
        """
        # The set of "truthy" arguments returned by docopt.
        opts_input = frozenset(opt for opt in arguments if arguments[opt])

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

        raise NoCommandFoundError(opts_input)

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
    "Registry",
    "CommandsOpts",
    "CommandoptException",
    "NoCommandFoundError",
    "CommandCollisionError",
]

__version__ = "1.0.0rc1"

# A decorated command function; the decorator returns the same callable type.
F = TypeVar("F", bound=Callable[..., Any])


class CommandsOpts(NamedTuple):
    """One registered command: its mandatory options and the handler function."""

    opts: tuple[str, ...]
    f: Callable[..., Any]


class _Command(NamedTuple):
    """Internal registry record.

    ``mandatory`` is kept both as a ``frozenset`` (for matching) and as an
    ordered ``opts`` tuple (for display in :meth:`Registry.list_commands`).
    """

    mandatory: frozenset[str]
    optional: frozenset[str]
    opts: tuple[str, ...]
    f: Callable[..., Any]


class Registry:
    """A collection of commands matched against a docopt arguments mapping.

    A command declared with mandatory options ``M`` and optional options ``O``
    accepts any truthy-argument set ``S`` with ``M <= S <= M | O``.

    Use a dedicated instance to host an independent set of commands (e.g. two
    CLIs in one process) or for test isolation. The process-global default
    registry is exposed through the :class:`Command` façade.

    :param ignore:  Application-level argument keys (``--config``, ``--debug``,
                    ``-v``…) that are excluded from command selection even when
                    truthy. The matched function still receives them in full.
    """

    def __init__(self, ignore: Iterable[str] = ()) -> None:
        self._commands: dict[frozenset[str], _Command] = {}
        self.ignored: frozenset[str] = frozenset(ignore)

    def reset(self) -> None:
        """Clear every registered command (useful for test isolation)."""
        self._commands = {}

    def add_command(
        self,
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

        existing = self._commands.get(mandatory_set)
        if existing is not None and existing.f is not f:
            raise CommandCollisionError(mandatory_set, existing.f, f)

        for other in self._commands.values():
            # Skip the same command (idempotent re-registration). Computed
            # inline rather than via ``continue`` so coverage is consistent
            # across Python versions.
            is_same_command = other.mandatory == mandatory_set or other.f is f
            if (
                not is_same_command
                and other.mandatory - mandatory_set <= optional_set
                and mandatory_set - other.mandatory <= other.optional
            ):
                witness = mandatory_set | other.mandatory
                raise CommandCollisionError(witness, other.f, f)

        self._commands[mandatory_set] = _Command(
            mandatory=mandatory_set,
            optional=optional_set,
            opts=mandatory_opts,
            f=f,
        )

    def find(
        self, arguments: Mapping[str, Any], ignore: Iterable[str] = ()
    ) -> Callable[..., Any]:
        """Select and return the command function for ``arguments`` (no execution).

        :param arguments:  The docopt arguments mapping.
        :param ignore:     Extra argument keys to exclude from selection for this
                           call, on top of the registry's :attr:`ignored` set.
        :raises NoCommandFoundError:  If no registered command matches.
        """
        ignored = self.ignored | frozenset(ignore)
        # The set of "truthy" arguments returned by docopt, minus ignored ones.
        opts_input = frozenset(opt for opt in arguments if arguments[opt]) - ignored

        # Fast path: an input made of exactly a command's mandatory options.
        command = self._commands.get(opts_input)
        if command is not None:
            return command.f

        # General case: find the command whose accepted range contains the input
        # (mandatory <= input <= mandatory | optional). Collision detection
        # guarantees at most one such command.
        for command in self._commands.values():
            if command.mandatory <= opts_input <= command.mandatory | command.optional:
                return command.f

        raise NoCommandFoundError(opts_input)

    def run(self, arguments: Mapping[str, Any], ignore: Iterable[str] = ()) -> Any:
        """Select the command for ``arguments``, execute it and return its result.

        Equivalent to ``find(arguments, ignore)(arguments)`` — the matched
        function receives the *full* ``arguments`` mapping, ignored keys included.

        :raises NoCommandFoundError:  If no registered command matches.
        """
        return self.find(arguments, ignore=ignore)(arguments)

    def list_commands(self) -> set[CommandsOpts]:
        """Return one :class:`CommandsOpts` per registered command."""
        return {CommandsOpts(opts=c.opts, f=c.f) for c in self._commands.values()}


class _CommandMeta(type):
    """Expose the default registry's mutable state on the :class:`Command` façade."""

    _registry: "Registry"

    @property
    def COMMANDS(cls) -> dict[frozenset[str], _Command]:
        return cls._registry._commands

    @property
    def ignored(cls) -> frozenset[str]:
        return cls._registry.ignored

    @ignored.setter
    def ignored(cls, value: Iterable[str]) -> None:
        cls._registry.ignored = frozenset(value)


class Command(metaclass=_CommandMeta):
    """Backward-compatible façade over a process-global default :class:`Registry`.

    Every classmethod delegates to ``Command._registry``. Configure the ignored
    application-level options with ``Command.ignored = {...}``. For isolated
    command sets (or test isolation), instantiate your own :class:`Registry`.
    """

    _registry = Registry()

    @classmethod
    def add_command(
        cls,
        mandatory: Iterable[str],
        f: Callable[..., Any],
        optional: Iterable[str] = (),
    ) -> None:
        """Delegate to :meth:`Registry.add_command` on the default registry."""
        cls._registry.add_command(mandatory, f, optional=optional)

    @classmethod
    def find(
        cls, arguments: Mapping[str, Any], ignore: Iterable[str] = ()
    ) -> Callable[..., Any]:
        """Delegate to :meth:`Registry.find` on the default registry."""
        return cls._registry.find(arguments, ignore=ignore)

    @classmethod
    def run(cls, arguments: Mapping[str, Any], ignore: Iterable[str] = ()) -> Any:
        """Delegate to :meth:`Registry.run` on the default registry."""
        return cls._registry.run(arguments, ignore=ignore)

    @classmethod
    def reset(cls) -> None:
        """Clear the default registry (useful for test isolation)."""
        cls._registry.reset()

    @classmethod
    def list_commands(cls) -> set[CommandsOpts]:
        """Return one :class:`CommandsOpts` per command in the default registry."""
        return cls._registry.list_commands()


def commandopt(
    mandopts: list[str],
    opts: Optional[list[str]] = None,
    registry: Optional[Registry] = None,
) -> Callable[[F], F]:
    """Register the decorated function as the command for ``mandopts``.

    :param mandopts:  Mandatory argument keys; all must be truthy to match.
    :param opts:      Optional argument keys that may also be truthy.
    :param registry:  Target registry; defaults to the global :class:`Command`
                      registry.
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
        target = Command._registry if registry is None else registry
        target.add_command(mandopts, wrapped, optional=optional)
        return cast(F, wrapped)

    return inner_decorator

#!/usr/bin/env python
# -*- coding: utf-8 -*-
from collections.abc import Callable, Iterable


class CommandoptException(Exception):
    """Base class of the commandopt exceptions."""

    pass


class NoCommandFoundError(CommandoptException):
    """No registered command matched the given arguments.

    :ivar opts:  The set of truthy argument keys that found no command.
    """

    def __init__(self, opts: Iterable[str]):
        self.opts = frozenset(opts)
        # Sort the opts so the message is deterministic regardless of set order.
        self.message = "No command found for opts = {}".format(sorted(self.opts))
        super().__init__(self.message)


class CommandCollisionError(CommandoptException):
    """Two different functions were registered for overlapping argument sets.

    :ivar opts:      A set of options accepted by both commands (the overlap).
    :ivar existing:  The already-registered function.
    :ivar new:       The function whose registration triggered the collision.
    """

    def __init__(self, opts: Iterable[str], existing: Callable, new: Callable):
        self.opts = frozenset(opts)
        self.existing = existing
        self.new = new
        self.message = (
            "Two different commands are registered for opts = {}: "
            "{!r} and {!r}".format(sorted(self.opts), existing, new)
        )
        super().__init__(self.message)

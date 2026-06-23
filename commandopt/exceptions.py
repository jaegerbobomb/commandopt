#!/usr/bin/env python
# -*- coding: utf-8 -*-


class CommandoptException(Exception):
    """Base class of the commandopt exceptions."""
    pass


class NoCommandFoundError(CommandoptException):
    def __init__(self, opts):
        self.message = "No command found for opts = {}".format(opts)
        super().__init__(self.message)


class CommandCollisionError(CommandoptException):
    def __init__(self, opts, existing, new):
        self.message = (
            "Two different commands are registered for opts = {}: "
            "{!r} and {!r}".format(opts, existing, new)
        )
        super().__init__(self.message)

#!/usr/bin/env python
# -*- coding: utf-8 -*-


class CommandoptException(Exception):
    """Base class of the commandopt exceptions."""
    pass


class NoCommandFoundError(CommandoptException):
    def __init__(self, opts):
        self.message = "No command found for opts = {}".format(opts)

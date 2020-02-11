# -*- coding: utf-8 -*-
from collections import namedtuple

from commandopt.exceptions import NoCommandFoundError


__version__ = "0.1.0"
CommandsOpts = namedtuple("CommandsOpts", ["opts", "f"])


def commandopt(opts):
    """Decorator to register commands given docopt arguments.

    :param opts:  Dict of arguments required
    """

    def inner_decorator(f):

        def wrapped(*args, **kwargs):
            return f(*args, **kwargs)

        # register wrapped function in Command.COMMANDS mapping
        Command.add_command(opts, wrapped)
        return wrapped

    return inner_decorator


class Command(object):
    """Dumb class to keep all the registered commands."""

    COMMANDS = set()

    def __new__(cls, arguments, call=False, give_kwargs=False):
        """Select the right command function and call it if asked."""

        f = cls.choose_command(arguments)
        if call and not give_kwargs:
            return f(arguments)
        elif call:
            raise NotImplementedError
            # TODO get arguments without "--" or "<>"...
            return f(**arguments)
        return f

    @classmethod
    def add_command(cls, opts, f):
        cls.COMMANDS.add(CommandsOpts(opts=tuple(opts), f=f))

    @classmethod
    def list_commands(cls):
        return cls.COMMANDS

    @classmethod
    def choose_command(cls, arguments):
        # First get all "True" arguments from docopt
        opts_input = set([opt for opt in arguments.keys() if arguments[opt]])
        for c in cls.COMMANDS:
            if opts_input == set(c.opts):
                return c.f
        raise NoCommandFoundError(opts_input)


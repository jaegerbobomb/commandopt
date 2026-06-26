"""Integration tests against docopt-ng.

These lock in the guarantee that commandopt works with the ``ParsedOptions``
object returned by docopt-ng (a ``dict`` subclass) without any code change.
They are skipped when docopt-ng is not installed (it is an optional extra).
"""
import pytest

from commandopt import Command, commandopt

docopt = pytest.importorskip("docopt")

DOC = """Naval Fate.

Usage:
  naval_fate.py ship new <name>...
  naval_fate.py new-ship [<name>]
  naval_fate.py --version

Options:
  --version     Show version.
"""


def test_parsed_options_is_a_dict_subclass():
    arguments = docopt.docopt(DOC, argv=["new-ship", "Boat"])
    assert isinstance(arguments, dict)


def test_command_run_selects_function_from_real_parsed_options():
    @commandopt(["ship", "new", "<name>"])
    def ship_new(arguments):
        return ("ship_new", arguments["<name>"])

    @commandopt(["new-ship"], ["<name>"])
    def new_ship(arguments):
        return ("new_ship", arguments["<name>"])

    arguments = docopt.docopt(DOC, argv=["ship", "new", "Titanic"])
    assert Command.run(arguments) == ("ship_new", ["Titanic"])

    arguments = docopt.docopt(DOC, argv=["new-ship", "Boat"])
    assert Command.run(arguments) == ("new_ship", ["Boat"])

    arguments = docopt.docopt(DOC, argv=["new-ship"])
    assert Command.run(arguments) == ("new_ship", [])

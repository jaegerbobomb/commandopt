import pytest

from commandopt import Command


@pytest.fixture(autouse=True)
def reset_commands():
    """Isolate the global Command.COMMANDS registry between tests."""
    Command.reset()
    yield
    Command.reset()

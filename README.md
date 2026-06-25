# commandopt

Turn a dict of arguments into cli commands, ideal companion of
[docopt-ng](https://pypi.org/project/docopt-ng/).

## Why ?

Using the `commandopt.commandopt` decorator, you are able to declare commands to be
executed depending on the input arguments of your app (required or optional).

It reduces the boilerplate code in your `main()`.

## Installation

```sh
pip install commandopt
# optionally, the maintained argument parser it pairs with:
pip install docopt-ng
```

> The original [docopt](https://pypi.org/project/docopt/) has been unmaintained
> since 2014. **docopt-ng** is its maintained, drop-in replacement: it installs
> as `docopt-ng` but still exposes the `docopt` module, so `from docopt import
> docopt` keeps working unchanged. commandopt only relies on the parsed
> arguments being a `dict` (docopt-ng returns a `ParsedOptions`, which is a
> `dict` subclass), so it works with either with no code change.

commandopt does **not** depend on docopt-ng directly — it accepts any dict of
arguments. Install it explicitly (or via the optional extra `commandopt[docopt]`).

## Signature

```py
def commandopt(mandopts: list[str], opts=None):
    # ...
```

### Call

```py
@commandopt(mandatory_arguments, optional_arguments)
def xxxx(*args, **kwargs):
```

## Example usage

```py
#myapp/myapp.py
"""Naval Fate.

Usage:
  naval_fate.py ship new <name>...
  naval_fate.py new-ship [<name>]
  naval_fate.py --version

Options:
  --version     Show version.

"""
from commandopt import Command
from docopt import docopt

import myapp.commands.ship

if __name__ == '__main__':
    arguments = docopt(__doc__, version='Naval Fate 2.0')
    command = Command.run(arguments)  # get the registered function
    command(arguments)  # execute the function
    # or, to select and execute in one call:
    # Command.run(arguments, call=True)

```

```py
#myapp/commands/ship.py
from commandopt import commandopt

class ShipCommand:

    @commandopt(["ship", "new", "<name>"])
    @commandopt(["new-ship"], ["<name>"])
    def new(arguments):
        """You can stack the decorator if you want."""
        name = arguments["<name>"] or "case when name is empty"
        # ... your code here
```

## Command matching

A command is selected by comparing the **set** of truthy arguments returned by
docopt against the registered command. A command declared with mandatory options
`M` and optional options `O` matches an input whose truthy set `S` satisfies:

```
M ⊆ S ⊆ M ∪ O
```

In other words, every mandatory option must be present, and any extra truthy
option must be one of the declared optionals. Declaration order is irrelevant
(matching is set-based), and each command is stored as a **single** record — no
matter how many optionals it declares.

> Earlier versions registered every subset of the optionals (`2**len(O)`
> entries per command). This is no longer the case: a command now costs one
> registration regardless of the number of optionals, while matching behaves
> exactly the same.

Registering **two different functions whose accepted argument sets overlap**
raises a `CommandCollisionError` instead of silently keeping one of them at
random:

```py
from commandopt import commandopt
from commandopt.exceptions import CommandCollisionError

@commandopt(["status"])
def show_status(arguments):
    ...

@commandopt(["status"])  # raises CommandCollisionError
def other_status(arguments):
    ...
```

## Limitations / gotchas

Matching is **exact** over the truthy arguments: every truthy argument must be
accounted for by the command's mandatory or optional options. Any *unexpected*
truthy argument makes matching fail with `NoCommandFoundError`, which can be
surprising with some docopt argument types:

- **Repeatable flags / counters** (`-v` used as `-vvv`) become an integer `> 0`,
  which is truthy.
- **Options with a non-`False` default value** are always truthy.

If your usage patterns include such arguments, declare them as optionals on the
relevant commands (so they fall within `M ∪ O`), or normalise the arguments dict
before calling `Command.run(...)`.


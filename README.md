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
def commandopt(mandopts: list[str], opts: list[str] | None = None):
    # ...
```

- `mandopts`: mandatory argument keys — all must be truthy for the command to match.
- `opts`: optional argument keys that may also be truthy.

### Call

```py
@commandopt(["ship", "new", "<name>"], ["--force"])
def ship_new(arguments):
    ...
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
    # select and execute the matching command in one call:
    Command.run(arguments)
    # or, to select without executing it:
    # command = Command.find(arguments)
    # command(arguments)

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

Selection looks at the **truthiness of each argument's value, not at the mere
presence of its key**. docopt returns *every* declared key on every run (each
option, present or not), so commandopt reduces that full dict to the set of keys
whose value is truthy — that active subset is what identifies the command:

```py
opts_input = frozenset(opt for opt in arguments if arguments[opt])
```

Matching is then exact over that set: every truthy argument must be accounted for
by the command's mandatory or optional options, or selection fails with
`NoCommandFoundError`.

The case to watch for is a **global / application-level argument that is truthy on
every invocation** — a flag usable with any subcommand, a counter (`-vvv` → `3`),
or an option with a non-`False` default. It lands in the selection set even though
it isn't meant to identify a command, and breaks matching:

```py
# Usage: tool [-v] add <item>
#   tool -v add foo  ->  {"-v": True, "add": True, "<item>": "foo", "remove": False}

@commandopt(["add", "<item>"])          # -v not declared
def add(arguments): ...

Command.run({"-v": True, "add": True, "<item>": "foo"})
# NoCommandFoundError: {'-v', 'add', '<item>'} is not accepted by {'add', '<item>'}
```

If the argument genuinely belongs to a command, declare it as an optional so it
falls within `M ∪ O`:

```py
@commandopt(["add", "<item>"], ["-v"])  # now '-v' is accepted
def add(arguments): ...
```

For a truly application-wide argument (`--config`, `--debug`, `-v`), declaring it
on every command is noise. Tell commandopt to **ignore** it for selection — the
matched command still receives it in full:

```py
from commandopt import Command

Command.ignored = {"--config", "--debug", "-v"}   # global default
Command.run(arguments)                            # --config no longer breaks matching

# ...or per call:
Command.run(arguments, ignore={"--config"})
```

## API reference

The public surface is exported via `__all__`:

- **`@commandopt(mandopts, opts=None, registry=None)`** — register the decorated
  function; `registry` targets a specific `Registry` (defaults to the global one).
- **`Command.find(arguments, ignore=())`** — select and return the matching
  function **without** executing it (raises `NoCommandFoundError`).
- **`Command.run(arguments, ignore=())`** — select **and execute** the matching
  function, returning its result (equivalent to `find(arguments)(arguments)`).
- **`Command.ignored`** — a settable set of application-level argument keys
  excluded from selection (see *Limitations / gotchas*).
- **`Command.list_commands()`** — return a `set` of `CommandsOpts(opts, f)`, one
  per registered command.
- **`Command.reset()`** — clear the global registry (handy for test isolation).
- **`CommandsOpts`** — a `NamedTuple` of `(opts, f)` describing one command.

### Registry

`Command` is a thin façade over a process-global default `Registry`. Instantiate
your own for an isolated set of commands — two CLIs in one process, or clean test
isolation — and pass it to the decorator:

```py
from commandopt import Registry

cli = Registry(ignore={"--config", "--debug"})

@commandopt(["add", "<item>"], registry=cli)
def add(arguments): ...

cli.run(arguments)     # same find/run/list_commands/reset API as Command
```

A `Registry` exposes `add_command`, `find`, `run`, `list_commands`, `reset`, and a
settable `ignored` set; `find`/`run` also accept a per-call `ignore`.

### Exceptions

All commandopt exceptions derive from **`CommandoptException`**:

- **`NoCommandFoundError`** — no command matched. Exposes `.opts`
  (the truthy argument keys) and `.message`.
- **`CommandCollisionError`** — two different functions accept overlapping
  argument sets. Exposes `.opts`, `.existing`, `.new`, and `.message`.

```py
from commandopt import Command, NoCommandFoundError

try:
    handler = Command.find(arguments)
except NoCommandFoundError as exc:
    print("unmatched:", sorted(exc.opts))
```


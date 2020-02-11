# commandopt
Turn a dict of arguments into cli commands, ideal companion of docopt.

## Why ?

Using the `commandopt.commandopt` decorator, you are able to declare commands to be
executed depending on the input arguments of your app.

It reduces the boilerplate code in your `main()`.

## Example usage :


```py
#myapp/myapp.py
"""Naval Fate.

Usage:
  naval_fate.py ship new <name>...
  naval_fate.py --version

Options:
  --version     Show version.

"""
from commandopt import Command
from docopt import docopt

import myapp.commands.ship

if __name__ == '__main__':
    arguments = docopt(__doc__, version='Naval Fate 2.0')
    run = Command(arguments)  # get the registered function
    run(arguments)  # execute the function
    # or
    # run = Command(arguments, call=True)

```

```py
#myapp/commands/ship.py
from commandopt import commandopt

class ShipCommand:

    @commandopt(["ship", "new", "<name>"])
    @commandopt(["ship", "new"])
    def new(arguments):
        """You can stack the decorator if you want."""
        name = arguments["<name>"] or "case when name is empty"
        # ... your code here
```

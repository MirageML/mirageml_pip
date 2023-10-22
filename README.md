# MirageML Python Library

The MirageML Python Library provides a convenient interface to run AI in the terminal using your files or web documentation as context.

## Installation

This requires Python 3.9 or later. Install the package with:

```
pip install -U mirageml
```

## Commands
```
mirage [OPTIONS] COMMAND [ARGS]
```
```
╭─ Options ─────────────────────────────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                                               │
╰───────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ────────────────────────────────────────────────────────────────────────────────╮
│ chat   Chat with MirageML                                                                 │
│ login  Login to MirageML                                                                  │
╰───────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Manage Source ───────────────────────────────────────────────────────────────────────────╮
│ add     Add a new source                                                                  │
│ delete  Delete sources                                                                    │
│ list    List sources                                                                      │
│ sync    Sync sources                                                                      │
╰───────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Utils and Configs ───────────────────────────────────────────────────────────────────────╮
│ config  Manage the config                                                                 │
╰───────────────────────────────────────────────────────────────────────────────────────────╯
```

## Chat Commands
```
mirage chat [OPTIONS]
```
```
╭─ Options ─────────────────────────────────────────────────────────────────────────────────╮
│ --files    -f      TEXT  Path to files/directories to use as context.                     │
│                                                                                           │
│                          mirage chat -f {filepath}                                        │
│                          [default: None]                                                  │
│ --urls     -u      TEXT  URLs to use as context.                                          │
│                                                                                           │
│                          mirage chat -u {url}                                             │
│                          [default: None]                                                  │
│ --sources  -s      TEXT  Specify sources to use as context:                               │
│                                                                                           │
│                          Ex: mirage chat -s disney-robot                                  │
│                                                                                           │
│                          Sources:                                                         │
│                                                                                           │
│                           • disney-robot                                                  │
│ --help                   Show this message and exit.                                      │
╰───────────────────────────────────────────────────────────────────────────────────────────╯
```

## Support
Send an email to [support@mirageml.com](mailto:support@mirageml.com) for support.

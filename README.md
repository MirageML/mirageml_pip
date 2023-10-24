# MirageML Python Library

The MirageML Python Library provides a convenient interface to run AI in the terminal using your files or web documentation as context.

## Installation

This requires Python 3.9 or later. Install the package with:

```
pip install -U mirageml
```

## Usage
You can use 'mirageml', 'mirage', or 'mml' to call the package.
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

## Contributing
If you want to contribute to MirageML, follow these steps:

1. Fork the repository: Click on the 'Fork' button at the top right corner of the repository page on GitHub.
2. Clone the forked repository to your local machine. `git clone https://github.com/<user_name>/mirageml_pip.git`
3. Create a new branch for your changes: `git checkout -b <user_name>/your-branch-name`
4. Review the [CONTRIBUTING.md](CONTRIBUTING.md) file for details on installing pip pacakages, testing, and linting.
4. Make your changes in this branch.
5. Commit your changes: `git commit -m "Your commit message"`
6. Push your changes to your forked repository: `git push origin your-branch-name`
7. Create a Pull Request: Go to your forked repository on GitHub and click on 'New Pull Request'.

Please provide a clear and concise description of your changes in the pull request description.


## Support
Send an email to [support@mirageml.com](mailto:support@mirageml.com) for support.

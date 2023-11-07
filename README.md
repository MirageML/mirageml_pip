# MirageML Python Library

The MirageML Python Library provides a convenient interface to run AI in the terminal using your files or web documentation as context.

## Installation

This requires Python 3.9 or later. Install the package with:

```
pip install -U mirageml
```

## Tutorial
You can run `mirage tutorial` to get started with MirageML. This will walk you through the process of creating a source, adding files to it, and using it to chat with MirageML.

## Usage
You can use 'mirageml', 'mirage', or 'mml' to call the package.
```
mirage [OPTIONS] COMMAND [ARGS]
```
```
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                                  │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ───────────────────────────────────────────────────────────────────╮
│ chat      Chat with MirageML                                                 │
│ login     Login to Mirage ML                                                 │
│ tutorial  Walk through the basics of using mirageml                          │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Manage Resources ───────────────────────────────────────────────────────────╮
│ add     Add a new resource                                                   │
│ delete  Delete resources                                                     │
│ list    List resources                                                       │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Utils and Configs ──────────────────────────────────────────────────────────╮
│ config  Manage the config                                                    │
╰──────────────────────────────────────────────────────────────────────────────╯
```

## Chat Commands
```
mirage chat [OPTIONS]
```
```
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --files          -f       TEXT  Path to files/directories to use as context. │
│                                                                              │
│                                 mml chat -f {filepath} -f {directory}        │
│                                 [default: None]                              │
│ --urls           -u       TEXT  URLs to use as context.                      │
│                                                                              │
│                                 mml chat -u {url1} -u {url2}                 │
│                                 [default: None]                              │
│ --sources        -s       TEXT  Specify sources:                             │
│                                                                              │
│                                 Ex: mml chat -s modal -s electronjs          │
│                                                                              │
│                                 Sources:                                     │
│                                                                              │
│                                  • modal                                     │
│                                  • electronjs                                │
│                                  • notion                                    │
│                                 [default: None]                              │
│ --system-prompt  -sp      TEXT  Name of the system prompt to use             │
│                                 [default: None]                              │
│ --help                          Show this message and exit.                  │
╰──────────────────────────────────────────────────────────────────────────────╯
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

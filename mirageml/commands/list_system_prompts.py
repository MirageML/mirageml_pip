import json

import typer

from .config import load_config


def list_system_prompts():
    config = load_config()
    if len(config["system_prompts"]) == 0:
        typer.secho("No System Prompts. Add one with 'mirageml add sp'", fg=typer.colors.BRIGHT_RED, bold=True)
    else:
        typer.secho("System Prompts:", fg=typer.colors.BRIGHT_GREEN, bold=True)
        print(json.dumps(config["system_prompts"], indent=4))

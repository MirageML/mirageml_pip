import typer

from .config import delete_var_config


def delete_system_prompt(args):
    name = args["name"]
    if not name:
        name = typer.prompt("Name")

    delete_var_config("system_prompts", name)
    typer.secho(f"Deleted system prompt: {name}", fg=typer.colors.BRIGHT_GREEN, bold=True)

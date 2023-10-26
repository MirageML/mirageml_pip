import typer

from .config import append_var_config


def fix_name(name):
    if name.startswith("http"):
        name = "_".join(name.split("/")[1:])

    name = name.replace(" ", "_")
    name = name.replace("/", "_")
    if name.startswith("_") or name.startswith("/"):
        name = name[1:]
    return name


def add_system_prompt(args):
    name = args["name"]
    if not name:
        name = typer.prompt("Name")
    name = fix_name(name)
    prompt = typer.prompt("Prompt")
    sp = {"name": name, "prompt": prompt}
    append_var_config("system_prompts", sp)
    typer.secho(f"Added system prompt: {name}", fg=typer.colors.BRIGHT_GREEN, bold=True)

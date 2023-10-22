import os
import json
import typer


def show_config():
    config = load_config()
    from rich import print

    print(json.dumps(config, indent=4))


def load_config():
    config_path = os.path.expanduser("~/.mirageml.json")
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            return json.load(f)
    return {"local_mode": False, "model": "gpt-4"}


def save_config(config):
    config_path = os.path.expanduser("~/.mirageml.json")
    with open(config_path, "w") as f:
        json.dump(config, f, indent=4)


def set_config():
    config = load_config()

    valid = {
        "local_mode": (("True", "False"), json.loads),
        "model": (("gpt-3.5-turbo", "gpt-4"), str),
    }

    for key, value in config.items():
        curvalue = value
        while True:
            question = f"Enter the value for '{key}' [{', '.join(valid[key][0])}] (current value: {curvalue}): "
            value = input(question)
            if value == "":
                break
            if value not in valid[key][0]:
                typer.secho(
                    f"Invalid value for '{key}'. Please use one of these options {valid[key][0]}",
                    fg=typer.colors.BRIGHT_RED,
                )
                continue
            config[key] = valid[key][1](value.lower())
            save_config(config)
            break

    typer.secho("MirageML Config updated!", fg=typer.colors.BRIGHT_GREEN)
    show_config()


def set_var_config(json_data):
    config = load_config()
    for key, value in json_data.items():
        config[key] = value
    save_config(config)

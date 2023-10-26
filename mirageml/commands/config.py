import json
import os

import typer


def show_config():
    config = load_config()
    from rich import print

    print(json.dumps(config, indent=4))


def load_config():
    config_path = os.path.expanduser("~/.mirageml.json")
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            curr_config = json.load(f)
    curr_config = {
        "local_mode": curr_config.get("local_mode", False),
        "model": curr_config.get("model", "gpt-4"),
        "keep_files_local": curr_config.get("keep_files_local", True),
        "local": curr_config.get("local", []),
        "remote": curr_config.get("remote", []),
    }
    save_config(curr_config)
    return curr_config


def save_config(config):
    config_path = os.path.expanduser("~/.mirageml.json")
    with open(config_path, "w") as f:
        json.dump(config, f, indent=4)


def set_config():
    config = load_config()

    valid = {
        "local_mode": (("True (not recommended without GPU)", "False"), json.loads),
        "model": (("gpt-3.5-turbo", "gpt-4"), str),
        "keep_files_local": (("True", "False"), json.loads),
    }

    for key, value in config.items():
        if key not in valid:
            continue
        curvalue = value
        while True:
            question = f"Enter the value for '{key}' [{', '.join(valid[key][0])}] (current value: {curvalue}): "
            value = input(question)
            if value == "":
                break
            if value not in [x.split()[0] for x in valid[key][0]]:
                typer.secho(
                    f"Invalid value for '{key}'. Please use one of these options {[x.split()[0] for x in valid[key][0]]}",
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

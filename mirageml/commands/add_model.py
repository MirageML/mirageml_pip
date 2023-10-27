import os
import typer
import keyring
import requests

from ..constants import SERVICE_ID, FINETUNE_CREATE_ENDPOINT, get_headers

def fix_name(name):
    if name.startswith("http"):
        name = "-".join(name.split("/")[1:])

    name = name.replace(" ", "-")
    name = name.replace("/", "-")
    if name.startswith("_") or name.startswith("/"):
        name = name[1:]
    return name


def add_model(model_name, link):
    from .list_models import get_models
    model_name = fix_name(model_name)

    if model_name in get_models():
        typer.secho(f"Model {model_name} already exists", fg=typer.colors.RED, bold=True)
        return

    user_id = keyring.get_password(SERVICE_ID, "user_id")
    json_data = {"user_id": user_id, "finetune_model_name": model_name, "links": [link]}
    requests.post(FINETUNE_CREATE_ENDPOINT, json=json_data, headers=get_headers())
    return True


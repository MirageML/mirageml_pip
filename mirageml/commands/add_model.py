import keyring
import requests
import typer

from ..constants import FINETUNE_CREATE_ENDPOINT, SERVICE_ID, get_headers
from .config import load_config


def fix_name(name):
    if name.startswith("http"):
        name = "-".join(name.split("/")[1:])

    name = name.replace(" ", "-")
    name = name.replace("/", "-")
    if name.startswith("_") or name.startswith("/"):
        name = name[1:]
    return name


def add_model(model_name, links):
    from .list_models import get_models

    model_name = fix_name(model_name)

    if model_name in get_models():
        typer.secho(f"Model {model_name} already exists", fg=typer.colors.RED, bold=True)
        return

    user_id = keyring.get_password(SERVICE_ID, "user_id")

    json_data = {"user_id": user_id, "finetune_model_name": model_name, "links": links}
    requests.post(FINETUNE_CREATE_ENDPOINT, json=json_data, headers=get_headers())
    typer.secho(
        f"Creating Finetuned Model: {model_name}. You will receive an email once its ready!",
        fg=typer.colors.GREEN,
        bold=True,
    )
    return True

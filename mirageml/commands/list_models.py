import sys

import keyring
import requests
import typer

from mirageml.constants import SERVICE_ID, SUPABASE_KEY, SUPABASE_URL


def get_models():
    access_token = keyring.get_password(SERVICE_ID, "access_token")
    user_id = keyring.get_password(SERVICE_ID, "user_id")
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/user_finetunes?user_id=eq.{user_id}&select=model_name", headers=headers
    )

    response_data = response.json()
    model_names = []
    if len(response_data) > 0:
        model_names = [data["model_name"] for data in response_data]

    return model_names


def set_models(models=None):
    from .config import set_var_config

    if not models:
        models = get_models()

    set_var_config({"custom_models": get_models()})


def list_models():
    models = get_models()

    if len(models) == 0:
        typer.secho(
            f"No custom models found. Please add a source using {sys.argv[0].split('/')[-1]} add model",
            fg=typer.colors.RED,
            bold=True,
        )
        return

    if len(models) != 0:
        typer.secho("Custom Models:", fg=typer.colors.BRIGHT_GREEN, bold=True)
        print("* " + "\n* ".join(models))

    set_models(models)

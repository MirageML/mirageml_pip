import sys
import typer
import keyring
from ..constants import (
    supabase,
    SERVICE_ID
)


def get_models():
    user_id = keyring.get_password(SERVICE_ID, "user_id")
    response = supabase.table("user_finetunes").select("model_name").eq("user_id", user_id).execute()
    model_names = []
    if len(response.data) > 0:
        model_names = [data["model_name"] for data in response.data]

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

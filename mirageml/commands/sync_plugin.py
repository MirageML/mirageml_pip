import keyring
import requests
import typer

from ..constants import SERVICE_ID, GMAIL_SYNC_ENDPOINT, NOTION_SYNC_ENDPOINT

def sync_plugin(args):
    plugin_name = args["plugin"]
    if plugin_name == "notion":
        notion_provider_token = keyring.get_password(SERVICE_ID, "notion_provider_token")
        if not notion_provider_token:
            typer.secho(
                "Please add the notion plugin first. Run `mirageml add plugin notion`",
                fg=typer.colors.BRIGHT_RED,
                bold=True,
            )
            return
        access_token = keyring.get_password(SERVICE_ID, "access_token")
        headers = {
            "Authorization": f"Bearer {access_token}",
        }
        sync_response = requests.post(NOTION_SYNC_ENDPOINT, json={}, headers=headers)
        sync_response_data = sync_response.json()
        if "error" in sync_response_data:
            typer.secho(sync_response_data["error"], fg=typer.colors.BRIGHT_RED, bold=True)
        else:
            typer.secho(
                "Syncing notion triggered successfully. You will receive an email when the sync is complete.",
                fg=typer.colors.BRIGHT_GREEN,
                bold=True,
            )
    elif plugin_name == "gmail":
        gmail_provider_token = keyring.get_password(SERVICE_ID, "gmail_provider_token")
        if not gmail_provider_token:
            typer.secho(
                "Please add the gmail plugin first. Run `mirageml add plugin gmail`",
                fg=typer.colors.BRIGHT_RED,
                bold=True,
            )
            return
        access_token = keyring.get_password(SERVICE_ID, "access_token")
        headers = {
            "Authorization": f"Bearer {access_token}",
        }
        sync_response = requests.post(GMAIL_SYNC_ENDPOINT, json={}, headers=headers)
        typer.secho("Syncing gmail triggered successfully.", fg=typer.colors.BRIGHT_GREEN, bold=True)

    else:
        typer.secho(
            "Only notion and gmail plugins is supported for now.",
            fg=typer.colors.BRIGHT_RED,
            bold=True,
        )
        return

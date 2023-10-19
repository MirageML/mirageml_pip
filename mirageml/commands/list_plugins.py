import keyring
import requests
import typer

from mirageml.constants import SERVICE_ID, SUPABASE_URL, SUPABASE_KEY

plugin_mapping = {
    "google_token": "gdrive",
    "notion_token": "notion",
}

def list_plugins():
    access_token = keyring.get_password(SERVICE_ID, 'access_token')
    user_id = keyring.get_password(SERVICE_ID, 'user_id')
    params = { "input_user_id": user_id }
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    response = requests.post(f"{SUPABASE_URL}/rest/v1/rpc/user_plugins", json=params, headers=headers)
    response_data = response.json()[0]
    connected_plugin_string = "Connected plugins: "
    for key in response_data:
        if (response_data[key]):
            connected_plugin_string += f"{plugin_mapping[key]}, "
    typer.secho(connected_plugin_string[:-2], fg=typer.colors.BRIGHT_GREEN, bold=True)
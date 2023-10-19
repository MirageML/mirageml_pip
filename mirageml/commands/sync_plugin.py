import keyring
import requests
from mirageml.constants import SERVICE_ID, NOTION_SYNC_ENDPOINT

def sync_plugin(args):
    plugin_name = args["plugin"]
    if plugin_name == "notion":
        notion_provider_token = keyring.get_password(SERVICE_ID, "notion_provider_token")
        if not notion_provider_token:
            print("Please add the notion plugin first. Run `mirageml add plugin notion`")
            return
        else:
            access_token = keyring.get_password(SERVICE_ID, "access_token")
            headers = {
                "Authorization": f"Bearer {access_token}",
            }
            sync_response = requests.post(NOTION_SYNC_ENDPOINT, json={}, headers=headers)
            sync_response_data = sync_response.json()
            if "error" in sync_response_data:
                print(sync_response_data["error"])
            else:
                print("Syncing notion triggered successfully. You will receive an email when the sync is complete.")
    else:
        print("Only notion plugin syncing is supported for now.")
        return

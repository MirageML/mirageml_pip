import keyring
import requests

from mirageml.constants import SERVICE_ID
from mirageml.index_handlers import index_notion

def sync_plugin(args):
    plugin_name = args["plugin"]
    if plugin_name != "notion":
        print("Only notion plugin syncing is supported for now.")
        return

    notion_provider_token = keyring.get_password(SERVICE_ID, "notion_provider_token")
    if not notion_provider_token:
        print("Please add the notion plugin first. Run `mirageml add plugin notion`")
        return

    index_notion(notion_provider_token)
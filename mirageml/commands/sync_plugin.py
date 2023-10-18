import keyring

from mirageml.constants import SERVICE_ID
from mirageml.classes import Notion

def sync_plugin(args):
    plugin_name = args["plugin"]
    if plugin_name == "notion":
        notion_provider_token = keyring.get_password(SERVICE_ID, "notion_provider_token")
        if not notion_provider_token:
            print("Please add the notion plugin first. Run `mirageml add plugin notion`")
            return
        else:
            n = Notion(notion_provider_token)
            n.sync()
    else:
        print("Only notion plugin syncing is supported for now.")
        return

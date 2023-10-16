

from mirageml import constants
from mirageml.classes import LoginManager

supabase = constants.supabase

def add_gdrive():
    m = LoginManager(
        handler="google_auth_handler",
        provider="google",
        provider_options={
            "redirect_to": constants.REDIRECT_URI,
            "scopes": "https://www.googleapis.com/auth/drive",
            "query_params": {
                "access_type": "offline",
                "prompt": "consent",
            }
        }
    )
    m.start_web_server()
    m.open_browser()

def add(args):
    plugin_name = args["plugin"]
    if plugin_name == "gdrive":
        add_gdrive()
    else:
        print("Plugin not support. Supported plugins: gdrive")
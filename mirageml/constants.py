from supabase import create_client

SERVICE_ID = "mirageml"

PORT = 9998
REDIRECT_URI = f"http://localhost:{PORT}/callback"
LINEAR_CLIENT_ID="80f64bdfc3e08d68d379b170d93f1390"
LINEAR_SCOPE="read,write,issues:create,comments:create"
LINEAR_AUTHORIZATION_URL=f"https://linear.app/oauth/authorize?client_id={LINEAR_CLIENT_ID}&scope={LINEAR_SCOPE}&redirect_uri={REDIRECT_URI}&response_type=code&prompt=consent"
LINEAR_TOKEN_ENDPOINT=""
SUPABASE_URL = "https://kfskvbhwrwpbruczecka.supabase.co"
SUPABASE_KEY = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
    "eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtmc2t2Ymh3cndwYnJ1Y"
    "3plY2thIiwicm9sZSI6ImFub24iLCJpYXQiOjE2OTcwNTI5MDYsImV4cCI6MjAxMjYyODkwNn0."
    "KZoU1QMfvh72QfKJK_HD3EQ_246g-QbggSzPbT83Su8"
)
NOTION_SYNC_ENDPOINT = " https://mirageml--notion-sync-trigger-notion-sync.modal.run"
ANALYTICS_WRITE_KEY = "WeKYF6EZAYtVxUwlx8g3sG1JKDMMv6jY"

WEB_SCRAPE_LINKS_ENDPOINT = "https://mirageml--web-scraper-recursive-links.modal.run"
WEB_SCRAPE_EXTRACT_ENDPOINT = "https://mirageml--web-scraper-extract-from-url.modal.run"

VECTORDB_EMBED_ENDPOINT = "https://mirageml--vectordb-embed-text.modal.run"
LLM_GPT_ENDPOINT = "https://mirageml--llm-gpt.modal.run"

VECTORDB_SEARCH_ENDPOINT = "https://mirageml--vectordb-search-db.modal.run"
VECTORDB_LIST_ENDPOINT = "https://mirageml--vectordb-list-db.modal.run"
VECTORDB_CREATE_ENDPOINT = "https://mirageml--vectordb-create-db.modal.run"
VECTORDB_UPSERT_ENDPOINT = "https://mirageml--vectordb-upsert-db.modal.run"
VECTORDB_DELETE_ENDPOINT = "https://mirageml--vectordb-delete-db.modal.run"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def fetch_new_access_token():
    import keyring

    refresh_token = keyring.get_password(SERVICE_ID, "refresh_token")
    response = supabase.auth._refresh_access_token(refresh_token)
    session = response.session
    keyring.set_password(SERVICE_ID, "access_token", session.access_token)
    keyring.set_password(SERVICE_ID, "refresh_token", session.refresh_token)
    keyring.set_password(SERVICE_ID, "expires_at", str(session.expires_at))
    return session.access_token


def get_headers():
    import time

    import keyring
    import typer

    expires_at = keyring.get_password(SERVICE_ID, "expires_at")
    access_token = keyring.get_password(SERVICE_ID, "access_token")
    if expires_at and float(expires_at) < time.time():
        try:
            refresh_token = keyring.get_password(SERVICE_ID, "refresh_token")
            response = supabase.auth._refresh_access_token(refresh_token)
            session = response.session
            keyring.set_password(SERVICE_ID, "access_token", session.access_token)
            keyring.set_password(SERVICE_ID, "refresh_token", session.refresh_token)
            keyring.set_password(SERVICE_ID, "expires_at", str(session.expires_at))
            access_token = session.access_token
        except Exception as e:
            print(e)
            typer.echo("Please login again. Run `mirageml login`")
            raise typer.Exit()
    headers = {"Authorization": f"Bearer {access_token}"}
    return headers


def help_list_sources(command_prompt):
    import json
    import os
    import sys

    invoked_alias = sys.argv[0].split("/")[-1]  # Extract only the alias name

    config_path = os.path.expanduser("~/.mirageml.json")
    config = {}
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            config = json.load(f)

    local_sources = config.get("local", [])
    remote_sources = config.get("remote", [])
    all_sources = list(set(local_sources + remote_sources))
    if len(all_sources) == 0:
        final_string = (
            f"Specify sources to delete:\n\n\nEx: " f"**{invoked_alias} {command_prompt} {{source1}}**\n\n\n\n"
        )
    elif len(all_sources) == 1:
        final_string = (
            f"Specify sources to delete:\n\n\nEx: " f"**{invoked_alias} {command_prompt} {all_sources[0]}**\n\n\n\n"
        )
    else:
        command_flag = "-s " if command_prompt.split()[0] == "chat" else ""
        final_string = (
            f"Specify sources to delete:\n\n\nEx: "
            f"**{invoked_alias} {command_prompt} {all_sources[0]} "
            f"{command_flag}{all_sources[1]}**\n\n\n\n"
        )

    if len(all_sources) != 0:
        final_string += "**Sources:**\n\n* "
        final_string += "\n\n* ".join(all_sources)
    return final_string

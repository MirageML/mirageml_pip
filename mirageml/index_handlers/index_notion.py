import requests
from mirageml.constants import NOTION_API_URL, NOTION_VERSION

def index_notion(provider_token):
    print(NOTION_API_URL, NOTION_VERSION)
    print("indexing notion pages, please wait...")
    headers = {
        "Authorization": f"Bearer {provider_token}",
        "Content-Type": "application/json",
        "Notion-Version": NOTION_VERSION,
    }
    response = requests.post(f"{NOTION_API_URL}/v1/search", json={}, headers=headers)
    print(response.json())
from supabase import create_client

SERVICE_ID = "mirageml"

PORT = 9998
REDIRECT_URI = f"http://localhost:{PORT}/callback"
SUPABASE_URL = "https://kfskvbhwrwpbruczecka.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtmc2t2Ymh3cndwYnJ1Y3plY2thIiwicm9sZSI6ImFub24iLCJpYXQiOjE2OTcwNTI5MDYsImV4cCI6MjAxMjYyODkwNn0.KZoU1QMfvh72QfKJK_HD3EQ_246g-QbggSzPbT83Su8"
NOTION_SYNC_ENDPOINT = " https://mirageml--notion-sync-trigger-notion-sync.modal.run"
ANALYTICS_WRITE_KEY = "WeKYF6EZAYtVxUwlx8g3sG1JKDMMv6jY"

VECTORDB_EMBED_ENDPOINT = "https://mirageml--vectordb-embed-text.modal.run"
LLM_GPT_ENDPOINT = "https://mirageml--llm-gpt.modal.run"

VECTORDB_SEARCH_ENDPOINT = 'https://mirageml--vectordb-search-db.modal.run'
VECTORDB_LIST_ENDPOINT = "https://mirageml--vectordb-list-db.modal.run"
VECTORDB_CREATE_ENDPOINT = "https://mirageml--vectordb-create-db.modal.run"
VECTORDB_DELETE_ENDPOINT = "https://mirageml--vectordb-delete-db.modal.run"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_headers():
    import keyring
    access_token = keyring.get_password(SERVICE_ID, 'access_token')
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    return headers
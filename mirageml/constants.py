from supabase import create_client

SERVICE_ID = "mirageml"

PORT = 9998
REDIRECT_URI = f"http://localhost:{PORT}/callback"
SUPABASE_URL = "https://kfskvbhwrwpbruczecka.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtmc2t2Ymh3cndwYnJ1Y3plY2thIiwicm9sZSI6ImFub24iLCJpYXQiOjE2OTcwNTI5MDYsImV4cCI6MjAxMjYyODkwNn0.KZoU1QMfvh72QfKJK_HD3EQ_246g-QbggSzPbT83Su8"
NOTION_SYNC_ENDPOINT = " https://mirageml--notion-sync-trigger-notion-sync.modal.run"


supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
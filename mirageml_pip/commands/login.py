import webbrowser
import requests

SUPABASE_URL = "https://kfskvbhwrwpbruczecka.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtmc2t2Ymh3cndwYnJ1Y3plY2thIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTY5NzA1MjkwNiwiZXhwIjoyMDEyNjI4OTA2fQ.HhMCQvmOHFo13E2fCBDXtm9KEZZOPvQ41jnz6MCJ3Rk"

def google_login():
    # Construct the Supabase Google login URL
    auth_url = f"{SUPABASE_URL}/auth/v1/authorize?provider=google&redirect_to=http://mirageml.com"

    # Open the authentication URL in the user's browser
    webbrowser.open(auth_url)

    # Ask the user to paste the redirect URL after logging in with Google
    print("Please copy the full redirect URL from the browser after logging in and paste it here.")
    redirect_url = input("Enter the redirect URL: ")

    # Extract the access token from the redirect URL
    token = extract_token_from_url(redirect_url)
    if token:
        print("Logged in successfully!")
        # You can save this token and use it for making authenticated Supabase API calls
        return token
    else:
        print("Failed to log in.")
        return None

def extract_token_from_url(url):
    # Simple parsing to get the access token from the redirect URL
    token_prefix = "access_token="
    if token_prefix in url:
        token = url.split(token_prefix)[-1].split("&")[0]
        return token
    return None


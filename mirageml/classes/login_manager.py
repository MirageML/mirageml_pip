import http.server
import threading
import platform
import subprocess
import sys
import keyring
import jwt
import urllib.parse
import requests

from mirageml.constants import SERVICE_ID, PORT, supabase, SUPABASE_KEY, SUPABASE_URL

class LoginManager:
  def __init__(self, handler="mirage_auth_handler", provider="google", provider_options={}):
    self._server = None
    self._thread = None
    self._handler = handler
    self._provider = provider
    self._provider_options = provider_options

  def start_web_server(self):
    """Kick off a thread for the local webserver."""
    th = threading.Thread(target=self._start_local_server)
    th.start()
    self._thread = th

  def select_handler(self):
    if self._handler == "mirage_auth_handler":
      return Handler
    elif self._handler == "google_auth_handler":
      return GoogleHandler

  def _start_local_server(self):
    self._server = http.server.HTTPServer(('localhost', PORT), self.select_handler())
    self._server.serve_forever()

  def open_browser(self):
    """Opens the browser to the login page."""
    # Waits for the server to start.
    while self._server is None:
        oauth_response = supabase.auth.sign_in_with_oauth({
           "provider": self._provider,
           "options": self._provider_options,
        })
        url = oauth_response.url
        system = platform.system()
        if system == 'Darwin':
            cmd = ['open', url]
        elif system == 'Linux':
            cmd = ['xdg-open', url]
        elif system == 'Windows':
            cmd = ['cmd', '/c', 'start', url.replace('&', '^&')]
        else:
            raise RuntimeError(f'Unsupported system: {system}')
        subprocess.run(cmd, check=True)

class Handler(http.server.SimpleHTTPRequestHandler):
  """Handle the response from accounts.google.com."""

  # Sketchy static variable to hold response.
  info = None

  def log_message(self, format, *args):
    return
    # return super().log_message(format, *args)

  def update_keyring(self, info):
    access_token = info['access_token']
    decoded = jwt.decode(access_token, algorithms=["HS256"], options={ "verify_signature": False })
    keyring.set_password(SERVICE_ID, 'access_token', info['access_token'])
    keyring.set_password(SERVICE_ID, 'refresh_token', info['refresh_token'])
    keyring.set_password(SERVICE_ID, 'expires_at', info['expires_at'])
    keyring.set_password(SERVICE_ID, 'user_id', decoded["sub"])
    keyring.set_password(SERVICE_ID, 'email', decoded["email"])
    return access_token, decoded["sub"]

  def callback_handler(self):
    self.send_response(200)
    self.send_header('Content-type', 'text/html')
    self.end_headers()
    # Serve an HTML page with JavaScript to send the fragment to the server
    self.wfile.write(b"""
    <html>
        <body>
            <script>
                // Send the fragment to the server
                fetch('/capture_fragment?' + location.hash.substr(1))
                .then(() => {
                    document.body.innerHTML = 'All set, feel free to close this tab';
                    window.close();
                });
            </script>
        </body>
    </html>
    """)

  def capture_fragment_handler(self):
    self.send_response(200)
    self.send_header('Content-type', 'text/html')
    self.end_headers()
    self.wfile.write(b'All set, feel free to close this tab')
    # parse the fragment for the access token and refresh token
    fragment = self.path.split('?')[1]
    info = dict(kv.split('=') for kv in fragment.split('&'))
    self.update_keyring(info)
    sys.exit(0)

  def do_GET(self):
    if self.path.startswith("/callback"):
      self.callback_handler()
    elif self.path.startswith("/capture_fragment"):
      self.capture_fragment_handler()

class GoogleHandler(Handler):

  def capture_fragment_handler(self):
    self.send_response(200)
    self.send_header('Content-type', 'text/html')
    self.end_headers()
    self.wfile.write(b'All set, feel free to close this tab')
    # parse the fragment for the access token and refresh token
    fragment = self.path.split('?')[1]
    info = dict(kv.split('=') for kv in fragment.split('&'))
    access_token, user_id = self.update_keyring(info)

    provider_token = info['provider_token']
    provider_refresh_token = urllib.parse.unquote(info['provider_refresh_token'])

    if provider_token and provider_refresh_token:
      params = {
        "user_id": user_id,
        "provider_token": provider_token,
        "provider_refresh_token": provider_refresh_token,
      }
      headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates",
      }
      requests.post(f"{SUPABASE_URL}/rest/v1/user_google_tokens", json=params, headers=headers)


    sys.exit(0)

  def do_GET(self):
    if self.path.startswith("/callback"):
      self.callback_handler()
    elif self.path.startswith("/capture_fragment"):
      self.capture_fragment_handler()
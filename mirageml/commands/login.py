import http.server
import threading
import platform
import subprocess
import sys
import time
import keyring
import jwt

from mirageml import constants

SERVICE_ID = constants.SERVICE_ID
PORT = constants.PORT
REDIRECT_URI = constants.REDIRECT_URI
supabase = constants.supabase

class LoginManager:
  def __init__(self):
    self._server = None
    self._thread = None

  def stop_web_server(self):
    """Stop the local web server."""
    if self._server:
        self._server.shutdown()
        self._server.server_close()

  def start_web_server(self):
    """Kick off a thread for the local webserver."""
    th = threading.Thread(target=self._start_local_server)
    th.start()

  def _start_local_server(self):
    self._server = http.server.HTTPServer(('localhost', PORT), Handler)
    print(f'Serving on port {PORT}')
    self._server.serve_forever()

  def open_browser(self):
    """Opens the browser to the login page."""
    # Waits for the server to start.
    while self._server is None:
        time.sleep(1)
        oauth_response = supabase.auth.sign_in_with_oauth({
            "provider": "google",
            "options": {
                "redirect_to": REDIRECT_URI
            }
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

  def do_GET(self):
    if self.path.startswith("/callback"):
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
                        setTimeout(() => window.close(), 1000);
                    });
                </script>
            </body>
        </html>
        """)
    elif self.path.startswith("/capture_fragment"):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b'All set, feel free to close this tab')
        # parse the fragment for the access token and refresh token
        fragment = self.path.split('?')[1]
        info = dict(kv.split('=') for kv in fragment.split('&'))
        access_token = info['access_token']
        decoded = jwt.decode(access_token, algorithms=["HS256"], options={ "verify_signature": False })
        keyring.set_password(SERVICE_ID, 'access_token', info['access_token'])
        keyring.set_password(SERVICE_ID, 'refresh_token', info['refresh_token'])
        keyring.set_password(SERVICE_ID, 'user_id', decoded["sub"])
        keyring.set_password(SERVICE_ID, 'email', decoded["email"])
        sys.exit(0)


def is_header(info):
  return 'alg' in info and 'typ' in info

def login():
  m = LoginManager()
  m.start_web_server()
  m.open_browser()

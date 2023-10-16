from mirageml.classes import LoginManager
from mirageml.constants import REDIRECT_URI

def login():
  m = LoginManager(
     provider="google",
     provider_options={
      "redirect_to": REDIRECT_URI,
      'query_params': {
        'access_type': 'offline',
        'prompt': 'consent',
      }
    }
  )
  m.start_web_server()
  m.open_browser()

from app.config import oauth_config
import urllib.parse

def generate_google_oauth_redirect_uri():
    query_params = {
        "client_id": oauth_config.OAUTH_CLIENT_ID,
        "redirect_uri": "http://localhost/auth/google",
        "response_type": "code",
        "scope": " ".join(oauth_config.OAUTH_SCOPES),
    }

    query_string = urllib.parse.urlencode(query_params, quote_via=urllib.parse.quote)
    base_url = "https://accounts.google.com/o/oauth2/v2/auth"
    return f"{base_url}?{query_string}"
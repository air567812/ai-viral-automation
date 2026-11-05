"""
1-Click Automated YouTube OAuth Connector.
Runs locally, opens your browser directly to Google sign-in,
captures the refresh token automatically, and uploads it to GitHub Secrets.
"""
import os
import sys
import json
import base64
import urllib.parse
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
from nacl import encoding, public

GITHUB_OWNER = "air567812"
GITHUB_REPO = "ai-viral-automation"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

auth_code = None

class OAuthCallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)

        if "code" in params:
            auth_code = params["code"][0]
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            html = """
            <html>
            <body style="font-family: sans-serif; text-align: center; padding: 50px; background: #0f172a; color: white;">
                <h1 style="color: #22c55e;">&#10004; YouTube Connected Successfully!</h1>
                <p>You can close this tab now. Your token has been captured and uploaded to GitHub.</p>
            </body>
            </html>
            """
            self.wfile.write(html.encode("utf-8"))
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Authorization failed.")

    def log_message(self, format, *args):
        pass  # Quiet logging

def encrypt_secret(public_key_str: str, secret_value: str) -> str:
    public_key = public.PublicKey(public_key_str.encode("utf-8"), encoding.Base64Encoder())
    sealed_box = public.SealedBox(public_key)
    encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
    return base64.b64encode(encrypted).decode("utf-8")

def update_github_secret(name: str, value: str):
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    key_url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/actions/secrets/public-key"
    r = requests.get(key_url, headers=headers)
    if r.status_code != 200:
        print(f"Failed to fetch GitHub public key: {r.status_code}")
        return False
    key_data = r.json()
    encrypted_val = encrypt_secret(key_data["key"], value)
    put_url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/actions/secrets/{name}"
    resp = requests.put(put_url, headers=headers, json={"encrypted_value": encrypted_val, "key_id": key_data["key_id"]})
    return resp.status_code in [201, 204]

def main():
    print("==================================================================")
    print("      1-CLICK AUTOMATED YOUTUBE OAUTH CONNECTOR                   ")
    print("==================================================================")
    
    # Read client_id and client_secret
    client_id = input("\nEnter your Google Client ID: ").strip()
    client_secret = input("Enter your Google Client Secret: ").strip()

    if not client_id or not client_secret:
        print("Error: Client ID and Client Secret cannot be empty!")
        sys.exit(1)

    port = 8080
    redirect_uri = f"http://localhost:{port}/"

    # Start local server to capture the OAuth redirect
    server = HTTPServer(("localhost", port), OAuthCallbackHandler)
    server.timeout = 120

    # Build Google OAuth URL
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "https://www.googleapis.com/auth/youtube.upload",
        "access_type": "offline",
        "prompt": "consent"
    }
    auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urllib.parse.urlencode(params)}"

    print("\nOpening your default browser for Google sign-in...")
    print("If it does not open automatically, open this URL:\n", auth_url)
    webbrowser.open(auth_url)

    print("\nWaiting for you to click 'Allow' in your browser...")
    while not auth_code:
        server.handle_request()

    print("\n[1/3] Authorization code received from Google!")

    # Exchange code for refresh token
    token_resp = requests.post("https://oauth2.googleapis.com/token", data={
        "client_id": client_id,
        "client_secret": client_secret,
        "code": auth_code,
        "grant_type": "authorization_code",
        "redirect_uri": redirect_uri
    }).json()

    refresh_token = token_resp.get("refresh_token")
    if not refresh_token:
        print(f"Error exchanging token: {token_resp}")
        sys.exit(1)

    print("[2/3] Successfully generated Refresh Token!")

    # Update GitHub Secrets automatically
    print("[3/3] Uploading credentials to GitHub Actions Secrets...")
    update_github_secret("YOUTUBE_CLIENT_ID", client_id)
    update_github_secret("YOUTUBE_CLIENT_SECRET", client_secret)
    update_github_secret("YOUTUBE_REFRESH_TOKEN", refresh_token)

    # Update local .env
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            content = f.read()
        lines = []
        for line in content.split("\n"):
            if line.startswith("YOUTUBE_CLIENT_ID="):
                lines.append(f'YOUTUBE_CLIENT_ID="{client_id}"')
            elif line.startswith("YOUTUBE_CLIENT_SECRET="):
                lines.append(f'YOUTUBE_CLIENT_SECRET="{client_secret}"')
            elif line.startswith("YOUTUBE_REFRESH_TOKEN="):
                lines.append(f'YOUTUBE_REFRESH_TOKEN="{refresh_token}"')
            else:
                lines.append(line)
        with open(env_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    print("\n==================================================================")
    print(" SUCCESS! Your YouTube Channel is now connected to GitHub Actions!")
    print(" Your videos will now automatically publish to your YouTube channel.")
    print("==================================================================")

if __name__ == "__main__":
    main()

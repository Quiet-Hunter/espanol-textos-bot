import os
import requests

# Environment variables for Gist ID and GitHub Token
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GIST_ID = os.getenv("GIST_ID")

# Headers for GitHub API requests
headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def load_chat_ids():
    """Fetch chat IDs from the Gist, ignoring any invalid lines."""
    url = f"https://api.github.com/gists/{GIST_ID}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        files = response.json()["files"]
        content = files["chat_ids.txt"]["content"]
        return {line.strip() for line in content.splitlines() if line.strip() and not line.startswith("<")}
    else:
        print(f"Failed to load chat_ids: {response.status_code}")
        return set()

def save_chat_id(chat_id):
    """Add a new chat ID to the Gist if it doesn't already exist."""
    chat_ids = load_chat_ids()
    if chat_id not in chat_ids:
        chat_ids.add(chat_id)
        update_gist(chat_ids)

def remove_chat_id(chat_id):
    """Remove a chat ID from the Gist if it exists."""
    chat_ids = load_chat_ids()
    if chat_id in chat_ids:
        chat_ids.remove(chat_id)
        update_gist(chat_ids)

def update_gist(chat_ids):
    """Update the Gist with the new list of chat IDs, including a placeholder if empty."""
    if not chat_ids:
        chat_ids.add("<chat_ids>")

    url = f"https://api.github.com/gists/{GIST_ID}"
    data = {
        "files": {
            "chat_ids.txt": {
                "content": "\n".join(chat_ids)
            }
        }
    }
    response = requests.patch(url, headers=headers, json=data)
    if response.status_code == 200:
        print("chat_ids.txt updated successfully.")
    else:
        print(f"Failed to update chat_ids.txt: {response.status_code}")

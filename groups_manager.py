# groups_manager.py

import os

CHAT_IDS_FILE = 'chat_ids.txt'

# Load all chat IDs from the file
def load_chat_ids():
    if not os.path.exists(CHAT_IDS_FILE):
        return set()
    with open(CHAT_IDS_FILE, 'r') as file:
        return set(line.strip() for line in file)

# Save a new chat ID to the file
def save_chat_id(chat_id):
    chat_ids = load_chat_ids()
    if chat_id not in chat_ids:
        with open(CHAT_IDS_FILE, 'a') as file:
            file.write(f"{chat_id}\n")

# Remove a chat ID from the file (optional, in case bot leaves the group)
def remove_chat_id(chat_id):
    chat_ids = load_chat_ids()
    if chat_id in chat_ids:
        chat_ids.remove(chat_id)
        with open(CHAT_IDS_FILE, 'w') as file:
            for cid in chat_ids:
                file.write(f"{cid}\n")

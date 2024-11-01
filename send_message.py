# send_message.py

import os
import csv
import requests
from dotenv import load_dotenv
from telegram import Bot
from groups_manager import load_chat_ids

WORDS_NUM = 5

# Load environment variables
load_dotenv()

API_KEY = os.getenv('BOT_API_KEY')
GOOGLE_SHEETS_CSV_URL = os.getenv('GOOGLE_SHEETS_CSV_URL')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GIST_ID = os.getenv('GIST_ID')

# Initialize bot
bot = Bot(token=API_KEY)
# GitHub headers for API requests
headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def fetch_words():
    """Fetches words and translations from a Google Sheets CSV."""
    response = requests.get(GOOGLE_SHEETS_CSV_URL)
    response.raise_for_status()
    words = []
    csv_data = response.content.decode('utf-8').splitlines()
    reader = csv.reader(csv_data)
    next(reader)  # Skip the header
    for row in reader:
        if len(row) >= 2:
            words.append((row[0], row[1]))  # Append (word, translation) tuples
    return words

def get_current_index():
    """Fetches the current index from index.txt in the Gist."""
    url = f"https://api.github.com/gists/{GIST_ID}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        files = response.json().get("files", {})
        content = files.get("index.txt", {}).get("content", "0")
        return int(content.strip()) if content.isdigit() else 0
    else:
        print(f"Failed to load index.txt: {response.status_code}")
        return 0

def save_current_index(index):
    """Updates the current index in index.txt in the Gist."""
    url = f"https://api.github.com/gists/{GIST_ID}"
    data = {"files": {"index.txt": {"content": str(index)}}}
    response = requests.patch(url, headers=headers, json=data)
    if response.status_code == 200:
        print("index.txt updated successfully in the Gist.")
    else:
        print(f"Failed to update index.txt: {response.status_code}")

def send_message():
    """Sends a group of words to each chat in the Gist's chat_ids list."""
    chat_ids = load_chat_ids()
    words = fetch_words()
    total_words = len(words)
    if total_words == 0:
        for chat_id in chat_ids:
            bot.send_message(chat_id=chat_id, text="No words found in the list.")
        return
    
    current_index = get_current_index()
    next_index = current_index + WORDS_NUM
    word_group = words[current_index:next_index]

    # If reaching the end of the list, loop back to the start
    if next_index >= total_words:
        next_index = 0

    # Update the current index for the next run
    save_current_index(next_index)

    # Format and send the message
    message = "\n".join([f"*{word}* - {translation}" for word, translation in word_group])
    for chat_id in chat_ids:
        bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

if __name__ == '__main__':
    send_message()

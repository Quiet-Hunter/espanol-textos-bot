import os
import csv
import requests
from dotenv import load_dotenv
from telegram import Bot

# Load environment variables
load_dotenv()

API_KEY = os.getenv('BOT_API_KEY')
GOOGLE_SHEETS_CSV_URL = os.getenv('GOOGLE_SHEETS_CSV_URL')
INDEX_FILE = 'index.txt'

# Initialize bot
bot = Bot(token=API_KEY)

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
    """Retrieves the current index from the index file."""
    if not os.path.exists(INDEX_FILE):
        return 0
    with open(INDEX_FILE, 'r') as file:
        index = file.read().strip()
        return int(index) if index.isdigit() else 0

def save_current_index(index):
    """Saves the current index to the index file."""
    with open(INDEX_FILE, 'w') as file:
        file.write(str(index))

def send_message(chat_ids):
    """Sends a group of words to each chat in the provided chat_ids list."""
    words = fetch_words()
    total_words = len(words)
    if total_words == 0:
        for chat_id in chat_ids:
            bot.send_message(chat_id=chat_id, text="No words found in the list.")
        return
    
    current_index = get_current_index()
    next_index = current_index + 5
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

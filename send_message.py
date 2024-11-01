# send_message.py

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

# Function to fetch words and translations from Google Sheets
def fetch_words():
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

# Function to get the current index
def get_current_index():
    if not os.path.exists(INDEX_FILE):
        return 0
    with open(INDEX_FILE, 'r') as file:
        index = file.read().strip()
        return int(index) if index.isdigit() else 0

# Function to save the current index
def save_current_index(index):
    with open(INDEX_FILE, 'w') as file:
        file.write(str(index))

# Function to send a group of words to each chat
def send_message(chat_ids):
    words = fetch_words()
    total_words = len(words)
    if total_words == 0:
        for chat_id in chat_ids:
            bot.send_message(chat_id=chat_id, text="No words found in the list.")
        return
    
    current_index = get_current_index()
    next_index = current_index + 5

    # Select the next group of 5 words, cycling back to the start if the end is reached
    word_group = words[current_index:next_index]
    if next_index >= total_words:
        # If reaching the end, loop back to the beginning
        next_index = 0

    # Update the current index for the next run
    save_current_index(next_index)

    # Format and send the message
    message = "\n".join([f"*{word}* - {translation}" for word, translation in word_group])
    for chat_id in chat_ids:
        bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

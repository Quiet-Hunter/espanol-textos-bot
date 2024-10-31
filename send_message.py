# send_message.py

import os
import csv
import requests
import random
from dotenv import load_dotenv
from telegram import Bot

# Load environment variables
load_dotenv()

API_KEY = os.getenv('BOT_API_KEY')
CHAT_ID = os.getenv('GROUP_CHAT_ID')
GOOGLE_SHEETS_CSV_URL = os.getenv('GOOGLE_SHEETS_CSV_URL')

# Initialize bot
bot = Bot(token=API_KEY)

# Function to fetch words and translations from Google Sheets
def fetch_words():
    response = requests.get(GOOGLE_SHEETS_CSV_URL)
    response.raise_for_status()  # Raise an error if the request fails

    words = []
    csv_data = response.content.decode('utf-8').splitlines()
    reader = csv.reader(csv_data)
    next(reader)  # Skip the header

    for row in reader:
        if len(row) >= 2:
            words.append((row[0], row[1]))  # Append (word, translation) tuples

    return words

# Function to send a word and its translation to the group
def send_message():
    words = fetch_words()
    if words:
        word, translation = random.choice(words)
        message = f"*{word}* - {translation}"
        bot.send_message(chat_id=CHAT_ID, text=message, parse_mode='Markdown')
    else:
        bot.send_message(chat_id=CHAT_ID, text="No words found in the list.")

if __name__ == '__main__':
    send_message()  # This allows you to run `python send_message.py` directly for testing

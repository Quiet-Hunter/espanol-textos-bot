# send_message.py

import os
import csv
import requests
import random
from dotenv import load_dotenv
from telegram import Bot
from groups_manager import load_chat_ids

# Load environment variables
load_dotenv()

API_KEY = os.getenv('BOT_API_KEY')
GOOGLE_SHEETS_CSV_URL = os.getenv('GOOGLE_SHEETS_CSV_URL')

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

# Function to send a word and its translation to each group
def send_message(chat_ids):
    words = fetch_words()
    if words:
        word, translation = random.choice(words)
        message = f"*{word}* - {translation}"
        for chat_id in chat_ids:
            bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')
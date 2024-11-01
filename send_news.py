# send_news.py

import os
import requests
from dotenv import load_dotenv
from telegram import Bot
from datetime import datetime, timedelta
import pytz

# Load environment variables
load_dotenv()

API_KEY = os.getenv('BOT_API_KEY')
MEDIASTACK_API_KEY = os.getenv('MEDIASTACK_API_KEY')

# Initialize bot
bot = Bot(token=API_KEY)

# Function to fetch a news article from the Mediastack API
def fetch_article():
    yesterday = (datetime.now(pytz.utc) - timedelta(days=1)).strftime('%Y-%m-%d')
    url = "http://api.mediastack.com/v1/news"
    params = {
        'access_key': MEDIASTACK_API_KEY,
        'languages': 'es',
        'categories': 'science,technology,health,entertainment,business',
        'limit': 1,
        'sort': 'popularity',
        'date': f'{yesterday}',
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data['data']:
            article = data['data'][0]
            title = article.get('title', 'No Title')
            description = article.get('description', 'No Description')
            url = article.get('url', '')
            return f"*{title}*\n\n{description}\n\n[Leer más]({url})"
    return None

# Function to send the news article to each group
def send_news(chat_ids):
    article_summary = fetch_article()
    if article_summary:
        for chat_id in chat_ids:
            bot.send_message(chat_id=chat_id, text=article_summary, parse_mode='Markdown')
    else:
        for chat_id in chat_ids:
            bot.send_message(chat_id=chat_id, text="No se encontraron artículos interesantes para ayer.")

"""
Functions:
    fetch_article(): Fetches a news article from the Mediastack API.
    send_news(): Sends the fetched news article to each chat in the list of chat IDs.
"""
import os
from datetime import datetime, timedelta
import requests
from dotenv import load_dotenv
from telegram import Bot
import pytz
from groups_manager import load_chat_ids

# Load environment variables
load_dotenv()

API_KEY = os.getenv('BOT_API_KEY')
MEDIASTACK_API_KEY = os.getenv('MEDIASTACK_API_KEY')

# Initialize bot
bot = Bot(token=API_KEY)

def fetch_article():
    """Fetches a news article from the Mediastack API."""
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

    response = requests.get(url, params=params, timeout=10)
    if response.status_code == 200:
        data = response.json()
        if data['data']:
            article = data['data'][0]
            title = article.get('title', 'No Title')
            description = article.get('description', 'No Description')
            url = article.get('url', '')
            return f"*{title}*\n\n{description}\n\n[Leer más]({url})"
    return None

def send_news():
    """Sends the news article to each chat in the Gist's chat_ids list."""
    chat_ids = load_chat_ids()
    article_summary = fetch_article()
    if article_summary:
        for chat_id in chat_ids:
            bot.send_message(chat_id=chat_id, text=article_summary, parse_mode='Markdown')
    else:
        for chat_id in chat_ids:
            return None
            # bot.send_message(chat_id=chat_id, text="No se encontraron artículos interesantes para ayer.")

if __name__ == '__main__':
    send_news()

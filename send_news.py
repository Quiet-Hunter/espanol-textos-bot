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
CHAT_ID = os.getenv('GROUP_CHAT_ID')
MEDIASTACK_API_KEY = os.getenv('MEDIASTACK_API_KEY')

# Initialize bot
bot = Bot(token=API_KEY)

# Function to fetch a news article from the Mediastack API
def fetch_article():
    # Get yesterday's date
    yesterday = (datetime.now(pytz.utc) - timedelta(days=1)).strftime('%Y-%m-%d')
    
    # Define the Mediastack API URL and parameters
    url = "http://api.mediastack.com/v1/news"
    params = {
        'access_key': MEDIASTACK_API_KEY,
        'languages': 'es',
        'categories': 'science,technology,health,entertainment,business',
        'limit': 1,
        'sort': 'popularity',
        'date': f'{yesterday}',
    }

    # Make a request to the Mediastack API
    response = requests.get(url, params=params)
    
    # Check if the response is successful
    if response.status_code == 200:
        data = response.json()
        if data['data']:
            # Take the first article from the response
            article = data['data'][0]
            title = article.get('title', 'No Title')
            description = article.get('description', 'No Description')
            url = article.get('url', '')

            # Return the formatted article summary
            return f"*{title}*\n\n{description}\n\n[Leer más]({url})"
    return None

# Function to send the news article to the group
def send_news():
    article_summary = fetch_article()
    if article_summary:
        bot.send_message(chat_id=CHAT_ID, text=article_summary, parse_mode='Markdown')
    else:
        bot.send_message(chat_id=CHAT_ID, text="No se encontraron artículos interesantes para ayer.")

if __name__ == '__main__':
    send_news()  # Allows testing the function locally

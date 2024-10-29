import os
import requests
from dotenv import load_dotenv
from telegram import Bot
from telegram.ext import Updater, CommandHandler
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import logging
import pytz
from datetime import datetime, timedelta

# Load environment variables from the .env file
load_dotenv()

API_KEY = os.getenv('BOT_API_KEY')
CHAT_ID = os.getenv('GROUP_CHAT_ID')
MEDIASTACK_API_KEY = os.getenv('MEDIASTACK_API_KEY')

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Initialize bot
bot = Bot(token=API_KEY)

# Function to fetch a short, interesting Spanish article from yesterday using the Mediastack API
def fetch_article():
    # Get yesterday's date
    yesterday = (datetime.now(pytz.utc) - timedelta(days=1)).strftime('%Y-%m-%d')
    
    # Define the Mediastack API URL and parameters
    url = "http://api.mediastack.com/v1/news"
    params = {
        'access_key': MEDIASTACK_API_KEY,
        'languages': 'es',            # Spanish language
        'categories': 'science,technology,health,entertainment,business',  # Choose interesting topics
        'limit': 1,                   # Get only one article
        'sort': 'popularity',         # Sort by popularity to get an interesting one
        'date': f'{yesterday}',  # Fetch only yesterday's articles
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
    #     else:
    #         return "No se encontraron artículos interesantes para ayer."
    # else:
    #     return "Error al obtener el artículo. Inténtalo más tarde."

# Function to send message to the group with the fetched article
def send_message():
    # Fetch the article
    article_summary = fetch_article()
    # Send the article to the Telegram group
    if article_summary:
        bot.send_message(chat_id=CHAT_ID, text=article_summary, parse_mode='Markdown')

# Function to handle the /start command
def start(update, context):
    update.message.reply_text('Bot started!')

# Set up a scheduler to run daily at the selected time with timezone
def schedule_daily_message():
    scheduler = BackgroundScheduler()
    # Set your timezone (e.g., UTC, Europe/Madrid)
    timezone = pytz.timezone('UTC')
    # Schedule the job with timezone information
    scheduler.add_job(send_message, trigger=CronTrigger(hour=11, minute=00, timezone=timezone))
    scheduler.start()

def main():
    # Set up the Updater and dispatcher
    updater = Updater(token=API_KEY, use_context=True)
    dispatcher = updater.dispatcher

    # Start command to initiate the bot
    dispatcher.add_handler(CommandHandler('start', start))

    # Schedule the daily message
    schedule_daily_message()

    # Start the bot
    updater.start_polling()
    updater.idle()

    # send_message()

if __name__ == '__main__':
    main()

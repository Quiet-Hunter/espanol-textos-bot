import os
from dotenv import load_dotenv
from telegram import Bot
from telegram.ext import Updater, CommandHandler
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import logging
import pytz

# Load environment variables from the .env file
load_dotenv()

API_KEY = os.getenv('BOT_API_KEY')
CHAT_ID = os.getenv('GROUP_CHAT_ID')
MEDIATSTACK_API_KEY = os.getenv('MEDIATSTACK_API_KEY')

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Initialize bot
bot = Bot(token=API_KEY)

# Function to send message to the group
def send_message():
    bot.send_message(chat_id=CHAT_ID, text="Hello")

# Function to handle the /start command
def start(update):
    update.message.reply_text('Bot started!')

# Set up a scheduler to run daily at the selected time with timezone
def schedule_daily_message():
    scheduler = BackgroundScheduler()
    # Set your timezone (e.g., UTC, Europe/Madrid)
    timezone = pytz.timezone('UTC')
    # Schedule the job with timezone information
    scheduler.add_job(send_message, trigger=CronTrigger(hour=11, minute=0, timezone=timezone))
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

if __name__ == '__main__':
    main()

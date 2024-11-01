# bot_main.py

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from telegram.ext import Updater, MessageHandler, Filters
from telegram import Update
from telegram.ext import CallbackContext
import os
import pytz
import logging

from groups_manager import load_chat_ids, save_chat_id, remove_chat_id
from send_message import send_message
from send_news import send_news

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Load the API key for the bot
API_KEY = os.getenv('BOT_API_KEY')
updater = Updater(token=API_KEY, use_context=True)

def track_group_membership(update: Update, context: CallbackContext):
    """Tracks when the bot is added to or removed from a group."""
    chat_id = str(update.effective_chat.id)
    if update.message.new_chat_members:
        save_chat_id(chat_id)
        update.message.reply_text("¡Hola! He sido añadido a este grupo y enviaré mensajes programados aquí.")
    elif update.message.left_chat_member:
        remove_chat_id(chat_id)

def schedule_daily_messages():
    """Sets up scheduled jobs for sending news and messages to groups."""
    scheduler = BackgroundScheduler()
    timezone = pytz.timezone('UTC')
    
    # Schedule news at 11:00 UTC
    scheduler.add_job(lambda: send_news(load_chat_ids()), trigger=CronTrigger(hour=11, minute=0, timezone=timezone))
    
    # Schedule word at 18:00 UTC
    scheduler.add_job(lambda: send_message(load_chat_ids()), trigger=CronTrigger(hour=18, minute=0, timezone=timezone))

    scheduler.start()
    logging.info("Scheduler started with daily jobs for news and words.")

def main():
    """Main function to start the bot, group tracking, and scheduler."""
    dispatcher = updater.dispatcher

    # Add handler for tracking group membership changes
    dispatcher.add_handler(MessageHandler(Filters.status_update.new_chat_members | Filters.status_update.left_chat_member, track_group_membership))
    
    # Start the scheduler for daily messages
    schedule_daily_messages()
    
    # Start the bot and polling to track group membership changes
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

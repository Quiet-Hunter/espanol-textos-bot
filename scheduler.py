# scheduler.py

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz
import os
import logging
from send_message import send_message
from send_news import send_news
from telegram.ext import Updater, MessageHandler, Filters
from groups_manager import load_chat_ids, save_chat_id, remove_chat_id
from telegram import Update
from telegram.ext import CallbackContext

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

API_KEY = os.getenv('BOT_API_KEY')
updater = Updater(token=API_KEY, use_context=True)

# Function to handle bot being added to or removed from a group
def track_group_membership(update: Update, context: CallbackContext):
    chat_id = str(update.effective_chat.id)
    if update.message.new_chat_members:
        save_chat_id(chat_id)
        update.message.reply_text("¡Hola! He sido añadido a este grupo y enviaré mensajes programados aquí.")
    elif update.message.left_chat_member:
        remove_chat_id(chat_id)

# Schedule messages
def schedule_daily_messages():
    scheduler = BackgroundScheduler()
    timezone = pytz.timezone('UTC')
    
    # Schedule news at 11:00 UTC
    scheduler.add_job(lambda: send_news(load_chat_ids()), trigger=CronTrigger(hour=11, minute=0, timezone=timezone))
    
    # Schedule word at 18:00 UTC
    scheduler.add_job(lambda: send_message(load_chat_ids()), trigger=CronTrigger(hour=11, minute=25, timezone=timezone))

    scheduler.start()
    scheduler.print_jobs()

def main():
    # Set up bot to track group changes
    dispatcher = updater.dispatcher
    dispatcher.add_handler(MessageHandler(Filters.status_update.new_chat_members | Filters.status_update.left_chat_member, track_group_membership))
    
    # Schedule the daily messages
    schedule_daily_messages()
    
    # Start polling to track group memberships
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

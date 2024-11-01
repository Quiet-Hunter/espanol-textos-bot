# bot_main.py

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from telegram import Bot, Update
from telegram.ext import Dispatcher, MessageHandler, Filters, CallbackContext
from flask import Flask, request
import os
import pytz
import logging

from groups_manager import load_chat_ids, save_chat_id, remove_chat_id
from send_message import send_message
from send_news import send_news

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Load the API key and initialize the bot and Flask app
API_KEY = os.getenv('BOT_API_KEY')
bot = Bot(token=API_KEY)
app = Flask(__name__)

# Initialize the dispatcher without polling
dispatcher = Dispatcher(bot, None, use_context=True)

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
    scheduler.add_job(lambda: send_news(load_chat_ids()), trigger=CronTrigger(hour=12, minute=52, timezone=timezone))
    
    # Schedule word at 18:00 UTC
    scheduler.add_job(lambda: send_message(load_chat_ids()), trigger=CronTrigger(hour=12, minute=52, timezone=timezone))

    scheduler.start()
    logging.info("Scheduler started with daily jobs for news and words.")

# Set up the handler for tracking group membership
dispatcher.add_handler(MessageHandler(Filters.status_update.new_chat_members | Filters.status_update.left_chat_member, track_group_membership))

# Define the webhook route
@app.route(f'/{API_KEY}', methods=['POST'])
def webhook():
    """Webhook to process incoming Telegram updates."""
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK", 200

@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    """Sets the webhook for Telegram to call on updates."""
    webhook_url = f"https://espanol-textos-bot-57d2b70cbb7f.herokuapp.com/{API_KEY}"
    bot.set_webhook(url=webhook_url)
    return "Webhook set successfully!", 200

def main():
    """Main function to initialize the bot with webhooks and start the scheduler."""
    # Start the scheduler for daily messages
    schedule_daily_messages()

    # Start the Flask app for webhook processing
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))

if __name__ == '__main__':
    main()

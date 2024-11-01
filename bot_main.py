# bot_main.py

from telegram import Bot
from telegram.ext import Dispatcher, MessageHandler, Filters
from flask import Flask, request
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import os
import logging
from groups_manager import load_chat_ids, save_chat_id, remove_chat_id
from send_message import send_message
from send_news import send_news

# Initialize environment variables and bot
API_KEY = os.getenv('BOT_API_KEY')
bot = Bot(token=API_KEY)
app = Flask(__name__)

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Initialize dispatcher without polling
dispatcher = Dispatcher(bot, None, workers=0)

# Function to handle bot being added to a group
def track_group_membership(update, context):
    chat_id = str(update.effective_chat.id)
    if update.message.new_chat_members:
        save_chat_id(chat_id)
        update.message.reply_text("¡Hola! He sido añadido a este grupo y enviaré mensajes programados aquí.")
    elif update.message.left_chat_member:
        remove_chat_id(chat_id)

# Set up command and message handlers
dispatcher.add_handler(MessageHandler(Filters.status_update.new_chat_members | Filters.status_update.left_chat_member, track_group_membership))

# Webhook endpoint to receive updates
@app.route(f'/{API_KEY}', methods=['POST'])
def webhook():
    update = bot.update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK", 200

# Endpoint to set up the webhook
@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    url = f"https://espanol-textos-bot-57d2b70cbb7f.herokuapp.com/{API_KEY}"
    webhook_set = bot.set_webhook(url)
    return "Webhook setup success!" if webhook_set else "Webhook setup failed.", 200

# Function to schedule sending messages and news
def schedule_jobs():
    scheduler = BackgroundScheduler()
    timezone = 'UTC'

    # Schedule the job for sending news at 11:00 UTC
    scheduler.add_job(lambda: send_news(load_chat_ids()), trigger=CronTrigger(hour=11, minute=0, timezone=timezone))

    # Schedule the job for sending words at 18:00 UTC
    scheduler.add_job(lambda: send_message(load_chat_ids()), trigger=CronTrigger(hour=18, minute=0, timezone=timezone))

    scheduler.start()
    logging.info("Scheduler started with daily jobs for news and words.")

# Start the app with scheduler
if __name__ == '__main__':
    # Schedule the jobs
    schedule_jobs()
    
    # Run the Flask app to receive webhooks
    app.run(port=5000)

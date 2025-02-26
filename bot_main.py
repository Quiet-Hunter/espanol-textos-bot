import os
import logging
from telegram import Bot, Update
from telegram.ext import Dispatcher, MessageHandler, Filters
from flask import Flask, request
from groups_manager import save_chat_id, remove_chat_id

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Load API key and initialize bot and Flask app
API_KEY = os.getenv('BOT_API_KEY')
bot = Bot(token=API_KEY)
app = Flask(__name__)

# Initialize dispatcher without polling
dispatcher = Dispatcher(bot, None, use_context=True)

def track_group_membership(update: Update):
    """Tracks when the bot is added to or removed from a group."""
    chat_id = str(update.effective_chat.id)
    if update.message.new_chat_members:
        save_chat_id(chat_id)
        update.message.reply_text("¡Hola! He sido añadido a este grupo y enviaré mensajes programados aquí.")
    elif update.message.left_chat_member:
        remove_chat_id(chat_id)

# Set up the handler for tracking group membership
dispatcher.add_handler(MessageHandler(Filters.status_update.new_chat_members | Filters.status_update.left_chat_member, track_group_membership))

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

@app.route('/')
def index():
    """Root route to confirm bot is running."""
    return "Español Textos Bot is running!"

def main():
    """Main function to start the Flask app for webhook processing."""
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))

if __name__ == '__main__':
    main()

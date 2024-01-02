from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import requests
from flask import Flask, request

bot_token = 'YOUR_BOT_TOKEN'
bot = Updater(token=bot_token, use_context=True)
dispatcher = bot.dispatcher

def start(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    update.message.reply_text(
        f"Hi {user.first_name},\n\nI can Download Files from Terabox.\n\nMade with ❤️ by @BalaPriyan\n\nSend any terabox link to download.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Channel", url="https://t.me/BalaPriyan"), InlineKeyboardButton("Report bug", url="https://t.me/TeraBoxTgbot")]
        ])
    )

def message(update: Update, context: CallbackContext) -> None:
    message_text = update.message.text
    if "terabox.com" in message_text or "teraboxapp.com" in message_text:
        parts = message_text.split("/")
        link_id = parts[-1]

        try:
            details = get_details(link_id)
            if details.get("ok"):
                update.message.reply_text(f"Sending {len(details['list'])} Files Please Wait.!!")
                for item in details['list']:
                    send_file(details['shareid'], details['uk'], details['sign'], details['timestamp'], item['fs_id'], update.message.chat_id)
            else:
                update.message.reply_text(details.get('message', 'Error fetching details'))
        except Exception as e:
            print(e)
            update.message.reply_text("Error occurred while processing the link.")
    else:
        update.message.reply_text("Please send a valid Terabox link.")

def get_details(link_id):
    try:
        response = requests.get(f"http://terabox-dl.qtcloud.workers.dev/api/get-info?shorturl={link_id}&pwd=")
        return response.json()
    except requests.RequestException as e:
        print(e)
        return {}

def send_file(shareid, uk, sign, timestamp, fs_id, chat_id):
    try:
        data = {
            "shareid": shareid,
            "uk": uk,
            "sign": sign,
            "timestamp": timestamp,
            "fs_id": fs_id
        }
        headers = {
            "Content-Type": "application/json"
        }
        response = requests.post("https://terabox-dl.qtcloud.workers.dev/api/get-download", json=data, headers=headers)
        file_url = response.json().get('url')
        bot.send_message(chat_id=chat_id, text=f"Download link: {file_url}")
    except requests.RequestException as e:
        print(e)

app = Flask(__name__)

@app.route('/', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot.bot)
    bot.dispatcher.process_update(update)
    return 'OK'

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, message))

if __name__ == '__main__':
    bot.start_polling()
    app.run(port=3000)

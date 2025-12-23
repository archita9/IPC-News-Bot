import os
from telegram.ext import Updater, MessageHandler, Filters
import feedparser
from urllib.parse import quote_plus
from flask import Flask
from threading import Thread

# 🔐 TELEGRAM BOT TOKEN (FROM ENV VARIABLE)
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not set in environment variables")

# IPC → Search Queries
IPC_MAP = {
    "320": "grievous injury OR serious assault India",
    "321": "hurt OR physical assault India",
    "323": "assault OR beaten India",
    "324": "attack with weapon OR knife attack India",
    "325": "severe injury OR brutal assault India",
    "326": "acid attack OR chemical burn India",
    "327": "extortion with injury India",
    "38":  "criminal conspiracy OR common intention India"
}

# 🌐 KEEP-ALIVE SERVER (FOR REPLIT FREE)
app = Flask(__name__)

@app.route('/')
def home():
    return "IPC News Bot is alive"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    Thread(target=run).start()

def fetch_latest_news(query):
    try:
        query = f"{query} when:7d"
        encoded_query = quote_plus(query)

        url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-IN&gl=IN&ceid=IN:en"
        feed = feedparser.parse(url)

        if not feed.entries:
            return "\n❌ No news found in the last 7 days.\n"

        response = "\n📰 Latest IPC News (Last 7 Days):\n\n"

        for entry in feed.entries[:3]:
            published = entry.published if hasattr(entry, "published") else "Date not available"
            response += (
                f"• {entry.title}\n"
                f"🕒 {published}\n"
                f"{entry.link}\n\n"
            )

        return response

    except Exception:
        return "\n⚠️ Error fetching news. Please try again later.\n"

def handle_message(update, context):
    user_text = update.message.text.strip()

    if user_text not in IPC_MAP:
        update.message.reply_text(
            "❌ IPC Act not supported yet.\n\n"
            "📌 Send an IPC section number like:\n"
            "320\n323\n326"
        )
        return

    query = IPC_MAP[user_text]
    reply = f"📘 IPC Act {user_text}\n"
    reply += fetch_latest_news(query)

    update.message.reply_text(reply, disable_web_page_preview=True)

def main():
    keep_alive()  # ✅ KEEP REPLIT AWAKE

    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    print("🤖 IPC News Bot is running...")
    updater.idle()

if __name__ == "__main__":
    main()

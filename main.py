
import os
import time
import threading
import tempfile
from urllib.parse import urlparse

import requests
import yt_dlp
from flask import Flask, request, abort

TOKEN = os.environ["BOT_TOKEN"]
WEBHOOK_SECRET = os.environ["WEBHOOK_SECRET"]
RENDER_URL = os.environ["RENDER_EXTERNAL_URL"].rstrip("/")

API = f"https://api.telegram.org/bot{TOKEN}/"
WEBHOOK_PATH = f"/webhook/{WEBHOOK_SECRET}"

app = Flask(__name__)

SUPPORT_ID = "@Ss_Pox_1"

INSTAGRAM = "انســۘــتـ‌اگـࢪا۾ 🖤"
YOUTUBE = "یـــۘــᤣتـ‌ᤣب 🤍"
MUSIC = "داטּــۘــلــᤣد آهـ‍‍‌ـטּــگ 🎶"
HELP = "راهــۘـــטּـما 🎗️"
SUPPORT = "پشــۘــتـ‌؎ــبـ‌انے زےـڪس ء 🖤"

menu = {
    "keyboard": [
        [INSTAGRAM],
        [YOUTUBE],
        [MUSIC],
        [HELP],
        [SUPPORT]
    ],
    "resize_keyboard": True
}


def send_message(chat_id, text, keyboard=None):
    data = {"chat_id": chat_id, "text": text}
    if keyboard:
        data["reply_markup"] = keyboard

    requests.post(API + "sendMessage", json=data, timeout=30)


def valid_url(url):
    try:
        host = (urlparse(url).hostname or "").lower()
        return (
            host == "youtube.com"
            or host.endswith(".youtube.com")
            or host == "youtu.be"
            or host == "instagram.com"
            or host.endswith(".instagram.com")
        )
    except Exception:
        return False


def download_video(url, folder):
    options = {
        "format": "best[ext=mp4]/best",
        "outtmpl": os.path.join(folder, "video.%(ext)s"),
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "max_filesize": 45 * 1024 * 1024,
        "socket_timeout": 30,
        "retries": 2
    }

    with yt_dlp.YoutubeDL(options) as ydl:
        ydl.download([url])

    for name in os.listdir(folder):
        path = os.path.join(folder, name)
        if os.path.isfile(path):
            return path

    return None


def send_video(chat_id, path):
    if os.path.getsize(path) > 45 * 1024 * 1024:
        send_message(chat_id, "حجم فایل زیاد است و فعلاً ارسال نمی‌شود.")
        return

    extension = os.path.splitext(path)[1].lower()
    method = "sendVideo" if extension == ".mp4" else "sendDocument"
    field = "video" if method == "sendVideo" else "document"

    with open(path, "rb") as file:
        response = requests.post(
            API + method,
            data={"chat_id": chat_id},
            files={field: file},
            timeout=180
        )

    if not response.ok:
        send_message(chat_id, "ارسال فایل انجام نشد. دوباره تلاش کن.")


def handle_message(message):
    if "text" not in message:
        return

    chat_id = message["chat"]["id"]
    text = message["text"].strip()

    if text == "/start":
        send_message(
            chat_id,
            """ســۘــلام - ؏ـزیز 🖤.

بہ ربــۘــات دانـ‍لودر ᴢᴇxx خـــۘــᤣش امــدے 🖤🎶.
لــۘــطفاً یڪے از گزینــۘــ‍ه ها؎ زیـر را انــۘــتـ‌خاب ڪن 🎗️🖤.""",
            menu
        )

    elif text == INSTAGRAM:
        send_message(
            chat_id,
            """بہ بـخـءـش دانــۘــلـود اینـــ̉ـستـاگـِࢪام خـ؏ـوش امدے ء لطفاً لیــۘـــטּـڪ پـست یا ویــۘــدیـᤣ را بفـــۘــرست ... 🎶🖤."""
        )

    elif text == YOUTUBE:
        send_message(
            chat_id,
            """بہ بـخـءـش دانــۘــلود یــۘــᤣتـ‌ᤣب خـ؏ـوش امدے ء لطفاً لیــۘـــטּـڪ ویدیــᤣ را بفرســۘــت ... 🎶🖤."""
        )

    elif text == MUSIC:
        send_message(chat_id, "بخش دانلود آهنگ هنوز فعال نشده است.")

    elif text == HELP:
        send_message(
            chat_id,
            f"""راهـטּــ̉ـماے استـءـفاده از ربات ᴢᴇxx 💤🖤.

1. بـخـءـش مـᤣردنظــۘــر خـءـود را انتـ‌خاب ڪن .

2. لیــۘــنڪ محتـ‌وا را بفــۘــرست .

3. منتـ‌ظر پاســۘــخ ربات بـ‌۾ــاـטּ .

پشتیبانی: {SUPPORT_ID}"""
        )

    elif text == SUPPORT:
        send_message(
            chat_id,
            f"""بہ پشتـ‌یبانے ᴢᴇxx خـءوش امدے ء 🖤͚👋🏾͚ ..
اگــۘــر مشڪلے دارے ء پیــۘــام خـᤣد را بفـِࢪست .

{SUPPORT_ID}"""
        )

    elif text.startswith(("http://", "https://")):
        if not valid_url(text):
            send_message(
                chat_id,
                "لـــۘـــטּــڪ ارســۘــالے درسـت نــ̉ـیست 🙂❌ ."
            )
            return

        send_message(
            chat_id,
            """درحـءـال بررسے ء درخواست شمـا ء هستیـءـم ... ⏳
لطفاً ڪمے صبر ڪن ."""
        )

        try:
            with tempfile.TemporaryDirectory() as folder:
                path = download_video(text, folder)
                if not path:
                    raise Exception("No file")
                send_video(chat_id, path)

        except Exception as error:
            print("Download error:", error)
            send_message(
                chat_id,
                """متـاسفانہ مشڪلے پیـءش امد ⚠️⚠️..
لطفاً دوبـار؏ تـ‌لاش ڪن .. 🖤."""
            )

    else:
        send_message(
            chat_id,
            "لـــۘـــטּــڪ ارســۘــالے درسـت نــ̉ـیست 🙂❌ ."
        )


def process_update(update):
    try:
        message = update.get("message")
        if message:
            handle_message(message)
    except Exception as error:
        print("Message error:", error)


@app.route("/", methods=["GET"])
def home():
    return "ZEXX Downloader is running!"


@app.route(WEBHOOK_PATH, methods=["POST"])
def webhook():
    secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
    if secret != WEBHOOK_SECRET:
        abort(403)

    update = request.get_json(silent=True) or {}
    threading.Thread(
        target=process_update,
        args=(update,),
        daemon=True
    ).start()

    return "OK", 200


def set_webhook():
    url = RENDER_URL + WEBHOOK_PATH
    try:
        response = requests.post(
            API + "setWebhook",
            json={
                "url": url,
                "secret_token": WEBHOOK_SECRET,
                "drop_pending_updates": False
            },
            timeout=30
        )
        print("Webhook setup:", response.text)
    except Exception as error:
        print("Webhook setup error:", error)


set_webhook()

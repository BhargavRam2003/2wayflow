
from flask import Flask, render_template
from datetime import datetime, date
from telegram import Bot
from apscheduler.schedulers.background import BackgroundScheduler
import asyncio
import pytz

app = Flask(__name__)

IST = pytz.timezone("Asia/Kolkata")

# -----------------------------
# DATE / WATER SCHEDULE
# -----------------------------

def today_ist():
    """Return today's date in IST."""
    return datetime.now(IST).date()


BOT_TOKEN = "8206108349:AAH8LQU14rY-0VQ_LqwxFU7dWrNOAoss0LQ"
CHAT_ID = 7077765572

water_hours = {
    0: 19,  # reminder for 7 PM water
    1: 21   # reminder for 9 PM water
}

last_sent_date = {}


# -----------------------------
# WATER DAY CALCULATION
# -----------------------------

def message_condition():
    start_day = date(2026, 1, 25)
    today = today_ist()

    days_passed = (today - start_day).days

    condition_date = days_passed % 4

    return condition_date


def message_loop():
    condition_date = message_condition()

    if condition_date == 0:
        return "💧 Water will come today at 7:00 PM!"

    elif condition_date == 1:
        return "💧 Water will come today at 9:00 PM!"

    else:
        return None


# -----------------------------
# TELEGRAM
# -----------------------------

async def send_telegram_message(message):
    async with Bot(token=BOT_TOKEN) as bot:
        await bot.send_message(
            chat_id=CHAT_ID,
            text=f"⏰ Reminder: {message}"
        )


def message_sender():
    global last_sent_date

    condition = message_condition()
    message = message_loop()

    # No water today
    if not message:
        return

    now = datetime.now(IST)
    now_hour = now.hour
    today_date = now.date()

    reminder_hour = water_hours.get(condition)

    if reminder_hour is None:
        return

    # Send during the reminder hour
    if reminder_hour <= now_hour < reminder_hour + 1:

        # Prevent multiple messages on the same day
        if last_sent_date.get(today_date) != condition:

            try:
                asyncio.run(send_telegram_message(message))

                last_sent_date[today_date] = condition

                print(
                    f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] "
                    f"Telegram message sent successfully!"
                )

            except Exception as e:
                print(f"Telegram error: {e}")


# -----------------------------
# FLASK HOME PAGE
# -----------------------------

@app.route("/")
def home():

    message = message_loop()

    if not message:
        message = "😴 Water will not come today, relax!"

    now = datetime.now(IST).strftime(
        "%A, %d %B %Y %I:%M %p"
    )

    return render_template(
        "index.html",
        now=now,
        message=message
    )


# -----------------------------
# SCHEDULER
# -----------------------------

scheduler = BackgroundScheduler(
    timezone="Asia/Kolkata"
)

scheduler.add_job(
    message_sender,
    "cron",
    minute="*",
    id="water_reminder",
    replace_existing=True
)

scheduler.start()


# -----------------------------
# START FLASK
# -----------------------------

if __name__ == "__main__":
    app.run(
        debug=True,
        use_reloader=False
    )
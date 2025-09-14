from flask import Flask, render_template
from datetime import datetime, date
from telegram import Bot
from apscheduler.schedulers.background import BackgroundScheduler
import asyncio
import pytz

app = Flask(__name__)

IST = pytz.timezone("Asia/Kolkata")

def today_ist():
    """Return today's date in IST (not UTC)."""
    return datetime.now(IST).date()

BOT_TOKEN = "8206108349:AAH8LQU14rY-0VQ_LqwxFU7dWrNOAoss0LQ"
CHAT_ID = 7077765572
bot = Bot(token=BOT_TOKEN)


water_hours = {0:16,1:20}

last_sent_date = {}


def message_condition():
    start_day = date(2025,9,9)
    today = today_ist()

    days_passed = (today - start_day).days

    condition_date = days_passed % 4

    return condition_date

def message_loop():

    condition_date = message_condition()

    if(condition_date == 0):
        return "💧 Water will come today at 5:00PM!"
    elif(condition_date ==1):
        return "💧 Water will come today at 9:00PM!"
    else:
        return None
    
    
# Telegram condtion  
def message_sender():
    global last_sent_date
    condition = message_condition()
    message = message_loop()

    if not message:
        return
    
    now = datetime.now(pytz.timezone("Asia/Kolkata"))
    now_hour = now.hour
    today_date = now.date()

    remainder_hour = water_hours.get(condition)
    if remainder_hour is None:
        return
    if remainder_hour <= now_hour < remainder_hour +1:
        if last_sent_date.get(today_date) != condition:
            asyncio.run(bot.send_message(chat_id=CHAT_ID, text=f"⏰ Reminder: {message}"))
            last_sent_date[today_date] = condition



@app.route('/')
def home():
    message = message_loop() or "😴 Water will not come today, relax!" 

    now = datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%A, %d %B %Y %I:%M %p")
    return render_template("index.html", now=now, message=message)

scheduler = BackgroundScheduler(timezone="Asia/Kolkata")
scheduler.add_job(message_sender, 'cron', minute="*")
scheduler.start()

if(__name__) == "__main__":
    app.run(debug=True)
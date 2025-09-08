from flask import Flask, render_template
from datetime import datetime, date, timedelta

app = Flask(__name__)

@app.route('/')
def home():

    start_day = date.today() + timedelta(days=1)
    today = date.today()

    days_passed = (today - start_day).days

    condition_date = days_passed % 4

    if(condition_date == 0):
        message = "💧 Water will come today at 5:00PM!"
    elif(condition_date ==1):
        message = "💧 Water will come today at 9:00PM!"
    else:
        message = "😴 Water will not come today, relax!"

    now = datetime.now().strftime("%A, %d %B %Y %I:%M %p")
    return render_template("index.html", now=now, message=message)

if(__name__) == "__main__":
    app.run(debug=True)
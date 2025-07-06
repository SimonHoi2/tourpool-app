from flask import Flask, render_template_string
from scraper import scrape_data
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
stand = []

def update():
    global stand
    try:
        stand = scrape_data()
    except Exception as e:
        print("Fout bij scrapen:", e)

scheduler = BackgroundScheduler()
scheduler.add_job(update, 'interval', minutes=10)
scheduler.start()
update()

@app.route("/")
def home():
    html = "<h1>Tourpool Stand</h1><ul>"
    for r in stand:
        html += f"<li>{r['naam']}: {r['punten']} punten</li>"
    html += "</ul>"
    return render_template_string(html)

if __name__ == "__main__":
    app.run()
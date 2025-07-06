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
    html = """
    <html>
    <head>
        <title>Tourpool Stand</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                padding: 2rem;
                background-color: #f4f4f4;
            }
            h1 {
                text-align: center;
                color: #222;
            }
            table {
                width: 70%;
                margin: 0 auto;
                border-collapse: collapse;
                background: white;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }
            th, td {
                padding: 12px;
                border: 1px solid #ddd;
                text-align: center;
            }
            th {
                background-color: #333;
                color: white;
            }
            tr:nth-child(even) {
                background-color: #f9f9f9;
            }
        </style>
    </head>
    <body>
        <h1>Tourpool Stand</h1>
        <table>
            <tr>
                <th>Positie</th>
                <th>Naam</th>
                
            </tr>
    """
    for i, r in enumerate(stand, 1):
        html += f"""
            <tr>
                <td>{r['position']}</td>
                <td>{r['naam']}</td>
                
            </tr>
        """
    html += """
        </table>
    </body>
    </html>
    """
    return render_template_string(html)

if __name__ == "__main__":
    app.run()
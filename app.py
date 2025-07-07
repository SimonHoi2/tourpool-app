from flask import Flask, render_template_string, abort
from scraper import scrape_data
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

# Dictionary met alle etappes
stands = {}

def update():
    global stands
    try:
        # Stel: scrape_data kan ook een etappe-nummer krijgen
        for etappe_nr in range(1, 22):
            stands[etappe_nr] = scrape_data(etappe_nr)
        print("Data bijgewerkt voor alle etappes")
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
                text-align: center;
            }
            h1 {
                color: #222;
            }
            .button-container {
                margin-bottom: 2rem;
            }
            .etappe-button {
                display: inline-block;
                margin: 0.2rem;
                padding: 0.6rem 1rem;
                background-color: #333;
                color: white;
                text-decoration: none;
                border-radius: 4px;
                font-weight: bold;
                transition: background-color 0.3s;
            }
            .etappe-button:hover {
                background-color: #555;
            }
        </style>
    </head>
    <body>
        <h1>Tourpool Stand</h1>
        <div class="button-container">
    """
    for i in range(1, 22):
        html += f'<a href="/etappe/{i}" class="etappe-button">Etappe {i}</a>'
    html += """
        </div>
    </body>
    </html>
    """
    return render_template_string(html)

@app.route("/etappe/<int:etappe_nr>")
def show_etappe(etappe_nr):
    if etappe_nr not in stands:
        abort(404)
    stand = stands[etappe_nr]

    html = """
    <html>
    <head>
        <title>Tourpool Stand - Etappe {{etappe_nr}}</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                padding: 2rem;
                background-color: #f4f4f4;
                text-align: center;
            }
            h1 {
                color: #222;
            }
            .button-container {
                margin-bottom: 1.5rem;
            }
            .etappe-button {
                display: inline-block;
                margin: 0.15rem;
                padding: 0.6rem 1rem;
                background-color: #333;
                color: white;
                text-decoration: none;
                border-radius: 4px;
                font-weight: bold;
                transition: background-color 0.3s;
            }
            .etappe-button:hover {
                background-color: #555;
            }
            .etappe-button.active {
                background-color: #007bff;  /* opvallende blauwe kleur */
                cursor: default;
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
        <h1>Tourpool Stand - Etappe {{etappe_nr}}</h1>
        <div class="button-container">
    """

    # Knoppen 1 t/m 21 genereren, met 'active' class voor huidige etappe
    for i in range(1, 22):
        active_class = "active" if i == etappe_nr else ""
        html += f'<a href="/etappe/{i}" class="etappe-button {active_class}">Etappe {i}</a>'

    html += """
        </div>
        <table>
            <tr>
                <th>Positie</th>
                <th>Naam</th>
            </tr>
    """
    for r in stand:
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
    return render_template_string(html, etappe_nr=etappe_nr)

if __name__ == "__main__":
    app.run()

from flask import Flask, render_template_string, abort
from scraper import scrape_data
from apscheduler.schedulers.background import BackgroundScheduler
from teams import load_teams_xlsx
app = Flask(__name__)

# Dictionary met alle etappes
stands = {}

teams = load_teams_xlsx()

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
        <title>Tourpool</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                padding: 0;
                margin: 0;
            }
            .tabs {
                display: flex;
                background-color: #333;
                overflow-x: auto;
            }
            .tab {
                padding: 1rem;
                color: white;
                cursor: pointer;
                white-space: nowrap;
                flex-shrink: 0;
            }
            .tab:hover {
                background-color: #555;
            }
            .tab.active {
                background-color: #007bff;
            }
            .content {
                padding: 2rem;
            }
            table {
                width: 60%;
                margin: 0 auto;
                border-collapse: collapse;
                background: white;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }
            th, td {
                padding: 10px;
                border: 1px solid #ddd;
                text-align: left;
            }
            th {
                background-color: #333;
                color: white;
            }
            tr:nth-child(even) {
                background-color: #f9f9f9;
            }
        </style>
        <script>
            function showTab(id) {
                const tabs = document.querySelectorAll('.tab');
                tabs.forEach(tab => tab.classList.remove('active'));
                document.getElementById('tab-' + id).classList.add('active');

                const contents = document.querySelectorAll('.tabcontent');
                contents.forEach(c => c.style.display = 'none');
                document.getElementById('content-' + id).style.display = 'block';
            }

            window.onload = function() {
                showTab(1);  // standaard Etappe 1 tonen
            }
        </script>
    </head>
    <body>
        <div class="tabs">
    """

    # Tabs voor Etappes 1 t/m 21
    for i in range(1, 22):
        html += f'<div class="tab" id="tab-{i}" onclick="showTab({i})">Etappe {i}</div>'

    # Extra tab voor Teams
    html += '<div class="tab" id="tab-teams" onclick="showTab(\'teams\')">Teams</div>'
    html += '</div><div class="content">'

    # Contentblokken voor alle etappes
    for i in range(1, 22):
        if i not in stands:
            continue
        stand = stands[i]
        html += f'<div id="content-{i}" class="tabcontent" style="display:none;">'
        html += f'<h2>Stand Etappe {i}</h2>'
        html += "<table><tr><th>Positie</th><th>Naam</th></tr>"
        for r in stand:
            html += f"<tr><td>{r['position']}</td><td>{r['naam']}</td></tr>"
        html += "</table></div>"

    # Teamoverzicht (in teams)
    html += '<div id="content-teams" class="tabcontent" style="display:none;">'
    html += '<h2>Gekozen Renners per Deelnemer</h2><table><tr><th>Deelnemer</th><th>Renners</th></tr>'
    for naam, renners in teams.items():
        html += f"<tr><td>{naam}</td><td>{', '.join(renners)}</td></tr>"
    html += "</table></div>"

    html += "</div></body></html>"
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

@app.route("/teams")
def show_teams():
    html = "<h1>Gekozen renners per deelnemer</h1><ul>"
    for naam, renners in teams.items():
        html += f"<li><strong>{naam}</strong>: {', '.join(renners)}</li>"
    html += "</ul>"
    return render_template_string(html)

if __name__ == "__main__":
    app.run()

from flask import Flask, render_template_string, abort
from scraper import scrape_data
from apscheduler.schedulers.background import BackgroundScheduler
from teams import load_teams_xlsx
from collections import defaultdict
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

def calculate_points_for_etappe(stand):
    punten = {}
    for r in stand:
        try:
            pos = int(r['position'])
        except:
            continue
        if pos >=1 and pos <= 15:
            punten[normalize(r['naam'])] = 16 - pos  # 1e =15pt, 2e=14, ..., 15e=1

    return punten

def calculate_team_points(stands, teams):
    team_points = {team: 0 for team in teams}
    for etappe_nr, stand in stands.items():
        etappe_punten = calculate_points_for_etappe(stand)

        print(f"--- Etappe {etappe_nr} ---")
        print("Etappe punten:", etappe_punten)  # DEBUG
        for team, renners in teams.items():
            for renner in renners:
                norm_renner = normalize(renner)
                if norm_renner in etappe_punten:
                    #print(f"✅ Match: {renner} ({norm_renner}) krijgt {etappe_punten[norm_renner]} punten")
                    team_points[team] += etappe_punten[norm_renner]
                else:
                    pass
                    #print(f"❌ Geen match voor: {renner} ({norm_renner})")
    return team_points

print("Aantal renners in stand etappe 1:", len(stands[1]))

def calculate_rider_points_matrix(stands):
    # {renner: {etappe: punten}}
    rider_matrix = {}
    for etappe_nr, stand in stands.items():
        etappe_punten = calculate_points_for_etappe(stand)
        for naam, punten in etappe_punten.items():
            if naam not in rider_matrix:
                rider_matrix[naam] = {}
            rider_matrix[naam][etappe_nr] = punten
    return rider_matrix

def calculate_deelnemers_matrix(stands):
    matrix = defaultdict(dict)
    deelnemers = set()
    etappes = set()

    for etappe, stand in stands.items():
        etappes.add(etappe)
        etappe_punten = calculate_points_for_etappe(stand)
        for deelnemer, punten in etappe_punten.items():
            matrix[deelnemer][etappe] = punten
            deelnemers.add(deelnemer)

    return matrix, sorted(deelnemers), sorted(etappes)


def debug_print():
    print("--- DEBUG ---")
    for i in range(1, 4):
        print(f"Etappe {i}: {len(stands[i])} renners")
        if len(stands[i]) > 0:
            print("1e renner:", stands[i][0])
    print("Voorbeeld team:", list(teams.items())[0])

debug_print()

def normalize(name):
    import unicodedata
    return ''.join(
        c for c in unicodedata.normalize('NFKD', name.lower())
        if not unicodedata.combining(c)
    )

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
            .team-container {
                max-width: 600px;
                margin: 0 auto;
                background: white;
                padding: 1rem 2rem;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                border-radius: 6px;
            }
            .team-name {
                font-size: 1.3rem;
                font-weight: bold;
                margin-top: 1rem;
                border-bottom: 2px solid #007bff;
                padding-bottom: 0.3rem;
            }
            ul.renners-list {
                list-style-type: disc;
                padding-left: 1.2rem;
            }
            table {
                width: 60%;
                margin: 0 auto;
                border-collapse: collapse;
                background: white;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                border-radius: 6px;
                overflow: hidden;
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
                showTab('teams');  // Teams tab als default tonen
            }
        </script>
    </head>
    <body>
        <div class="tabs">
    """

    # Eerst de Teams tab
    html += '<div class="tab" id="tab-teams" onclick="showTab(\'teams\')">Teams</div>'

    html += '<div class="tab" id="tab-punten" onclick="showTab(\'punten\')">Punten</div>'
    html += '<div class="tab" id="tab-renners" onclick="showTab(\'renners\')">Rennerspunten</div>'
    # Daarna alle etappes tabs
    for i in range(1, 22):
        html += f'<div class="tab" id="tab-{i}" onclick="showTab({i})">Etappe {i}</div>'

    html += '</div><div class="content">'

    # Teams inhoud
    html += '<div id="content-teams" class="tabcontent" style="display:none;">'
    html += '<h2>Gekozen Renners per Deelnemer</h2>'
    for naam, renners in teams.items():
        html += '<div class="team-container">'
        html += f'<div class="team-name">{naam}</div>'
        html += '<ul class="renners-list">'
        for renner in renners:
            html += f'<li>{renner}</li>'
        html += '</ul></div>'
    html += '</div>'

    # Etappes inhoud
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

    # Puntentelling inhoud
    team_points = calculate_team_points(stands, teams)
    sorted_teams = sorted(team_points.items(), key=lambda x: x[1], reverse=True)
    html += '<div id="content-punten" class="tabcontent" style="display:none;">'
    html += '<h2>Puntenstand Teams</h2>'
    html += '<table><tr><th>Team</th><th>Punten</th></tr>'
    for team, pts in sorted_teams:
        html += f"<tr><td>{team}</td><td>{pts}</td></tr>"
    html += '</table></div>'

    rider_matrix = calculate_rider_points_matrix(stands)
    etappes = list(range(1, 22))

    html += '<div id="content-renners" class="tabcontent" style="display:none;">'
    html += '<h2>Rennerspunten per Etappe</h2>'
    html += '<table><tr><th>Renner</th>'
    for e in etappes:
        html += f"<th>{e}</th>"
    html += "<th>Totaal</th></tr>"

    for renner in sorted(rider_matrix.keys()):
        html += f"<tr><td>{renner}</td>"
        totaal = 0
        for e in etappes:
            p = rider_matrix[renner].get(e, 0)
            totaal += p
            html += f"<td>{p if p > 0 else ''}</td>"
        html += f"<td class='total'>{totaal}</td></tr>"

    html += '</table></div>'

    matrix, deelnemers, etappes = calculate_deelnemers_matrix(stands)

    # Maak nieuwe tabknop
    html += '<div class="tab" id="tab-matrix" onclick="showTab(\'matrix\')">Puntenmatrix</div>'

    # Maak de content
    html += '<div id="content-matrix" class="tabcontent" style="display:none;">'
    html += '<h2>Puntenmatrix per deelnemer</h2>'
    html += '<table><tr><th>Deelnemer</th><th>Totaal</th>'

    for e in etappes:
        html += f"<th>E{e}</th>"
    html += "</tr>"

    # Max punten per etappe bepalen voor groene markering
    max_per_etappe = {e: max(matrix[d].get(e, 0) for d in deelnemers) for e in etappes}

    for deelnemer in deelnemers:
        html += f"<tr><td>{deelnemer}</td>"
        totaal = sum(matrix[deelnemer].get(e, 0) for e in etappes)
        html += f"<td class='total'>{totaal}</td>"
        for e in etappes:
            p = matrix[deelnemer].get(e, 0)
            cell_class = "highlight" if p == max_per_etappe[e] and p > 0 else ""
            html += f"<td class='{cell_class}'>{p if p > 0 else ''}</td>"
        html += "</tr>"

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

@app.route("/punten")
def show_points():
    team_points = calculate_team_points(stands, teams)
    html = """
    <html><head>
        <title>Tourpool Puntenstand</title>
        <style>
            body { font-family: Arial,sans-serif; background: #f4f4f4; padding: 2rem; text-align: center; }
            table { margin: 0 auto; border-collapse: collapse; background: white; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
            th, td { padding: 10px 20px; border: 1px solid #ddd; }
            th { background: #333; color: white; }
            tr:nth-child(even) { background: #f9f9f9; }
        </style>
    </head><body>
        <h1>Puntenstand Teams</h1>
        <table>
            <tr><th>Team</th><th>Punten</th></tr>
    """
    # Sorteer teams op punten, hoog naar laag
    sorted_teams = sorted(team_points.items(), key=lambda x: x[1], reverse=True)
    for team, pts in sorted_teams:
        html += f"<tr><td>{team}</td><td>{pts}</td></tr>"
    html += "</table></body></html>"
    return render_template_string(html)

@app.route("/rennerspunten")
def show_rider_points():
    rider_matrix = calculate_rider_points_matrix(stands)
    etappes = list(range(1, 22))

    html = """
    <html><head>
        <title>Rennerspunten per Etappe</title>
        <style>
            body { font-family: Arial, sans-serif; background: #f4f4f4; padding: 2rem; text-align: center; }
            table { margin: 0 auto; border-collapse: collapse; background: white; box-shadow: 0 2px 8px rgba(0,0,0,0.1); font-size: 0.9rem; }
            th, td { padding: 6px 10px; border: 1px solid #ddd; text-align: center; }
            th { background: #333; color: white; }
            tr:nth-child(even) { background: #f9f9f9; }
            .total { font-weight: bold; background: #e0ffe0; }
        </style>
    </head><body>
        <h1>Rennerspunten per Etappe</h1>
        <table>
            <tr>
                <th>Renner</th>"""
    for e in etappes:
        html += f"<th>{e}</th>"
    html += "<th>Totaal</th></tr>"

    for renner in sorted(rider_matrix.keys()):
        html += f"<tr><td>{renner}</td>"
        totaal = 0
        for e in etappes:
            p = rider_matrix[renner].get(e, 0)
            totaal += p
            html += f"<td>{p if p > 0 else ''}</td>"
        html += f"<td class='total'>{totaal}</td></tr>"

    html += "</table></body></html>"
    return render_template_string(html)


if __name__ == "__main__":
    app.run()

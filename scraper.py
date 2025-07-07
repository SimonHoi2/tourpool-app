import requests
from bs4 import BeautifulSoup

def scrape_data(etappe_nr):
    url = f"https://www.procyclingstats.com/race/tour-de-france/2025/stage-{etappe_nr}"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    table = soup.find("table", class_="results")
    if not table:
        raise ValueError("Tabel niet gevonden")

    data = []
    for row in table.find_all("tr"):
        rider_td = row.find("td", class_="ridername")
        position_td = row.find("td")

        if rider_td and position_td:
            achternaam_el = rider_td.find("span", class_="uppercase")
            voornaam_txt = achternaam_el.next_sibling.strip() if achternaam_el else ""
            achternaam = achternaam_el.get_text(strip=True) if achternaam_el else ""
            naam = f"{voornaam_txt} {achternaam}".strip()

            position = position_td.get_text(strip=True)
            data.append({
                "position": position,
                "naam": naam
            })

    return data

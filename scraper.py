import requests
from bs4 import BeautifulSoup

def scrape_data():
    url = "https://racecenter.letour.fr/en/rankings/1/ite"  # Vervang dit met de echte URL
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    table = soup.find("table")
    data = []
    for row in table.find_all("tr")[1:]:
        cols = row.find_all("td")
        data.append({
            "naam": cols[0].text.strip(),
            "punten": cols[1].text.strip()
        })
    return data
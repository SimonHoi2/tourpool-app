import pandas as pd
from collections import defaultdict

def load_teams_xlsx(path="teams.xlsx"):
    df = pd.read_excel(path)
    teams = defaultdict(list)
    for _, row in df.iterrows():
        naam = row["naam"]
        renner = row["renner"]
        teams[naam].append(renner)
    return dict(teams)


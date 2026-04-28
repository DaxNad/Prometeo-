import json

from pathlib import Path

COMP_PATH = Path.home() / "PROMETEO" / "data" / "local_smf" / "prometeo_componenti.json"

# temporaneo: quantità mock (da sostituire con SMF reale)
QUANTITA = {
    "12077": 100,
    "12058": 8,
    "12062": 72
}

def load_componenti():
    return json.load(open(COMP_PATH))

def calcola_counter(data):
    counter = {}
    for codice, info in data.items():
        for c in info["componenti"]:
            counter[c] = counter.get(c, 0) + 1
    return counter

def build_sequence():
    data = load_componenti()
    counter = calcola_counter(data)

    planner = []

    for codice, info in data.items():
        score_componenti = sum(counter.get(c, 0) for c in info["componenti"])
        q = QUANTITA.get(codice, 0)

        henn = 1 if "469122" in info["componenti"] else 0

        score = score_componenti + (q / 50) + (henn * 2)

        planner.append({
            "article": codice,
            "score": round(score, 2),
            "quantity": q,
            "henn": bool(henn)
        })

    planner.sort(key=lambda x: -x["score"])

    return planner

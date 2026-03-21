STATIONS_SEQUENCE = [
    "lavaggio",
    "collaudo_visivo",
    "guaina",
    "marcature",
    "henn",
    "innesto_rapido",
    "crimp_zaw",
    "pidmill",
    "collaudo_pressione",
    "imballo",
]


def is_valid_station(station: str) -> bool:
    return station in STATIONS_SEQUENCE

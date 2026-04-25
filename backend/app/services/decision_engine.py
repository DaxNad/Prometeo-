import json
from pathlib import Path

CLUSTER_PATH = Path("/Users/davidepiangiolino/Documents/PROMETEO/backend/app/data/shared_component_clusters.json")

def load_clusters():
    if not CLUSTER_PATH.exists():
        return []
    return json.loads(CLUSTER_PATH.read_text())


def match_cluster(item, clusters):
    comps = set(item.get("shared_components", []))
    for c in clusters:
        if c["component"] in comps:
            return c
    return None


def compute_decision(item, clusters):
    open_events = item.get("open_events_total", 0)
    priority = item.get("customer_priority", "MEDIA")
    cluster = match_cluster(item, clusters)

    # BLOCCO HARD
    if open_events > 0:
        return {
            "decision": "BLOCK",
            "decision_reason": "eventi attivi",
            "decision_score": 100
        }

    # CLUSTER COMPONENTI
    if cluster:
        return {
            "decision": "ALLOW",
            "decision_reason": f"cluster componente {cluster['component']}",
            "decision_score": 80
        }

    # PRIORITÀ
    if priority == "CRITICA":
        return {
            "decision": "ALLOW",
            "decision_reason": "priorità cliente",
            "decision_score": 90
        }

    return {
        "decision": "ALLOW",
        "decision_reason": "ok",
        "decision_score": 50
    }


def apply_decisions(items):
    clusters = load_clusters()
    # clusters già caricati
    result = []
    for item in items:
        item.update(compute_decision(item, clusters))
        result.append(item)
    return result

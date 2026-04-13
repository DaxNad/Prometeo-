from sqlalchemy.orm import Session

from app.services.sequence_planner import _get_open_events_by_station
from app.db.session import SessionLocal


def test_get_open_events_by_station_handles_missing_table():
    # Usa SQLite senza tabella 'events': la funzione deve restituire dict vuoto
    db: Session = SessionLocal()
    try:
        result = _get_open_events_by_station(db)
        assert isinstance(result, dict)
        assert result == {}
    finally:
        db.close()


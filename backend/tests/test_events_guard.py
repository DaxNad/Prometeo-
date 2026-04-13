from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.services.sequence_planner import _get_open_events_by_station


def test_get_open_events_by_station_handles_missing_table():
    # Usa un DB SQLite in-memory isolato senza la tabella 'events':
    # la funzione deve restituire dict vuoto senza propagare eccezioni.
    engine = create_engine("sqlite:///:memory:")
    IsolatedSession = sessionmaker(bind=engine)
    db: Session = IsolatedSession()
    try:
        result = _get_open_events_by_station(db)
        assert isinstance(result, dict)
        assert result == {}
    finally:
        db.close()


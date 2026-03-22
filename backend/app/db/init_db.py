from backend.app.db.session import Base, engine
from backend.app.db import models  # noqa: F401


def init_db():
    Base.metadata.create_all(bind=engine)

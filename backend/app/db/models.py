from sqlalchemy import Column, DateTime, Integer, String, Text, func
from backend.app.db.session import Base


class EventRecord(Base):
    __tablename__ = "event_records"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(100), nullable=False, index=True)
    source = Column(String(100), nullable=True, index=True)
    payload = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class StateRecord(Base):
    __tablename__ = "state_records"

    id = Column(Integer, primary_key=True, index=True)
    state_key = Column(String(150), nullable=False, unique=True, index=True)
    state_value = Column(Text, nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

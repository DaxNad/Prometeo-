from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class EventsRepository(ABC):
    @abstractmethod
    def list_events(self) -> list[dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def list_active_events(self) -> list[dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def create_event(self, payload: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def get_event(self, event_id: str) -> dict[str, Any] | None:
        raise NotImplementedError

    @abstractmethod
    def update_event(self, event_id: str, payload: dict[str, Any]) -> dict[str, Any] | None:
        raise NotImplementedError

    @abstractmethod
    def close_event(self, event_id: str, closed_by: str) -> dict[str, Any] | None:
        raise NotImplementedError

    @abstractmethod
    def close_events_by_line(self, line: str, closed_by: str) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def list_station_states(self) -> list[dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def get_station_state(self, line: str, station: str) -> dict[str, Any] | None:
        raise NotImplementedError

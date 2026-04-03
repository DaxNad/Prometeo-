from __future__ import annotations

import asyncio
from typing import Any

from .service import AgentRuntimeService


async def analyze_event_background(
    *,
    source: str,
    line_id: str,
    event_type: str,
    severity: str | None,
    payload: dict[str, Any],
) -> None:
    try:
        service = AgentRuntimeService()
        await service.analyze(
            source=source,
            line_id=line_id,
            event_type=event_type,
            severity=severity or "info",
            payload=payload,
        )
    except Exception:
        # non deve rompere il flusso principale eventi
        pass


def trigger_runtime_analysis(
    *,
    source: str,
    line_id: str,
    event_type: str,
    severity: str | None,
    payload: dict[str, Any],
) -> None:
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(
            analyze_event_background(
                source=source,
                line_id=line_id,
                event_type=event_type,
                severity=severity,
                payload=payload,
            )
        )
    except RuntimeError:
        asyncio.run(
            analyze_event_background(
                source=source,
                line_id=line_id,
                event_type=event_type,
                severity=severity,
                payload=payload,
            )
        )

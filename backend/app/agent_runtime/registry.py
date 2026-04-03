from __future__ import annotations

from .tools.event_inspector import EventInspectorTool


class ToolRegistry:
    def __init__(self) -> None:
        self._tools = {
            "event_inspector": EventInspectorTool(),
        }

    def get(self, name: str):
        return self._tools[name]

    def list_tools(self) -> list[str]:
        return list(self._tools.keys())

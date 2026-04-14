from __future__ import annotations

from typing import TypedDict, List, Dict, Any


class ConstraintSet(TypedDict, total=False):
    hard: List[Dict[str, Any]]
    soft: List[Dict[str, Any]]


class ObjectiveSpec(TypedDict, total=False):
    goals: List[Dict[str, Any]]


class SolveResult(TypedDict, total=False):
    sequence: List[str]
    meta: Dict[str, Any]


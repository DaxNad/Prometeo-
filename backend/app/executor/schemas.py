from pydantic import BaseModel
from typing import Literal, Any, Optional

CertaintyLevel = Literal["CERTO", "INFERITO", "DA_VERIFICARE"]
ExecutionAction = Literal["run_test", "crosscheck_bom"]


class ExecutionTask(BaseModel):
    action: ExecutionAction
    target_type: Literal[
        "order",
        "code",
        "station",
        "component",
        "system",
    ]
    target_id: Optional[str] = None
    payload: dict[str, Any] = {}
    source: Literal["system"]


class ExecutionResult(BaseModel):
    success: bool
    data: dict[str, Any] = {}
    error: Optional[str] = None

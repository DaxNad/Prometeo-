from pydantic import BaseModel
from typing import Literal, Any, Optional


class ExecutionTask(BaseModel):
    action: Literal["run_test"]
    target_type: Literal["system"]
    target_id: Optional[str] = None
    payload: dict[str, Any] = {}
    source: Literal["system"]


class ExecutionResult(BaseModel):
    success: bool
    data: dict[str, Any] = {}
    error: Optional[str] = None

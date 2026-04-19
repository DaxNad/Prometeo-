from app.executor.schemas import ExecutionTask, ExecutionResult


def run_test_tool(task: ExecutionTask) -> ExecutionResult:
    return ExecutionResult(
        success=True,
        data={
            "message": "executor_test_ok",
            "payload": task.payload,
        },
    )

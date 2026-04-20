from fastapi import APIRouter
from datetime import datetime

from app.executor.service import execute_task

router = APIRouter()


def build_run_test_task():

    return {

        "task_id":

            f"EXEC-RUNTEST-{datetime.utcnow().timestamp()}",


        "origin": {

            "module": "dev_executor_endpoint",

            "reason": "manual_trigger_run_test"
        },


        "target": {

            "layer": "planner_support",

            "files": []
        },


        "action": {

            "type": "run_test",

            "description": "run planner compatibility checks"
        },


        "constraints": {

            "domain_rules_required": True,

            "preserve_order_identity": True,

            "preserve_event_model": True,

            "smf_bridge_mandatory": True
        },


        "expected_effect": {

            "domain_entities_affected": [

                "ProductionEvent"
            ],

            "event_type":

                "executor_test_executed",

            "reversible": True
        },


        "validation": {

            "checks_required": [

                "sequence_compat_check",

                "machine_load"
            ],

            "success_criteria":

                "planner endpoints respond"
        },


        "trace": {

            "created_at":

                datetime.utcnow().isoformat(),

            "created_by":

                "DEV_ENDPOINT",

            "correlation_id":

                "EXECUTOR-RUNTEST"
        }

    }


@router.post("/dev/executor/run-test")
def run_executor_test():

    task = build_run_test_task()

    result = execute_task(task)

    return result


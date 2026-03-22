from fastapi import APIRouter

from ..services import devos_service

router = APIRouter(tags=["Development OS"])


@router.get("/dev/status")
def get_dev_status():
    return devos_service.get_dev_status()


@router.get("/dev/tasks")
def get_dev_tasks():
    return devos_service.get_dev_tasks()


@router.get("/dev/logs")
def get_dev_logs():
    return devos_service.get_dev_logs()


@router.get("/dev/milestones")
def get_dev_milestones():
    return devos_service.get_dev_milestones()

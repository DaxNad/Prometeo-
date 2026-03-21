from fastapi import APIRouter

from ..services.devos_service import devos_service

router = APIRouter(prefix="/dev", tags=["Development OS"])


@router.get("/status")
def get_dev_status():
    return devos_service.get_status()


@router.get("/tasks")
def get_dev_tasks():
    return devos_service.get_tasks()


@router.get("/logs")
def get_dev_logs():
    return devos_service.get_logs()


@router.get("/milestones")
def get_dev_milestones():
    return devos_service.get_milestones()

from fastapi import APIRouter
import os

router = APIRouter()

@router.get("/version")
def version():
    return {"service":"PROMETEO CORE","version":os.getenv("PROMETEO_VERSION","0.3.1")}

@router.get("/auth/verify")
def verify():
    return {"ok":True}

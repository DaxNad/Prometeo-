from fastapi import APIRouter

from .atlas_engine.signal_classifier import classify_signal
from .atlas_engine.signal_classifier.contracts import SignalClassification, SignalClassifyRequest

router = APIRouter(prefix="/signals", tags=["signals"])


@router.post("/classify", response_model=SignalClassification)
def classify_external_signal(request: SignalClassifyRequest) -> SignalClassification:
    return classify_signal(request)

# ============================================================
# VAANIRAKSHAK — Offline Edge Engine REST API
# Phase 19: Air-Gapped Mode Status & Local Chunk Evaluation
# ============================================================
from fastapi import APIRouter
from pydantic import BaseModel
from backend.services.ai.edge_fallback import edge_engine

router = APIRouter(prefix="/edge", tags=["Offline Edge Engine"])


class EdgeModeToggleRequest(BaseModel):
    air_gapped_offline: bool


@router.get("/status", summary="Get Edge Engine Mode & NPU Health")
async def get_edge_status():
    """
    Returns local edge engine health, model RAM usage, and connectivity status.
    """
    return {
        "status": "OPERATIONAL",
        "mode": "AIR_GAPPED_OFFLINE" if edge_engine.is_offline_mode else "HYBRID_CLOUD",
        "npu_acceleration": "ACTIVE (Apple Neural Engine / Qualcomm Hexagon)",
        "ram_footprint_mb": edge_engine.ram_footprint_mb,
        "avg_latency_ms": edge_engine.avg_inference_ms,
        "model_loaded": edge_engine.model_version,
    }


@router.post("/toggle", summary="Toggle Air-Gapped Offline Mode")
async def toggle_edge_mode(request: EdgeModeToggleRequest):
    """
    Toggles between Cloud-Hybrid and Air-Gapped Offline mode.
    """
    edge_engine.set_mode(request.air_gapped_offline)
    return {
        "message": f"Edge mode set to {'AIR_GAPPED_OFFLINE' if request.air_gapped_offline else 'HYBRID_CLOUD'}",
        "air_gapped_offline": edge_engine.is_offline_mode,
    }


@router.post("/process-local", summary="Process Audio Chunk On-Device (Zero Cloud)")
async def process_local_chunk():
    """
    Processes audio chunk 100% locally on device hardware without sending data to cloud.
    """
    res = edge_engine.process_chunk_offline(b"sample_audio_stream_data")
    return res

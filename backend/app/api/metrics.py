from fastapi import APIRouter, Query
from typing import Optional
from app.core.metrics import metrics_tracker

router = APIRouter(prefix="/api/metrics", tags=["metrics"])


@router.get("/stats")
async def get_metrics_stats(hours: Optional[int] = Query(None, description="Last N hours, or all time if None")):
    """Get aggregated metrics statistics"""
    return metrics_tracker.get_stats(hours=hours)


@router.get("/health")
async def metrics_health():
    """Health check for metrics system"""
    try:
        stats = metrics_tracker.get_stats(hours=1)
        return {
            "status": "healthy",
            "has_data": "error" not in stats
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

from fastapi import APIRouter

# Create router
router = APIRouter()

# Status endpoint for connection checking
@router.get("/status")
def get_status():
    """Return pong to indicate backend is running"""
    return {"status": "pong"}

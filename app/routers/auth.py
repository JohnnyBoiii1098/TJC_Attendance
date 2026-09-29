from fastapi import APIRouter, HTTPException, Header, Depends, status
from typing import Optional
from app.config import ADMIN_PASSCODE
from app.schemas import VerifyPinRequest, VerifyPinResponse

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

from fastapi import Query

def require_admin_pin(
    x_admin_pin: Optional[str] = Header(None, alias="X-Admin-PIN"),
    pin: Optional[str] = Query(None)
):
    """
    Dependency to protect endpoints with the access passcode.
    Can be provided via the HTTP header 'X-Admin-PIN' or query parameter '?pin=...'.
    """
    if not ADMIN_PASSCODE:
        # If no passcode is set in .env, permit actions freely
        return True

    candidate = (x_admin_pin or pin or "").strip()
    if candidate != ADMIN_PASSCODE.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing access passcode. Please authenticate."
        )
    return True

@router.post("/verify", response_model=VerifyPinResponse)
def verify_pin(payload: VerifyPinRequest):
    """Verifies user-submitted admin PIN."""
    if not ADMIN_PASSCODE:
        return VerifyPinResponse(valid=True, message="Admin PIN protection is disabled.")
    
    if payload.pin.strip() == ADMIN_PASSCODE.strip():
        return VerifyPinResponse(valid=True, message="PIN verified successfully.")
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect PIN."
    )

@router.get("/status")
def auth_status(x_admin_pin: Optional[str] = Header(None, alias="X-Admin-PIN")):
    """Checks whether the currently supplied header PIN is valid."""
    is_valid = bool(ADMIN_PASSCODE and x_admin_pin and x_admin_pin.strip() == ADMIN_PASSCODE.strip())
    return {
        "is_authenticated": is_valid,
        "pin_required": bool(ADMIN_PASSCODE)
    }

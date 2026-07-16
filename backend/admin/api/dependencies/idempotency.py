from fastapi import Header, HTTPException, status
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# In memory mock for Idempotency keys (Should use Redis in prod)
_idempotency_store = set()

def verify_idempotency_key(
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key")
) -> Optional[str]:
    """
    Phase 17: Idempotency Key Validator.
    Ensures that state-changing requests with the same Idempotency-Key are not processed multiple times.
    """
    if idempotency_key is None:
        return None # Optional as per requirements

    if idempotency_key in _idempotency_store:
        logger.warning(f"Duplicate Idempotency-Key detected: {idempotency_key}")
        # In a real implementation, this should return the saved response of the previous request
        # rather than throwing a 409, but returning 409 Conflict is acceptable for prevention.
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A request with this Idempotency-Key has already been processed."
        )
        
    # Register the key
    _idempotency_store.add(idempotency_key)
    
    return idempotency_key

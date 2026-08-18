import os

from fastapi import HTTPException, Request
from clerk_backend_api import authenticate_request,AuthenticateRequestOptions
from app.settings.config import settings


FRONTEND_URL = settings.FRONTEND_URL.rstrip("/")

def get_current_user(request: Request):
    state = authenticate_request(
        request,
        AuthenticateRequestOptions(
            secret_key=settings.CLERK_SECRET_KEY, 
            authorized_parties=["http://localhost:3000",
                                FRONTEND_URL],
            accepts_token=["session_token"],
        ),
    )

    if not state.is_signed_in:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized",
        )

    return state.payload
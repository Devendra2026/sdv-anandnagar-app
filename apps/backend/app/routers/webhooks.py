
import json


from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from svix.webhooks import Webhook

from app.database import get_db
from app.database_models.users import User
from app.settings.config import settings

router = APIRouter()


@router.post("/webhook")
async def clerk_webhook(
    request: Request,
    db: Session = Depends(get_db),
):
    webhook_secret = settings.CLERK_WEBHOOK_SECRET

    if not webhook_secret:
        raise HTTPException(
            status_code=500,
            detail="CLERK_WEBHOOK_SECRET not configured",
        )

    payload = await request.body()

    headers = {
        "svix-id": request.headers.get("svix-id"),
        "svix-timestamp": request.headers.get("svix-timestamp"),
        "svix-signature": request.headers.get("svix-signature"),
    }

    try:
        wh = Webhook(webhook_secret)
        wh.verify(payload, headers)

        event = json.loads(payload)

    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid webhook signature",
        )

    event_type = event.get("type")

    if event_type not in ["user.created", "user.updated"]:
        return {"message": "Ignored"}

    data = event.get("data", {})

    clerk_id = data.get("id")

    if not clerk_id:
        raise HTTPException(
            status_code=400,
            detail="Clerk user id missing",
        )

    email = None
    email_addresses = data.get("email_addresses") or []

    if email_addresses:
        primary_email_id = data.get("primary_email_address_id")

        primary_email = next(
            (
                email_item
                for email_item in email_addresses
                if email_item.get("id") == primary_email_id
            ),
            email_addresses[0],
        )

        email = primary_email.get("email_address")

    first_name = data.get("first_name") or ""
    last_name = data.get("last_name") or ""

    name = f"{first_name} {last_name}".strip()

    existing_user = (
        db.query(User)
        .filter(User.clerk_id == clerk_id)
        .first()
    )

    if existing_user:
        existing_user.name = name
        existing_user.email = email

        db.commit()
        db.refresh(existing_user)

        return {
            "message": "User updated successfully",
            "id": existing_user.id,
        }

    new_user = User(
        clerk_id=clerk_id,
        name=name,
        email=email,
        role="user",
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User created successfully",
        "id": new_user.id,
    }


# '''
# admin - EO
# Head Clerk
# Computer Operator
# user
# '''

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.clerk_auth import get_current_user
from app.database import get_db
from app.database_models.users import User


def get_current_db_user(
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    clerk_id = (
        user.get("sub")
        or user.get("id")
        or user.get("clerk_id")
        or user.get("user_id")
    )

    if not clerk_id:
        raise HTTPException(
            status_code=401,
            detail="Clerk user id not found in token.",
        )

    db_user = (
        db.query(User)
        .filter(User.clerk_id == clerk_id)
        .first()
    )

    if not db_user:
        raise HTTPException(
            status_code=404,
            detail="Current user not found in database.",
        )

    return db_user


def require_roles(*allowed_roles: str):
    def checker(
        db_user: User = Depends(get_current_db_user),
    ):
        role = (db_user.role or "").lower()

        if role not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail="You don't have permission to perform this action.",
            )

        return db_user

    return checker

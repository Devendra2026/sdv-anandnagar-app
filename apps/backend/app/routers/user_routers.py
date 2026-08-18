

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.database_models.users import User
from app.schemas import user_schema
from app.auth.clerk_auth import get_current_user
from app.auth.permissions import require_roles

router = APIRouter()


# Reading all users data
@router.get("/")
def read_user_data(
    permit=Depends(require_roles("admin", "clerk", "operator")),
    db: Session = Depends(get_db),
):
    users = db.query(User).all()
    return users


# Reading logged-in database user
@router.get("/me")
def read_current_user(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    clerk_id = (
        current_user.get("sub")
        or current_user.get("id")
        or current_user.get("clerk_id")
    )

    if not clerk_id:
        raise HTTPException(
            status_code=401,
            detail="Clerk user id not found in token",
        )

    user = db.query(User).filter(User.clerk_id == clerk_id).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="Current user not found in database",
        )

    return user


# Reading a specific user
@router.get("/{user_id}")
def read_specific_user(
    user_id: int,
    permit=Depends(require_roles("admin", "clerk", "operator")),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found!",
        )

    return user


# Updating a specific user
@router.put("/{user_id}")
def update_user_data(
    user_id: int,
    user: user_schema.UserUpdate,
    permit=Depends(require_roles("admin", "clerk", "operator")),
    db: Session = Depends(get_db),
):
    db_user = db.query(User).filter(User.id == user_id).first()

    if not db_user:
        raise HTTPException(
            status_code=404,
            detail="User Not Found",
        )

    try:
        update_data = user.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_user, field, value)

        db.commit()
        db.refresh(db_user)

        return {
            "message": "User Information Updated Successfully",
        }

    except Exception as e:
        db.rollback()
        print("USER UPDATE ERROR:", e)

        raise HTTPException(
            status_code=500,
            detail="Error Updating User Information",
        )


# Deleting a specific user
@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    permit=Depends(require_roles("admin")),
    db: Session = Depends(get_db),
):
    db_user = db.query(User).filter(User.id == user_id).first()

    if not db_user:
        raise HTTPException(
            status_code=404,
            detail="User Deletion Failed",
        )

    try:
        db.delete(db_user)
        db.commit()

        return {
            "message": "User Deleted Successfully!",
        }

    except Exception:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Error deleting user!",
        )

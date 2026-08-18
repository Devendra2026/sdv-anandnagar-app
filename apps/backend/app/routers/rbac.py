import re

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session, selectinload

from app.auth.permissions import require_roles
from app.database import get_db
from app.database_models.rbac import Permission, Role
from app.schemas.rbac_schema import (
    PermissionResponse,
    RoleCreate,
    RolePermissionsUpdate,
    RoleResponse,
    RoleUpdate,
)


router = APIRouter()


DEFAULT_PERMISSIONS = [
    {
        "key": "permissions.read",
        "label": "View Permissions",
        "group": "RBAC",
        "description": "Can view available permissions.",
    },
    {
        "key": "roles.read",
        "label": "View Roles",
        "group": "RBAC",
        "description": "Can view role details.",
    },
    {
        "key": "roles.create",
        "label": "Create Roles",
        "group": "RBAC",
        "description": "Can create roles.",
    },
    {
        "key": "roles.update",
        "label": "Update Roles",
        "group": "RBAC",
        "description": "Can update role details.",
    },
    {
        "key": "roles.delete",
        "label": "Delete Roles",
        "group": "RBAC",
        "description": "Can delete roles.",
    },
    {
        "key": "roles.permissions.update",
        "label": "Update Role Permissions",
        "group": "RBAC",
        "description": "Can change permissions assigned to a role.",
    },
    {
        "key": "contacts.read",
        "label": "View Contact Forms",
        "group": "Contact Forms",
        "description": "Can view contact form submissions.",
    },
    {
        "key": "contacts.update",
        "label": "Update Contact Forms",
        "group": "Contact Forms",
        "description": "Can update contact form submissions.",
    },
    {
        "key": "contacts.delete",
        "label": "Delete Contact Forms",
        "group": "Contact Forms",
        "description": "Can delete contact form submissions.",
    },
    {
        "key": "grievances.read",
        "label": "View Grievances",
        "group": "Public Grievance",
        "description": "Can view grievance submissions.",
    },
    {
        "key": "grievances.update",
        "label": "Update Grievances",
        "group": "Public Grievance",
        "description": "Can update grievance submissions.",
    },
    {
        "key": "grievances.delete",
        "label": "Delete Grievances",
        "group": "Public Grievance",
        "description": "Can delete grievance submissions.",
    },
    {
        "key": "users.read",
        "label": "View Users",
        "group": "Users",
        "description": "Can view users.",
    },
    {
        "key": "users.update",
        "label": "Update Users",
        "group": "Users",
        "description": "Can update users.",
    },
    {
        "key": "users.delete",
        "label": "Delete Users",
        "group": "Users",
        "description": "Can delete users.",
    },
]


def normalize_role_key(value: str) -> str:
    key = re.sub(r"[^a-z0-9]+", "_", value.strip().lower())
    return key.strip("_")


def ensure_default_permissions(db: Session) -> None:
    existing_keys = {
        permission_key
        for (permission_key,) in db.query(Permission.key).all()
    }

    missing_permissions = [
        Permission(**permission)
        for permission in DEFAULT_PERMISSIONS
        if permission["key"] not in existing_keys
    ]

    if not missing_permissions:
        return

    db.add_all(missing_permissions)
    db.commit()


def get_role_or_404(db: Session, role_id: int) -> Role:
    role = (
        db.query(Role)
        .options(selectinload(Role.permissions))
        .filter(Role.id == role_id)
        .first()
    )

    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )

    return role


def get_permissions_from_keys(
    db: Session,
    permission_keys: list[str],
) -> list[Permission]:
    clean_keys = []
    for key in permission_keys:
        clean_key = key.strip()
        if clean_key and clean_key not in clean_keys:
            clean_keys.append(clean_key)

    if not clean_keys:
        return []

    permissions = (
        db.query(Permission)
        .filter(Permission.key.in_(clean_keys))
        .all()
    )
    found_keys = {permission.key for permission in permissions}
    missing_keys = sorted(set(clean_keys) - found_keys)

    if missing_keys:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid permission keys: {', '.join(missing_keys)}",
        )

    return permissions


@router.get(
    "/permissions",
    response_model=list[PermissionResponse],
    summary="List Permissions",
)
def list_permissions(
    permit=Depends(require_roles("admin")),
    db: Session = Depends(get_db),
):
    ensure_default_permissions(db)

    permissions = (
        db.query(Permission)
        .order_by(Permission.group, Permission.label)
        .all()
    )

    return permissions


@router.get(
    "/roles",
    response_model=list[RoleResponse],
    summary="List Roles",
)
def list_roles(
    permit=Depends(require_roles("admin")),
    db: Session = Depends(get_db),
):
    roles = (
        db.query(Role)
        .options(selectinload(Role.permissions))
        .order_by(Role.name)
        .all()
    )

    return roles


@router.post(
    "/roles",
    response_model=RoleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Role",
)
def create_role(
    role: RoleCreate,
    permit=Depends(require_roles("admin")),
    db: Session = Depends(get_db),
):
    ensure_default_permissions(db)

    role_name = role.name.strip()
    role_key = normalize_role_key(role.key or role_name)

    if not role_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role name is required",
        )

    if not role_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role key is required",
        )

    existing_role = (
        db.query(Role)
        .filter(
            (func.lower(Role.key) == role_key)
            | (func.lower(Role.name) == role_name.lower())
        )
        .first()
    )

    if existing_role:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Role already exists",
        )

    permissions = get_permissions_from_keys(db, role.permission_keys)

    db_role = Role(
        key=role_key,
        name=role_name,
        description=role.description,
        is_system=False,
    )
    db_role.permissions = permissions

    db.add(db_role)
    db.commit()
    db.refresh(db_role)

    return get_role_or_404(db, db_role.id)


@router.get(
    "/roles/{role_id}",
    response_model=RoleResponse,
    summary="Get Role",
)
def get_role(
    role_id: int,
    permit=Depends(require_roles("admin")),
    db: Session = Depends(get_db),
):
    return get_role_or_404(db, role_id)


@router.put(
    "/roles/{role_id}",
    response_model=RoleResponse,
    summary="Update Role",
)
def update_role(
    role_id: int,
    role: RoleUpdate,
    permit=Depends(require_roles("admin")),
    db: Session = Depends(get_db),
):
    db_role = get_role_or_404(db, role_id)
    role_name = role.name.strip()

    if not role_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role name is required",
        )

    if db_role.is_system:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="System role cannot be updated",
        )

    duplicate_role = (
        db.query(Role)
        .filter(func.lower(Role.name) == role_name.lower())
        .filter(Role.id != role_id)
        .first()
    )

    if duplicate_role:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Role name already exists",
        )

    db_role.name = role_name
    db_role.description = role.description

    db.commit()
    db.refresh(db_role)

    return get_role_or_404(db, role_id)


@router.delete(
    "/roles/{role_id}",
    summary="Delete Role",
)
def delete_role(
    role_id: int,
    permit=Depends(require_roles("admin")),
    db: Session = Depends(get_db),
):
    db_role = get_role_or_404(db, role_id)

    if db_role.is_system:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="System role cannot be deleted",
        )

    db.delete(db_role)
    db.commit()

    return {"message": "Role deleted successfully"}


@router.put(
    "/roles/{role_id}/permissions",
    response_model=RoleResponse,
    summary="Update Role Permissions",
)
def update_role_permissions(
    role_id: int,
    role_permissions_update: RolePermissionsUpdate,
    permit=Depends(require_roles("admin")),
    db: Session = Depends(get_db),
):
    ensure_default_permissions(db)

    db_role = get_role_or_404(db, role_id)

    if db_role.is_system:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="System role permissions cannot be updated",
        )

    db_role.permissions = get_permissions_from_keys(
        db,
        role_permissions_update.permission_keys,
    )

    db.commit()
    db.refresh(db_role)

    return get_role_or_404(db, role_id)

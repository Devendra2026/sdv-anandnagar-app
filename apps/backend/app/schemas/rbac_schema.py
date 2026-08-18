from datetime import datetime

from pydantic import BaseModel, Field


class PermissionResponse(BaseModel):
    id: int
    key: str
    label: str
    group: str
    description: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class RoleCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    key: str | None = Field(default=None, max_length=80)
    description: str | None = None
    permission_keys: list[str] = Field(default_factory=list)


class RoleUpdate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    description: str | None = None


class RolePermissionsUpdate(BaseModel):
    permission_keys: list[str]


class RoleResponse(BaseModel):
    id: int
    key: str
    name: str
    description: str | None = None
    is_system: bool
    created_at: datetime
    permissions: list[PermissionResponse] = Field(default_factory=list)

    model_config = {"from_attributes": True}

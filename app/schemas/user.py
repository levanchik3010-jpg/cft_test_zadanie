from pydantic import BaseModel
from app.models.user import UserRole


class UserOut(BaseModel):
    id: int
    username: str
    full_name: str | None
    role: UserRole

    model_config = {"from_attributes": True}


class UserCreate(BaseModel):
    username: str
    password: str
    full_name: str | None = None
    role: UserRole = UserRole.employee

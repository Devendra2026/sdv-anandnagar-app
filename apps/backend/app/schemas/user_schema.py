
from pydantic import EmailStr, BaseModel

class UserCreate(BaseModel):
    name : str
    email : EmailStr
    role : str
    clerk_id : str

class UserUpdate(BaseModel):
    name : str | None = None
    email : EmailStr | None = None
    role : str | None = None
    
    
    
    
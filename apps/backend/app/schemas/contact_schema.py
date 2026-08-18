
from pydantic import EmailStr, BaseModel


class ContactCreate(BaseModel):
    name : str
    email : EmailStr
    phone : str
    subject : str
    message : str

    
class ContactUpdate(BaseModel):
    name : str | None = None
    email : EmailStr | None = None
    phone : str | None = None
    subject : str | None = None
    message : str | None = None
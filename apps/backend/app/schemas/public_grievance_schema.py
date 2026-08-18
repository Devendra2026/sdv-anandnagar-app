
from pydantic import EmailStr, BaseModel

class GrievanceCreate(BaseModel):
    full_name : str
    email : EmailStr
    mobile_number : str
    complaint_category : str
    municipal_ward : str
    incident_address : str
    description : str
    
class GrievanceUpdate(BaseModel):
    full_name : str | None = None
    email : EmailStr | None = None
    mobile_number : str | None = None
    complaint_category : str | None = None
    municipal_ward : str | None = None
    incident_address : str | None = None
    description : str | None = None

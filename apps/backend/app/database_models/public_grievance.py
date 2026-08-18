from app.database import Base
from sqlalchemy import Column, String, Integer


class Grievance(Base):
    __tablename__ = "Grievances"
         
    id = Column(Integer, primary_key=True, autoincrement=True, index=True )
    full_name = Column(String(50))
    email = Column(String(100))
    mobile_number = Column(String(20))
    complaint_category = Column(String(100))
    municipal_ward = Column(String)
    incident_address = Column(String(100))
    description = Column(String(1000))

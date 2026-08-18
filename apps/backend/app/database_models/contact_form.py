from app.database import Base
from sqlalchemy import Column, String, Integer



class Contact(Base):
    __tablename__ = "Contact"
         
    id = Column(Integer, primary_key=True, autoincrement=True, index=True )
    name = Column(String(50))
    email = Column(String(100))
    phone = Column(String(20))
    subject = Column(String(100))
    message = Column(String(1000))
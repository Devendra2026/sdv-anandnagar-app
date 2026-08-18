
from sqlalchemy import Integer, String, Column
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key = True, autoincrement = True)
    name = Column(String(100))
    email = Column(String(100), unique= True)
    role = Column(String(50), default = "user")
    clerk_id = Column(String(500), unique= True)
    created_at = Column(String(100), default = "now()")
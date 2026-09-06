from database import Base
from sqlalchemy import Column, Integer, String,Float, Boolean,Date, ForeignKey
class Transactions(Base):
    __tablename__= 'transactions'
    id=Column(Integer, primary_key=True)
    title=Column(String) 
    amount=Column(Float)
    type=Column(String)
    category=Column(String)
    date = Column(Date)
    owner_id = Column(Integer, ForeignKey("users.id"))

class Users(Base):
    __tablename__='users'
    id=Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    username=Column(String, unique=True, nullable=False)
    firstname=Column(String)
    lastname=Column(String)
    
    hashed_password = Column(String, nullable=False)
    is_active=Column(Boolean, default=True)
    
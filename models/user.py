from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from config.db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True)
    password = Column(String(100))
    account_number = Column(String, unique=True, default=0)
    is_admin = Column(Boolean, default=False)
    

class Books(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, unique=True)
    title = Column(String)
    author = Column(String)
    publisher = Column(String)
    genre = Column(String)
    description = Column(String)
    available = Column(Boolean, default=True)

class Borrowing(Base):
    __tablename__ = 'borrowing'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    book_id = Column(Integer)
    borrow_date = Column(String)
    return_date = Column(String)
    status = Column(String)
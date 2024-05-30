
from pydantic import BaseModel
from typing import List

# Schemas
class BookSchema(BaseModel):
    title: str
    author: str
    publisher: str
    genre: str
    description:str
    available: bool

class UserSchema(BaseModel):
    account_number: str
    password: str
    role: bool

class BorrowingSchema(BaseModel):
    user_id: int
    account_number:int
    book_id: int
    borrow_date: str
    return_date: str
    status: str

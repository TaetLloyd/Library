from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials,OAuth2PasswordBearer
from config.db import SessionLocal
from models.user import User, Books, Borrowing
from schemas.user import BorrowingSchema,UserSchema, BookSchema
from passlib.context import CryptContext
from sqlalchemy.orm import Session

app = FastAPI()

security = HTTPBasic()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password:str):
    return pwd_context.hash(password)


# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

next_account_number = 1000


# Generate a new 4-digit account number with auto-increment
def generate_account_number():
    global next_account_number
    account_number = next_account_number
    next_account_number += 1
    return account_number

# Register a new user
@app.post("/register")
def register_user(username: str, password: str, is_admin:bool,db:Session= Depends(get_db)):
    account_number = generate_account_number()
    hashed_password = pwd_context.hash(password)
    account = User(username=username, password=hashed_password, account_number=account_number, is_admin=is_admin)
    db.add(account)
    db.commit()
    db.refresh(account)
    return {"Your account_number: ": account_number}


# User authentication dependency
def authenticate_user(credentials: HTTPBasicCredentials = Depends(security), db = Depends(get_db)):
    account = db.query(User).filter(User.username == credentials.username, User.password==credentials.password).first()
    if not account or account.password != credentials.password:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return True

# Admin Add Books
@app.post("/Admin Add Book/",tags=["Admin Use Only"])
def Add_book(book: BookSchema,log:UserSchema,db = Depends(get_db)):
    account = db.query(User).filter(User.account_number == log.account_number).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid username or password",)
    
    if not verify(log.password, account.password):
         raise HTTPException(
             status_code=status.HTTP_404_NOT_FOUND,
             detail="Invalid Password",
         )
    if account.is_admin != True:
        return {"message": "User can not access users"}
    
    new_book=Books(title=book.title, author=book.author, publisher=book.publisher, genre=book.genre, description=book.description, available=book.available)
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return {"message": "Book added successful."}

# Deposit into account
@app.post("/return")
def return_book(transaction: BorrowingSchema,book_id: int, user_id:int,db = Depends(get_db)):
    account = db.query(User).filter(User.account_number == transaction.account_number).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid username or password",)

    borrowing = db.query(Borrowing).filter(Books.id == book_id, Borrowing.user_id == user_id).first()
    if borrowing:
        borrowing.status = "returned"
        db.commit()
        book = db.query(Books).filter(Books.id == book_id).first()
        book.available = True
        db.commit()
        return {"message": "Book returned successfully"}
    else:
        return {"message": "Book not found or not borrowed by user"}

# Withdraw from account
@app.post("/borrow")
def borrow_book(transaction: BorrowingSchema,book_id: int, status:str,db = Depends(get_db)):
    account = db.query(User).filter(User.account_number == transaction.account_number).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    book = db.query(Books).filter(Books.id == book_id).first()
    if status == "available":
        borrowing = Borrowing(user_id=transaction.user_id, book_id=transaction.book_id, borrow_date=transaction.borrow_date, return_date=transaction.return_date, status=transaction.status)
        db.add(borrowing)
        db.commit()
        return {"message": "Book borrowed successfully"}
    else:
        return {"message": "Book is not available"}

# Check account balance
@app.post("/View Books")
def View_books(log:UserSchema,db = Depends(get_db)):
    account = db.query(User).filter(User.account_number == log.account_number).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid username or password",)
    
    if not verify(log.password, account.password):
         raise HTTPException(
             status_code=status.HTTP_404_NOT_FOUND,
             detail="Invalid Password",
         )
    books = db.query(Books).all()
    return books

# Change account password
@app.put("/admin/View users/",tags=["Admin Use Only"])
def view_users(user: UserSchema, db = Depends(get_db)):
    account = db.query(User).filter(User.account_number == user.account_number).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    if not verify(user.password, account.password):
         raise HTTPException(
             status_code=status.HTTP_404_NOT_FOUND,
             detail="Invalid Password",)
    
    if account.is_admin != True:
        return {"message": "User can not access users"}

    
    users = db.query(User).all()
    return users

# Admin view - get all users and todos
@app.post("/admin/books/", tags=["Admin Use Only"])
def View_books(borrow:BorrowingSchema,request:UserSchema, db = Depends(get_db)):
    account = db.query(User).filter(User.account_number == request.account_number).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    if not verify(request.password, account.password):
         raise HTTPException(
             status_code=status.HTTP_404_NOT_FOUND,
             detail="Invalid Password",)

    if account.is_admin != True:
        return {"message": "User can not access users"}
    
    users = db.query(User).all()
    return users


# Start the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

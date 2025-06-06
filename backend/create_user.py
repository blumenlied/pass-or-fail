from app.database import SessionLocal
from app.crud.users import create_user

email = input("Enter email: ")
password = input("Enter password: ")

db = SessionLocal()
create_user(db, email, password, role="faculty")
db.close()


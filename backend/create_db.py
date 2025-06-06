# create_db.py
from app.database import Base, engine
from app.models import Student

Base.metadata.create_all(bind=engine)


# create_tables.py
from app.database import Base, engine
import app.models

# Create tables based on models
Base.metadata.create_all(bind=engine)


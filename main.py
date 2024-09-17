from fastapi import FastAPI, UploadFile, File, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from db.models import Base
from db.session import engine
import os

# Directory where CSV files will be saved
UPLOAD_DIR = "historical_data"

# Ensure the upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

def create_tables(): 
    """Create all tables in the database."""
    Base.metadata.create_all(bind=engine)

def start_application():
    """Initialize the FastAPI application."""
    app = FastAPI()
    create_tables()

    @app.post("/upload/")
    async def upload_csv(table: str, file: UploadFile = File(...)):
        """Handle CSV file upload and save to the server."""
        # Check if the table name is valid
        if table not in ["departments", "jobs", "hired_employees"]:
            raise HTTPException(status_code=400, detail="Table not found")

        # Save the uploaded file to the specified directory
        file_location = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_location, "wb") as f:
            f.write(await file.read())

        return {"status": "success", "filename": file.filename}

    return app 

app = start_application()



from fastapi import FastAPI, UploadFile, File, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey,inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.sqltypes import Integer, String, DateTime
from db.models import Base, Department, Job, Employee  # Import models
from db.session import engine,SessionLocal
import pandas as pd
import os

# Directory where CSV files will be saved
UPLOAD_DIR = "historical_data"

# Ensure the upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

def create_tables(): 
    """Create all tables in the database."""
    Base.metadata.create_all(bind=engine)

def read_csv(file_path: str):
    """Read a CSV file without headers into a DataFrame."""
    return pd.read_csv(file_path, header=None)  # No headers in the CSV

def extract_column_types(model):
    """Extract expected column types from an SQLAlchemy model."""
    column_types = []
    for column in model.__table__.columns:
        if isinstance(column.type, Integer):
            column_types.append('int64')  # Pandas integer type
        elif isinstance(column.type, String):
            column_types.append('object')  # Pandas object type for strings
        elif isinstance(column.type, DateTime):
            column_types.append('object')  # Pandas datetime type (treat as object for simplicity)
        else:
            column_types.append(str(column.type))  # Handle other types as strings
    return column_types

def validate_data_types(data, expected_types):
    """Validate the data types of CSV columns against expected SQLAlchemy types."""
    if len(data.columns) != len(expected_types):
        raise HTTPException(status_code=400, detail="Column count mismatch between CSV and database table.")
    
    # Validate each column's data type in order
    for i, expected_type in enumerate(expected_types):
        actual_type = data.iloc[:, i].dtype  # Get the data type of the i-th column
        if str(actual_type) != expected_type:
            raise HTTPException(status_code=400, detail=f"Column {i+1} has incorrect type. Expected {expected_type}, got {actual_type}.")

def insert_data(session, table_class, data, column_mapping):
    """Insert data into a specified table using column mapping."""
    records = data.to_dict(orient='records')
    
    for record in records:
        mapped_record = {column_mapping[i]: value for i, value in record.items()}  # Map each column to the correct field name
        obj = table_class(**mapped_record)  # Create a new model instance
        session.add(obj)
    
    session.commit()

def start_application():
    """Initialize the FastAPI application."""
    app = FastAPI()
    create_tables()

    @app.post("/upload/")
    async def upload_csv(table: str, file: UploadFile = File(...)):
        """Handle CSV file upload and validate data types."""
        # Map table names to SQLAlchemy models and their column mappings
        table_classes = {
            "departments": (Department, ["id", "department"]),  # Mapping for departments table
            "jobs": (Job, ["id", "job"]),                      # Mapping for jobs table
            "hired_employees": (Employee, ["id", "name", "datetime", "department_id", "job_id"])  # Mapping for hired_employees table
        }

        # Check if the table name is valid
        if table not in table_classes:
            raise HTTPException(status_code=400, detail="Table not found")

        # Get the table class and column mapping
        table_class, column_mapping = table_classes[table]

        # Save the uploaded file
        file_location = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_location, "wb") as f:
            f.write(await file.read())

        # Read the CSV without headers
        data = read_csv(file_location)

        # Extract the expected column types from the SQLAlchemy model
        expected_types = extract_column_types(table_class)

        # Validate the CSV data types (no need to check column names)
        validate_data_types(data, expected_types)

        # Insert data into the database
        with SessionLocal() as session:
            insert_data(session, table_class, data, column_mapping)

        return {"status": "success", "filename": file.filename}

    return app 

app = start_application()

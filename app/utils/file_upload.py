import os
import uuid
from typing import Optional
from fastapi import UploadFile
from pathlib import Path

UPLOAD_DIR = Path("uploads") 

async def save_upload_file(upload_file: UploadFile, subdirectory: Optional[str] = None) -> str:
    try:
        # Ensure the upload directory exists
        full_upload_path = UPLOAD_DIR
        if subdirectory:
            full_upload_path = UPLOAD_DIR / subdirectory
        full_upload_path.mkdir(parents=True, exist_ok=True)

        # Generate a unique filename using UUID and preserve the original extension
        file_extension = Path(upload_file.filename).suffix
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = full_upload_path / unique_filename

        # Write the file asynchronously
        contents = await upload_file.read()
        with open(file_path, "wb") as f:
            f.write(contents)

        return str(file_path)
    except Exception as e:
        # Log the exception for debugging
        print(f"Error saving file: {e}")
        raise 
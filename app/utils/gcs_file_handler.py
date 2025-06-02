import uuid
from typing import Optional
from fastapi import UploadFile, HTTPException, status
from google.cloud import storage
import os
import re

# IMPORTANT:
# For local development, ensure your GOOGLE_APPLICATION_CREDENTIALS environment variable
# points to the path of your service account key file.
# Example: export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/key.json"
# For Railway, you will set this as an environment variable in your project settings,
# or directly set the JSON content of the key.

# --- Configuration ---
# Replace with your actual GCS bucket name
GCS_BUCKET_NAME = os.environ.get("GCS_BUCKET_NAME", "your-default-gcs-bucket-name")
# Replace with your Google Cloud Project ID if not set via GOOGLE_APPLICATION_CREDENTIALS
GOOGLE_CLOUD_PROJECT = os.environ.get("GOOGLE_CLOUD_PROJECT", None)
# --- End Configuration ---

# Initialize GCS client
try:
    if GOOGLE_CLOUD_PROJECT:
        gcs_client = storage.Client(project=GOOGLE_CLOUD_PROJECT)
    else:
        gcs_client = storage.Client()
    # Test if the bucket exists and is accessible
    # This will raise an exception if the bucket is not found or credentials are bad
    _ = gcs_client.get_bucket(GCS_BUCKET_NAME)
    print(f"Successfully connected to GCS bucket: {GCS_BUCKET_NAME}")
except Exception as e:
    print(f"ERROR: Failed to initialize Google Cloud Storage client or access bucket '{GCS_BUCKET_NAME}': {e}")
    # In a real application, you might want to exit or log more severely.
    # For now, we'll let the functions below handle specific upload/delete failures.


async def upload_file_to_gcs(upload_file: UploadFile, subdirectory: Optional[str] = None) -> str:
    """
    Saves an uploaded file to Google Cloud Storage.
    Returns the public URL of the saved file.
    """
    if not GCS_BUCKET_NAME or GCS_BUCKET_NAME == "your-default-gcs-bucket-name":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="GCS_BUCKET_NAME is not configured."
        )

    try:
        # Generate a unique filename using UUID and preserve the original extension
        file_extension = os.path.splitext(upload_file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"

        # Construct the full path in the bucket
        if subdirectory:
            destination_blob_name = f"{subdirectory}/{unique_filename}"
        else:
            destination_blob_name = unique_filename

        bucket = gcs_client.bucket(GCS_BUCKET_NAME)
        blob = bucket.blob(destination_blob_name)

        # Read the file content asynchronously
        contents = await upload_file.read()
        blob.upload_from_string(contents, content_type=upload_file.content_type)

        # Make the blob publicly accessible (if needed)
        # Be careful with public access; consider signed URLs for more security
        blob.make_public()

        # Return the public URL
        return blob.public_url

    except Exception as e:
        print(f"Error uploading file to GCS: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload image: {e}"
        )

async def delete_file_from_gcs(file_url: str):
    """
    Deletes a file from Google Cloud Storage given its public URL.
    """
    if not GCS_BUCKET_NAME or GCS_BUCKET_NAME == "your-default-gcs-bucket-name":
        print("GCS_BUCKET_NAME is not configured for deletion. Skipping delete.")
        return

    # Check if the URL is a GCS public URL to avoid trying to delete non-GCS files
    if not re.match(r"https://storage.googleapis.com/", file_url):
        print(f"URL is not a GCS public URL, skipping deletion: {file_url}")
        return

    try:
        # Extract bucket name and blob name from the URL
        # GCS public URL format: https://storage.googleapis.com/<bucket-name>/<blob-name>
        parts = file_url.split('/')
        if len(parts) < 4 or parts[2] != "storage.googleapis.com":
            print(f"Invalid GCS URL format for deletion: {file_url}")
            return

        bucket_name_from_url = parts[3]
        blob_name = "/".join(parts[4:])

        if bucket_name_from_url != GCS_BUCKET_NAME:
            print(f"Bucket name mismatch during deletion: {bucket_name_from_url} vs {GCS_BUCKET_NAME}. Skipping.")
            return

        bucket = gcs_client.bucket(GCS_BUCKET_NAME)
        blob = bucket.blob(blob_name)

        if blob.exists():
            blob.delete()
            print(f"Successfully deleted GCS file: {blob_name}")
        else:
            print(f"GCS file not found for deletion, might already be deleted: {blob_name}")

    except Exception as e:
        print(f"Error deleting file from GCS '{file_url}': {e}")
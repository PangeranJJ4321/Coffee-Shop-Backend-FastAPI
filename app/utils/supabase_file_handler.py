import uuid
from typing import Optional
from fastapi import UploadFile, HTTPException, status
from supabase import create_client, Client
import os
import re

# Import your settings object
from app.core.config import settings

supabase_client: Client = None

def initialize_supabase_client():
    """Initializes the Supabase client. Called once when the module is loaded."""
    global supabase_client
    # Use settings values
    if not settings.SUPABASE_URL:
        print("ERROR: SUPABASE_URL is not configured in settings. Supabase client will not be initialized.")
        return
    if not settings.SUPABASE_SERVICE_KEY:
        print("ERROR: SUPABASE_SERVICE_KEY is not configured in settings. Supabase client will not be initialized.")
        return

    try:
        supabase_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
        print("Successfully initialized Supabase client.")
    except Exception as e:
        print(f"ERROR: Failed to initialize Supabase client: {e}. Please check your Supabase URL and Service Key.")

# Initialize client on module load
initialize_supabase_client()


async def upload_file_to_supabase(upload_file: UploadFile, subdirectory: Optional[str] = None) -> str:
    """
    Saves an uploaded file to Supabase Storage.
    Returns the public URL of the saved file.
    """
    if not supabase_client:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Supabase client not initialized. Check application settings for SUPABASE_URL and SUPABASE_SERVICE_KEY."
        )

    try:
        # Generate a unique filename using UUID and preserve the original extension
        file_extension = os.path.splitext(upload_file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"

        # Construct the full path in the bucket
        if subdirectory:
            destination_path = f"{subdirectory}/{unique_filename}"
        else:
            destination_path = unique_filename

        contents = await upload_file.read()

        response_data = supabase_client.storage.from_(settings.SUPABASE_BUCKET_NAME).upload( # Use settings.SUPABASE_BUCKET_NAME
            file=contents,
            path=destination_path,
            file_options={"content-type": upload_file.content_type, "upsert": "true"}
        )

        public_url = supabase_client.storage.from_(settings.SUPABASE_BUCKET_NAME).get_public_url(destination_path) # Use settings.SUPABASE_BUCKET_NAME
        
        if not public_url:
            raise ValueError(f"Supabase returned an invalid public URL for path: {destination_path}")

        print(f"Successfully uploaded to Supabase: {public_url}")
        return public_url

    except Exception as e:
        print(f"Error uploading file to Supabase: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload image: {e}"
        )

async def delete_file_from_supabase(file_url: str):
    """
    Deletes a file from Supabase Storage given its public URL.
    """
    if not supabase_client:
        print("Supabase client not initialized for deletion. Skipping delete.")
        return

    match = re.search(r'/public/([^/]+)/(.+)$', file_url)
    if not match:
        print(f"URL is not a valid Supabase public URL or malformed, skipping deletion: {file_url}")
        return

    bucket_name_in_url = match.group(1)
    path_in_bucket = match.group(2)

    if bucket_name_in_url != settings.SUPABASE_BUCKET_NAME: # Use settings.SUPABASE_BUCKET_NAME
        print(f"Bucket name in URL '{bucket_name_in_url}' does not match configured bucket '{settings.SUPABASE_BUCKET_NAME}'. Skipping delete.")
        return

    try:
        path_to_delete = '/'.join(path_in_bucket.split('/')[1:]) # Extract path relative to bucket, assuming bucket name is first segment

        response = supabase_client.storage.from_(settings.SUPABASE_BUCKET_NAME).remove([path_in_bucket]) # Use settings.SUPABASE_BUCKET_NAME

        if isinstance(response, list) and all(isinstance(item, dict) and item.get('status') == '200' for item in response):
            print(f"Successfully deleted Supabase file: {path_in_bucket}")
        else:
            print(f"Supabase remove response for {path_in_bucket}: {response}")
            if isinstance(response, dict) and 'error' in response:
                print(f"Error detail from Supabase: {response['error']}")
            else:
                print("Unexpected response from Supabase remove operation.")

    except Exception as e:
        print(f"Error deleting file from Supabase '{file_url}': {e}")
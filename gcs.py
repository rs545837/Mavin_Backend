import os

from google.cloud import storage


def upload_pdf_to_gcs(bucket_name, source_file_path, destination_blob_name):
    """Uploads a PDF file to Google Cloud Storage and returns the public URL.

  Args:
      bucket_name: The name of the Google Cloud Storage bucket.
      source_file_path: The local path to the PDF file.
      destination_blob_name: The desired name for the PDF file in GCS.

  Returns:
      The public URL of the uploaded PDF file, or None on error.
  """

    # Set up authentication (replace with your credentials)
    os.environ[
        "GOOGLE_APPLICATION_CREDENTIALS"] = "dinewiseai-84e9951a9657.json"

    # Create a storage client
    storage_client = storage.Client()

    # Get the bucket
    bucket = storage_client.bucket(bucket_name)

    # Upload the PDF file
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_path)

    # Make the file publicly readable if desired
    acl = blob.acl
    acl.public = True  # Set to True for public access
    blob.acl.save()

    # Get the public URL
    public_url = blob.public_url

    if public_url:
        print(f"PDF uploaded successfully! Public URL: {public_url}")
        return public_url
    else:
        print("Failed to get public URL.")
        return None


def upload_audio_to_gcs(bucket_name, source_file_path, destination_blob_name):
    """Uploads an audio file to Google Cloud Storage and returns the public URL.

    Args:
        bucket_name: The name of the Google Cloud Storage bucket.
        source_file_path: The local path to the audio file.
        destination_blob_name: The desired name for the audio file in GCS.

    Returns:
        The public URL of the uploaded audio file, or None on error.
    """

    # Set up authentication (replace with your credentials)
    os.environ[
        "GOOGLE_APPLICATION_CREDENTIALS"] = "dinewiseai-84e9951a9657.json"

    # Create a storage client
    storage_client = storage.Client()

    # Get the bucket
    bucket = storage_client.bucket(bucket_name)

    # Upload the audio file
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_path)

    # Make the file publicly readable if desired
    acl = blob.acl
    acl.public = True  # Set to True for public access
    blob.acl.save()

    # Get the public URL
    public_url = blob.public_url

    if public_url:
        print(f"Audio uploaded successfully! Public URL: {public_url}")
        return public_url
    else:
        print("Failed to get public URL.")
        return None


if __name__ == "__main__":

    # Example usage (replace with your details)
    bucket_name = "this-is-goat"
    source_file_path = ""
    destination_blob_name = "public/my_pdf.pdf"  # Optional, customize the in-bucket name

    public_url = upload_pdf_to_gcs(bucket_name, source_file_path,
                                   destination_blob_name)

    if public_url:
        print(f"You can now access the PDF at: {public_url}")

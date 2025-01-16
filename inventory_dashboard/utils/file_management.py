# File: utils/file_management.py

import os

def save_uploaded_file(uploaded_file, upload_dir):
    """Save the uploaded file to the specified directory."""
    os.makedirs(upload_dir, exist_ok=True)  # Ensure the directory exists
    file_path = os.path.join(upload_dir, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())  # Save the file content
    return file_path

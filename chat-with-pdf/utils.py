import os 
import time 
import json 
import streamlit as st 
from typing import Any 

# Utility function to save the docs into a temporary directory
def temp_save_uploaded_file(uploadedfile):
    if not os.path.isdir(".tempdir"):
        os.makedirs(".tempdir")
    
    save_path = os.path.join(".tempdir", uploadedfile.name)
    try:
        with open(save_path, "wb") as f:
            f.write(uploadedfile.getbuffer())
        return  save_path
    except Exception:
        st.sidebar.toast("Failed to upload the file. Try again", icon="❌")
        return None  


# Function to upload multiple files to prem repository
def upload_multiple_files_to_pre_repo(
    client: Any,
    uploadedfiles: list, 
    prem_repo_id: int
):
    len_uploaded_files = len(uploadedfiles)
    progress_text = "Uploading files to Prem repository"
    my_bar = st.progress(0, text=progress_text)

    for i in range(len_uploaded_files):    
        file_path = temp_save_uploaded_file(uploadedfile=uploadedfiles[i])
        time.sleep(0.1)
        try:
            _ = client.repository.document.create(
                repository_id=prem_repo_id,
                file=file_path
            )
            my_bar.progress((i + 1) / len_uploaded_files, text=progress_text)  # Update progress bar within the try block
        except Exception as e:
            print(e)
            st.toast(f"Error with file: {uploadedfiles[i].name}", icon="❌")

    my_bar.empty()
    st.toast(body=f"Uploaded {len_uploaded_files} files", icon="🚀")


# Function to watch retrieved chunks 
def see_repos(retrieved_docs):
    docs = [doc.to_dict() for doc in retrieved_docs]
    with st.expander("See retrieved docs"):
        st.json(json.dumps(docs, indent=4)) 
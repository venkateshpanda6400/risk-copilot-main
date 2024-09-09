import streamlit as st
import os
from riskCopilot.components.rag.embeddings import get_table_names

# Create the directory if it doesn't exist
os.makedirs("data/raw", exist_ok=True)

st.title("Document Uploader")


# Function to get updated embeddings
def get_updated_embeddings():
    return get_table_names(
        os.path.join(os.environ["connection_string"], os.environ["db_name"])
    )


# Initialize session state for embeddings if not exists
if "embeddings" not in st.session_state:
    st.session_state.embeddings = [
        i.replace("data_", "") for i in get_updated_embeddings()
    ]

uploaded_files = st.file_uploader("Choose files to upload", accept_multiple_files=True)

if uploaded_files:
    for file in uploaded_files:
        # Save the file to the data/raw directory
        file_path = os.path.join("data/raw", file.name)
        with open(file_path, "wb") as f:
            f.write(file.getbuffer())
        st.success(f"File '{file.name}' has been successfully saved to 'data/raw'")

    # Update embeddings after each file upload
    st.session_state.embeddings = [
        i.replace("data_", "") for i in get_updated_embeddings()
    ]

# Display available embeddings
st.header("Available Embeddings")
embeddings_text = "\n".join(
    [f"{i+1}. {embedding}" for i, embedding in enumerate(st.session_state.embeddings)]
)
st.text_area("", value=embeddings_text, height=300, disabled=True)

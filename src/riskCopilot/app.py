import os
from dotenv import load_dotenv

load_dotenv()

import warnings

warnings.filterwarnings("ignore")

# import logging

# # Configure logging
# logging.basicConfig(level=logging.ERROR)  # Set logging level to ERROR or higher

# # Optionally, you can suppress specific loggers or messages
# logging.getLogger("httpx").setLevel(
#     logging.ERROR
# )  # Suppress logs from the httpx logger

import streamlit as st
from riskCopilot.components.rag.bot import bot
from riskCopilot.components.rag.embeddings import get_table_names

import base64



# @st.cache_data
# def get_img_as_base64(file):
#     with open(file, "rb") as f:
#         data = f.read()
#     return base64.b64encode(data).decode()


# img = get_img_as_base64("randstaddigital.png")

# page_bg_img = f"""
# <style>
# [data-testid="stAppViewContainer"] > .main {{
# background-image: url("data:image/png;base64,{img}");
# background-size: cover;
# }}

# [data-testid="stHeader"] {{
# background: rgba(0,0,0,0);
# }}

# [data-testid="stToolbar"] {{
# right: 2rem;
# }}

# </style>
# """


# A Streamlit interface to handle and save our chats
def handle_userinput():

    clear = False

    # Add clear chat button
    if st.button("Clear Chat history"):
        clear = True
        st.session_state.messages = []
        st.session_state.agent.memory.reset()
        st.session_state.messages = [
            {"role": "assistant", "content": "How can I help you?"}
        ]

    # Initialize our Streamlit chat interface
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "How can I help you?"}
        ]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Clear the cache memory
    if clear:
        st.session_state.agent.memory.reset()
        clear = False

    if prompt := st.chat_input():

        with st.chat_message("user"):
            st.markdown(prompt)

        # Add user question to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Generate response
        with st.spinner("Generating Answer..."):
            st.session_state.msg = st.session_state.agent.chat(prompt)

        with st.chat_message("assistant"):
            st.markdown(st.session_state.msg)

        # Add response to session state
        st.session_state.messages.append(
            {"role": "assistant", "content": st.session_state.msg}
        )


# Function to get updated embeddings
def get_updated_embeddings():
    return get_table_names(
        os.path.join(os.environ["connection_string"], os.environ["db_name"])
    )


def available_documents():
    st.sidebar.header("Available Documents")
    # Update embeddings after each file upload
    st.session_state.embeddings = [
        i.replace("data_", "") for i in get_updated_embeddings()
    ]
    embeddings_text = "\n".join(
        [
            f"{i+1}. {embedding}"
            for i, embedding in enumerate(st.session_state.embeddings)
        ]
    )
    st.sidebar.text_area("", value=embeddings_text, height=1000, disabled=True)


def main():
    st.set_page_config(page_title="RANDSTAD DIGITAL", page_icon=":books:")

    # st.markdown( unsafe_allow_html=True) # page_bg_img,

    if "agent" not in st.session_state:
        st.session_state.agent = bot(True)

        # Update embeddings after each file upload

    st.title("💬 Randstad Risk Co-Pilot")

    available_documents()
    handle_userinput()


if __name__ == "__main__":
    main()

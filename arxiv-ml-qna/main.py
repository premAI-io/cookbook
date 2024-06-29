import dspy 
from dspy import PremAI
from qdrant_client import QdrantClient

import streamlit as st
from utils import RAG, get_retriever, get_all_collections, chat

# ---- Configurations ---- #
premai_api_key = st.secrets.premai_api_key
premai_project_id = st.secrets.premai_project_id
embedding_model_name = "mistral-embed"
qdrant_server_url = "http://localhost:6333"

# ---- Define the Prem LLM and QdrantRM ---- #
qdrant_client = QdrantClient(qdrant_server_url)

def setup_retriever_and_llm(collection_name: str):
    llm = PremAI(
        project_id=premai_project_id, 
        **{"temperature":0.1, "max_tokens":1024}
    )
    abstract_retriever = get_retriever(
        premai_api_key=premai_api_key,
        qdrant_collection_name=collection_name,
        qdrant_client=qdrant_client,
        premai_project_id=premai_project_id,
        document_field="abstract",
        embedding_model_name=embedding_model_name
    )

    title_retriever = get_retriever(
        premai_api_key=premai_api_key,
        qdrant_collection_name=collection_name,
        qdrant_client=qdrant_client,
        premai_project_id=premai_project_id,
        document_field="title",
        embedding_model_name=embedding_model_name
    )

    dspy.settings.configure(lm=llm, rm=abstract_retriever)
    pipeline = RAG(title_retriever=title_retriever)
    return pipeline 

# ---- Streamlit Stuffs ---- #
st.set_page_config(page_title="arxiv paper search", page_icon="🧩")
st.markdown(
    """
    <h2 style='text-align: center;'>ArXiv Paper search & QnA</h2>
    """,
    unsafe_allow_html=True,
)

# ---- Set the sidebar to connect the Tables of the database ---- #
with st.sidebar:
    st.image("logo.png", use_column_width=True)
    st.markdown(
        """
        <h2 style='text-align: center;'>Prem AI</h2>
        """,
        unsafe_allow_html=True,
    )
    with st.container(border=True):
        st.markdown(
            """
            [Prem App](https://app.premai.io)  | [Join our Discord](https://discord.gg/TZ83cefwNV) | [Documentation]()
            """
        )
    
    all_collections = get_all_collections(client=qdrant_client)
    selected_collection = st.selectbox(label="Select your collection", options=all_collections)
    if selected_collection is None:
        st.error("No collections found")
    else:
        st.success(
            f"You will be chatting with Table: {selected_collection}" 
        )

# ---- Main UI ---- #

if selected_collection is None:
    st.error(
        "Please set up Qdrant Engine properly. No Collections found."
    )
else:
    pipeline = setup_retriever_and_llm(collection_name=selected_collection)
    chat(pipeline=pipeline)
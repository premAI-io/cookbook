import time
import streamlit as st
from llama_index.core import Settings
from llama_index.llms.premai import PremAI
from llama_index.embeddings.premai import PremAIEmbeddings
from db_utils import get_all_tables_from_db, setup_index

# ---- PremAI configuration ----
premai_api_key = st.secrets.premai_api_key
premai_project_id = st.secrets.premai_project_id
embedding_model_name = "text-embedding-3-large"

# ---- Database configuration ----
username = st.secrets.username
password = st.secrets.password
host = st.secrets.host
port = st.secrets.port
dbname = st.secrets.database

db_config = {
    "username": username,
    "password": password,
    "host": host,
    "port": port,
    "database": dbname,
}

# ---- Define the LLM and Embedding model using Prem ----
llm = PremAI(
    project_id=premai_project_id, premai_api_key=premai_api_key, temperature=0.1
)
embedding_model = PremAIEmbeddings(
    project_id=premai_project_id,
    premai_api_key=premai_api_key,
    model_name=embedding_model_name,
)

Settings.llm = llm
Settings.embed_model = embedding_model

# ---- Streamlit config to set the page header and the main title ----
st.set_page_config(page_title="chat with sql", page_icon="🧩")
st.markdown(
    """
    <h2 style='text-align: center;'>Chat With SQL Tables</h2>
    """,
    unsafe_allow_html=True,
)

# ---- Set the sidebar to connect the Tables of the database ----
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

    all_tables = get_all_tables_from_db(db_config=db_config)
    options = st.selectbox(label="Select your database", options=all_tables)
    if options is None:
        st.error("No table found")
    else:
        use_all_tables = st.checkbox("Use all tables")
        st.success(
            f"You will be chatting with Table: {options}" +
            ("\nIndexing all the tables" if use_all_tables else "")
        )

# ---- Main chat UI code that will return the response and the SQL used to retrieve ----
if options is None:
    st.error("Please set up the SQL DB Engine connection properly. No Tables found.")

else:
    query_engine = setup_index(
        db_config=db_config, table=options, use_all=use_all_tables
    )

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Please write your query"):
        user_content = {"role": "user", "content": prompt}
        st.session_state.messages.append(user_content)
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""

            while not full_response:
                with st.spinner("Thinking ...."):
                    try:
                        response = query_engine.query(prompt)
                        response_str, response_meta = (
                            response.response,
                            response,
                        )
                    except Exception:
                        response_str = "Failed to respond"
                        response_meta = []

                fr = ""
                full_response = str(response_str)
                for i in full_response:
                    time.sleep(0.01)
                    fr += i
                    message_placeholder.write(fr + "▌")
                message_placeholder.write(f"{full_response}")
                with st.expander(label="See what was run inside the model"):
                    st.write(response_meta)

            st.session_state.messages.append(
                {"role": "assistant", "content": full_response}
            )

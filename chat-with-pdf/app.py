import time 
import premai 
import streamlit as st 
import utils 

# Set all the constants here 
premai_api_key = st.secrets.premai_api_key
premai_project_id = 4071
premai_repository_id = 2100
prem_client = premai.Prem(api_key=premai_api_key)

# Set the webpage config 
st.set_page_config(page_title="chat with pdf", page_icon="💬")
st.markdown(
    """
    <h2 style='text-align: center;'>Chat With PDF</h2>
    """,
    unsafe_allow_html=True,
)

# Side bar
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
    with st.container(border=True):
        st.write(
            "Upload pdf files. Once uploading is fininshed, please remove "
            "all the files by crossing out them. Otherwise streamlit loads "
            "the files everytime with each new chat."
        )
        st.warning(
            "Please note: Max size per article is 20 MB"
        )
    uploaded_files = st.file_uploader(
        label="Upload PDF files",
        accept_multiple_files=True,
        type=[".pdf"]
    )

    if uploaded_files:
        utils.upload_multiple_files_to_pre_repo(
            client=prem_client,
            prem_repo_id=premai_repository_id,
            uploadedfiles=uploaded_files
        )

uploaded_files = None 

# Chat with the PDF section

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


    

# We get the input prompt from user

repositories = dict(
    ids=[premai_repository_id], 
    similarity_threshold=0.25, 
    limit=5
)

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
                    response = prem_client.chat.completions.create(
                        project_id=premai_project_id,
                        messages=[user_content],
                        repositories=repositories,
                        stream=False
                    )
                    response_content = response.choices[0].message.content
                    response_doc_chunks = response.document_chunks
                except Exception:
                    response_content = "Failed to respond"
                    response_doc_chunks = []
                
            fr = ""
            full_response = str(response_content)
            
            for i in full_response:
                time.sleep(0.01)
                fr += i
                message_placeholder.write(fr + "▌")
            message_placeholder.write(f"{full_response}")
            utils.see_repos(retrieved_docs=response_doc_chunks)
        
        st.session_state.messages.append(
            {"role": "assistant", "content": full_response}
        )

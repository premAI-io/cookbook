import os 
import json 
import streamlit as st 
from urllib.parse import urlparse
from langchain_community.chat_models.premai import ChatPremAI

from utils import summarize_url

# Some helper functions

def is_valid_url(url: str):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False 

def summarize_component(urls: list[str], client: ChatPremAI):
    passed, failed = [], []
    with st.spinner("Please wait while we summarize the content"):
        for url in urls:
            if not is_valid_url(url):
                failed.append(url)
            else:
                results = summarize_url(url, llm=client)
                if results:
                    passed.append({
                        "url": url,
                        "document": results["input_documents"],
                        "intermediate": results["intermediate_steps"],
                        "summary": results["output_text"]
                    })
                    with st.expander(label=f"URL: {url}"):
                        st.write(results["output_text"])
                else:
                    failed.append(url)
        
        if len(failed) > 0:
            st.json(json.dumps(failed)) 
    return passed, failed 


st.set_page_config(page_title="url summary and qna", page_icon="💬")

# Set all the settings here 
# Please set a valid PROJECT ID when running this code 
premai_api_key = st.secrets.premai_api_key
premai_project_id = 123456789
os.environ["PREMAI_API_KEY"] = premai_api_key
prem_client = ChatPremAI(project_id=premai_project_id)

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
    
st.markdown(
    """
    <h2 style='text-align: center;'>URL Topic Summarizer</h2>

    Dump all your urls in this text area, all comma seperated. Once all dumped, hit submit button, and we will first create the summary for all the urls and also index all of them so that you can ask questions from it.
    """,
    unsafe_allow_html=True,
)

with st.form("Dump all URLs here"):
    input_urls = st.text_area(
        label="urls",
        height=300,
        placeholder="Should be comma seperated valid urls"
    )
    button = st.form_submit_button("Submit")
    if button:
        urls = [url.strip() for url in input_urls.split(",")]
        _, _ = summarize_component(urls=urls, client=prem_client)

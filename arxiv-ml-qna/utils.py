import time 
from typing import Optional
import dspy
from qdrant_client import QdrantClient
from dspy.retrieve.qdrant_rm import QdrantRM
from dsp.modules.sentence_vectorizer import PremAIVectorizer 

import streamlit as st 

def get_retriever(
    qdrant_collection_name: str, 
    qdrant_client: QdrantClient, 
    premai_project_id: str,
    embedding_model_name: str,
    document_field: str,
    premai_api_key: Optional[str]=None,
):
    retriever = QdrantRM(
        qdrant_collection_name=qdrant_collection_name,
        qdrant_client=qdrant_client,
        vectorizer=PremAIVectorizer(
            project_id=premai_project_id,
            model_name=embedding_model_name,
            api_key=premai_api_key
        ),
        document_field=document_field,
        k=3
    )
    return retriever

# ------ DSPy Signature ------ #

class GenerateAnswer(dspy.Signature):
    """Think and Answer questions based on the context provided."""
    context = dspy.InputField(desc="May contain relevant facts about user query")
    question = dspy.InputField(desc="User query")
    answer = dspy.OutputField(desc="Answer in one or two lines")

# ------ DSPy Module ------ #

class RAG(dspy.Module):
    def __init__(self, title_retriever):
        self.generate_answer = dspy.Predict(GenerateAnswer)
        self.retriever = dspy.Retrieve(k=3)
        self.title_retriever = title_retriever
    
    def forward(self, question):
        context = self.retriever(question).passages     
        titles = self.title_retriever(question) 
        prediction = self.generate_answer(
            context=context, question=question
        )        
        return [
            dspy.Prediction(context=context, answer=prediction.answer), 
            [title["long_text"] for title in titles]
        ]

# ------ DSPy Signature ------ #

def get_all_collections(client: QdrantClient):
    return [collection.name for collection in client.get_collections().collections] 

# ------ Streamlit chat utility ------ #

def chat(pipeline):
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
                        response, titles = pipeline(prompt)
                        response_str = response.answer
                        response_contexts = response.context
                        response_meta = [
                            {"title": title, "abstract": abstract}
                            for title, abstract in zip(titles, response_contexts)
                        ]
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
                
                if response_meta is not None and len(response_meta) > 0:
                    for meta in response_meta:
                        title = meta["title"]
                        abstract = meta["abstract"]
                        with st.expander(label=title):
                            st.write(abstract)
                else:
                    st.warning("No contexts found")

            st.session_state.messages.append(
                {"role": "assistant", "content": full_response}
            )
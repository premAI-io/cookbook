from langchain_community.document_loaders import WebBaseLoader
from langchain_community.chat_models.premai import ChatPremAI

from langchain.chains.llm import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_text_splitters import CharacterTextSplitter
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chains import MapReduceDocumentsChain, ReduceDocumentsChain

map_template = """
The following is a set of documents
{docs}
Based on this list of docs, please identify the main themes and extract 
informations from them which are highly valuable. So the main point should
be the theme/topic and subpoints should be the information extracts of the
documents which are very invaluable. 
Helpful Answer:
"""

reduce_template = """
The following is set of summaries:
{docs}
Take this and then make a very good summary with a very human like way so that
people can use this summary to decide whether to use that resource to finally read
or not. Do not give them the decision, give them enough insights or summary
that will help them. Include the following sub headings

1. What is this is about
2. Main key takeaways 
3. Things to note additionally
Helpful Answer:
"""

def summarize_url(url: str, llm: ChatPremAI) -> dict:
    loader = WebBaseLoader(url)
    docs = loader.load()
    
    # Get the prompts from prompt templates
    map_prompt = PromptTemplate.from_template(template=map_template)
    reduce_prompt = PromptTemplate.from_template(template=reduce_template)

    # Make the map and reduce LLM chains
    map_chain = LLMChain(llm=llm, prompt=map_prompt)
    reduce_chain = LLMChain(llm=llm, prompt=reduce_prompt)

    # apply those chains for the documents
    combined_documents_chain = StuffDocumentsChain(
        llm_chain=reduce_chain, document_variable_name="docs"
    )
    
    reduce_documents_chain = ReduceDocumentsChain(
        combine_documents_chain=combined_documents_chain,
        collapse_documents_chain=combined_documents_chain,
        token_max=4000
    )

    map_reduce_chain = MapReduceDocumentsChain(
        llm_chain=map_chain,
        reduce_documents_chain=reduce_documents_chain,
        document_variable_name="docs",
        return_intermediate_steps=True,
    )
    
    text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=1000, chunk_overlap=0
    )

    # Use the document splits
    split_docs = text_splitter.split_documents(docs)
    result = map_reduce_chain.invoke(split_docs)
    return result


def upload_text_to_prem_repo(
    repository_id: int,
    prem_client: ChatPremAI,
    name: str, 
    text: str 
):
    try:
        _ = prem_client.repository.document.create(
            repository_id=repository_id,
            name=f"{name}.txt",
            content=text,
            document_type="text"
        )
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False 
    


# This is just for one document and it's summary
def upload_summarized_doc_and_chunks_to_repo(
    repository_id: int, 
    prem_client: ChatPremAI,
    topic_name: str, 
    input_document: str, 
    intermediate_results: list[str], 
    summary: str
):
    document_failed_to_upload = []

    # first we upload the content
    input_doc_status = upload_text_to_prem_repo(
        repository_id=repository_id,
        prem_client=prem_client,
        name=f"{topic_name}_input_docuents",
        text=input_document
    )
    if not input_doc_status:
        document_failed_to_upload.append({
            "type":"input", 
            "content":input_document
        })

    # Upload the intermediate document results 
    
    for i, result in enumerate(intermediate_results):
        status = upload_text_to_prem_repo(
            repository_id=repository_id,
            prem_client=prem_client,
            text=result,
            name=f"{topic_name}_intermediate_doc_num_{i}"
        ) 
        if not status:
            document_failed_to_upload.append({
                "type": "input",
                "content": result
            })
    

    # Upload the summary of the document too 
    summary_status = upload_text_to_prem_repo(
        repository_id=repository_id,
        prem_client=prem_client,
        text=summary,
        name=f"{topic_name}_summary"
    )
    if not summary_status:
        document_failed_to_upload.append({
            "type":"summary", 
            "content":input_document
        })

    return document_failed_to_upload
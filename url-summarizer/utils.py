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
    
    # Step 1: Load the WebBasedLoader and CharacterTextSplitter to load and split documents 
    loader = WebBaseLoader(url)
    docs = loader.load()
    text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=1000, chunk_overlap=0
    )
    split_docs = text_splitter.split_documents(docs)

    # Step 2: Get the prompts from prompt templates
    map_prompt = PromptTemplate.from_template(template=map_template)
    reduce_prompt = PromptTemplate.from_template(template=reduce_template)

    # Step 3: Make the map and reduce LLM chains
    map_chain = LLMChain(llm=llm, prompt=map_prompt)
    reduce_chain = LLMChain(llm=llm, prompt=reduce_prompt)

    # Step 4: Define `combined_document_chain` which combines all the summarized chunks 
    combined_documents_chain = StuffDocumentsChain(
        llm_chain=reduce_chain, document_variable_name="docs"
    )
    
    # Step 5: Define `reduce_document_chain`
    reduce_documents_chain = ReduceDocumentsChain(
        combine_documents_chain=combined_documents_chain,
        collapse_documents_chain=combined_documents_chain,
        token_max=4000
    )

    # Step 6: Define the final map-reduce-chain which combines all of the above and run in one single pipeline
    map_reduce_chain = MapReduceDocumentsChain(
        llm_chain=map_chain,
        reduce_documents_chain=reduce_documents_chain,
        document_variable_name="docs",
        return_intermediate_steps=True,
    )

    # Step 7: Run the chain and get the results back
    result = map_reduce_chain.invoke(split_docs)
    return result

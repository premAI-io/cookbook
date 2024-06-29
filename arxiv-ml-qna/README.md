## ArXiv paper search and QnA using PremAI, DSPy and Qdrant

In this recipe, we are going to implement a custom [Retrieval Augmented Generation (RAG)](https://blogs.nvidia.com/blog/what-is-retrieval-augmented-generation/) pipeline using PremAI, [Qdrant](https://qdrant.tech/) and [DSPy](https://dspy-docs.vercel.app/).

<img width="1119" alt="url-summarizer" src="../assets/arxiv paper search.jpeg">

### Setting up the project 

It's quite simple. First clone the repository:

```bash
git clone https://github.com/premAI-io/cookbook.git
cd cookbook/arxiv-ml-qna
```

After that, create a virtual environment and install the requirements.

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

 To install Qdrant engine, you need to have [docker](https://www.docker.com/) installed. You can build and run the Qdrant's official docker image using the following command:

```bash
docker run -p 6333:6333 -p 6334:6334 \
    -v $(pwd)/qdrant_storage:/qdrant/storage:z \
    qdrant/qdrant
```

### Running the app

Before running the app, please do not forget to add the secrets `premai_api_key ` to secrets.toml.template and remove `.template` from it. Please add the valid `PROJECT_ID` from the Prem App before running the app. To run the app, type the following command:

```bash
streamlit run main.py
```
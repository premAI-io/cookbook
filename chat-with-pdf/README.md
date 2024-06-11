## Simple chat with pdf using Prem AI SDK 

In this first cookbook recipe, we are going to show how we can create 
a very simple chat with pdf application using Prem AI SDK and Streamlit. 

The best part! It's just 100 lines of code, and you don't even require the knowledge of RAG or Retrieval Augmented Generation. The step by step tutorial is available [here](https://docs.premai.io)

<img width="1119" alt="url-summarizer" src="../assets/chat with pdf.jpeg">

### Setting up the project 

It's quite simple. First clone the repository:

```bash
git clone https://github.com/premAI-io/cookbook.git
cd cookbook/chat-with-pdf
```

After that, create a virtual environment and install the requirements.

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Running the app

Before running the app, please do not forget to add the secrets `premai_api_key ` to secrets.toml.template and remove `.template` from it. Please add the valid `PROJECT_ID` and `REPOSITORY_ID` from the Prem App before running the app. To run the app, type the following command:

```bash
streamlit run app.py
```

Congratulations on running your first app with Prem AI. Please check out our rest of our tutorials to explore more such use cases. 

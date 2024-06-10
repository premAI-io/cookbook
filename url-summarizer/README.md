## URL Summarizer with Langchain Prem AI 

In this recipe, we are going to show you how you can use [LangChain ChatPremAI](https://python.langchain.com/v0.2/docs/integrations/chat/premai/) (prem SDK integration into langchain) to summarize multiple URLs.We also used streamlit to put a nice interface and visualization. 

![Screenshot 2024-06-10 at 5 16 50 PM](https://github.com/premAI-io/cookbook/assets/58508471/dbdaec26-ef69-408c-aab4-965424c8f0b4)

### Setting up the project

It's quite simple. First clone the repository:

```
git clone https://github.com/premAI-io/cookbook.git
cd cookbook/url-summarizer
```

After that, create a virtual environment and install the requirements.

```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Running the app

Before running the app, please do not forget to add the secrets `premai_api_key`  to secrets.toml.template and remove .template from it. To run the app, type the following command:

```
streamlit run app.py
```

Congratulations, you made it. Please check out our rest of our tutorials to explore more such use cases.

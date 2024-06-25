## Chat with SQL Tables using Prem AI and llama-index

In this cookbook recipe, we are going to show how we can index a SQL Table to perform question answering on the table using llama-index and Prem AI. We also Streamlit to provide a nice UI of the overall project. 

The step by step tutorial is available [here](https://docs.premai.io/cookbook/chat-with-sql)

<img width="1119" alt="url-summarizer" src="../assets/chat with sql.jpeg">

### Setting up the project 

It's quite simple. First clone the repository:

```bash
git clone https://github.com/premAI-io/cookbook.git
cd cookbook/chat-with-sql
```

After that, create a virtual environment and install the requirements.

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Running the app

Before running the app, please do not forget to add the following values:

```
premai_api_key = "xxxx-xxxx-xxxx"
premai_project_id = xxxx
username = 'xxxxx'
password = 'xxxxx'
database = 'xxxxx'
```

inside `secrets.toml.template` file and remove `.template` from it. To run the app, type the following command:

```bash
streamlit run app.py
```
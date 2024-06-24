from typing import Union
from sqlalchemy import MetaData, create_engine

from llama_index.core import SQLDatabase
from llama_index.core.query_engine import NLSQLTableQueryEngine
from llama_index.core.llms.llm import LLM
from llama_index.core.embeddings import BaseEmbedding


# ---- Function to fetch all the tables from pg database ----
def get_all_tables_from_db(db_config: dict) -> Union[list, None]:
    metadata = MetaData()
    username = db_config["username"]
    host = db_config["host"]
    password = db_config["password"]
    port = db_config["port"]
    database = db_config["database"]

    try:
        engine = create_engine(
            f"postgresql://{username}:{password}@{host}:{port}/{database}"
        )
        metadata.reflect(bind=engine)
        table_names = metadata.tables.keys()
    except Exception as e:
        print(f"Error: {e}")
        return None
    return table_names


# ---- Function using llama-index to index the SQL entries for semantic search ----
def setup_index_before_chat(
    db_config: dict, table: str, llm: LLM, embed_model: BaseEmbedding
):
    username = db_config["username"]
    host = db_config["host"]
    password = db_config["password"]
    port = db_config["port"]
    database = db_config["database"]
    engine = create_engine(
        f"postgresql://{username}:{password}@{host}:{port}/{database}"
    )

    sql_database = SQLDatabase(engine=engine, include_tables=[table])
    query_engine = NLSQLTableQueryEngine(
        sql_database=sql_database,
        llm=llm,
        embed_model=embed_model,
    )
    return query_engine

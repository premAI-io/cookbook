from typing import Union, Optional
from sqlalchemy import MetaData, create_engine

from llama_index.core import SQLDatabase
from llama_index.core.query_engine import NLSQLTableQueryEngine
from llama_index.core.llms.llm import LLM
from llama_index.core.embeddings import BaseEmbedding
from llama_index.core.indices.struct_store import SQLTableRetrieverQueryEngine
from llama_index.core.objects import (
    SQLTableNodeMapping,
    ObjectIndex,
    SQLTableSchema
)
from llama_index.core import VectorStoreIndex

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


# ---- Function using llama-index to call Text2SQL for semantic QnA ----

def setup_index_before_chat(db_config: dict, table: str, ):
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
    )
    return query_engine


# ---- Function using llama-index to index the SQL entries with embeddings ----

def setup_index_before_chat_use_embedding(db_config: dict):
    username = db_config["username"]
    host = db_config["host"]
    password = db_config["password"]
    port = db_config["port"]
    database = db_config["database"]
    engine = create_engine(
        f"postgresql://{username}:{password}@{host}:{port}/{database}"
    )

    sql_database = SQLDatabase(engine=engine)
    table_node_mapping = SQLTableNodeMapping(sql_database)
    table_schema_objs = []

    all_table_names = get_all_tables_from_db(db_config)
    for table_name in all_table_names:
        table_schema_objs.append(SQLTableSchema(table_name=table_name))
    
    object_index = ObjectIndex.from_objects(
        table_schema_objs,
        table_node_mapping,
        VectorStoreIndex,
    )
    query_engine = SQLTableRetrieverQueryEngine(
        sql_database,
        object_index.as_retriever(similarity_top_k=1),
    )
    return query_engine


def setup_index(db_config, table: Optional[str]=None, use_all: bool=False):
    if use_all:
        # we assume that we are calling for all the tables 
        query_engine = setup_index_before_chat_use_embedding(db_config=db_config) 
    else:
        assert table is not None, ValueError("Table must not be None")
        query_engine = setup_index_before_chat(db_config=db_config, table=table)
    return query_engine
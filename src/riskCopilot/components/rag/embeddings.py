import os
import psycopg2
from sqlalchemy import make_url
from llama_index.vector_stores.postgres import PGVectorStore
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core import StorageContext
from llama_index.core import VectorStoreIndex
from llama_index.core import Settings
from llama_index.embeddings.openai import OpenAIEmbedding
from sqlalchemy import create_engine, MetaData


from llama_index.core.response_synthesizers import CompactAndRefine
from llama_index.core.retrievers import QueryFusionRetriever
from llama_index.core.query_engine import RetrieverQueryEngine

from dotenv import load_dotenv

load_dotenv()

from riskCopilot import logger


def get_table_names(connection_string: str) -> list:
    """
    input : link to the pg database

    output: list of  tables
    """

    try:
        # Create a SQLAlchemy engine
        engine = create_engine(connection_string)

        # Create a metadata object
        metadata = MetaData()

        # Reflect the tables from the database into the metadata
        metadata.reflect(bind=engine)

        # Get a list of all table names
        table_names = metadata.tables.keys()

        return list(table_names)
    except Exception as e:
        # Handle any exceptions (e.g., connection error)
        return str(e)


def create_text_embeddings(
    document: dict,
    db_name: str = os.environ["db_name"],
    connection_string: str = os.environ["connection_string"],
):
    """
    document : llamaindex document object

    creates text embeddings and and saves them to vector database
    """

    # Establish databse connection
    try:
        conn = psycopg2.connect(connection_string)
        # Additional database operations can be performed here
    except psycopg2.Error as e:
        print(f"Error connecting to PostgreSQL: {e}")

    # defign embedding model
    Settings.embed_model = OpenAIEmbedding(model="text-embedding-ada-002")

    # defign a node parsor object
    node_parser = SentenceSplitter()

    # Get the table names
    table_names = get_table_names(os.path.join(connection_string, db_name))

    for title in document:

        if "data_" + title not in table_names:
            # break documents into nodes
            nodes = node_parser.get_nodes_from_documents(document[title])

            # connect to pgvectordb
            url = make_url(connection_string)

            # create a table whose name is same as that of document name
            vector_store = PGVectorStore.from_params(
                database=db_name,
                host=url.host,
                password=url.password,
                port=url.port,
                user=url.username,
                table_name=title,
                embed_dim=1536,  # openai embedding dimension
                hybrid_search=True,
                cache_ok=True,
            )

            storage_context = StorageContext.from_defaults(vector_store=vector_store)

            VectorStoreIndex(nodes, storage_context=storage_context, show_progress=True)
        else:
            print(f"db {title} exsist!")


def load_text_embeddings(
    title: str,
    db_name: str = os.environ["db_name"],
    connection_string: str = os.environ["connection_string"],
) -> RetrieverQueryEngine:
    """
    title : the name of the document you want to load the embedding tool

    gets the retrival tool
    """

    # Establish databse connection
    try:
        conn = psycopg2.connect(connection_string)
        # Additional database operations can be performed here
    except psycopg2.Error as e:
        print(f"Error connecting to PostgreSQL: {e}")

    # defign embedding model
    Settings.embed_model = OpenAIEmbedding(model="text-embedding-ada-002")

    # Get the table names
    doc_names = get_table_names(os.path.join(connection_string, db_name))

    # connect to pgvectordb
    url = make_url(connection_string)

    # check if the database exsists
    if "data_" + title in doc_names:
        # create a table whose name is same as that of document name
        vector_store = PGVectorStore.from_params(
            database=db_name,
            host=url.host,
            password=url.password,
            port=url.port,
            user=url.username,
            table_name=title,
            embed_dim=1536,  # openai embedding dimension
            hybrid_search=True,
            text_search_config="english",
            cache_ok=True,
        )

        # build index
        index = VectorStoreIndex.from_vector_store(vector_store=vector_store)

        # dense retriver
        vector_retriever = index.as_retriever(
            vector_store_query_mode="default",
            similarity_top_k=3,
        )

        # sparse retriver
        text_retriever = index.as_retriever(
            vector_store_query_mode="sparse",
            similarity_top_k=3,  # interchangeable with sparse_top_k in this context
        )

        retriever = QueryFusionRetriever(
            [vector_retriever, text_retriever],
            similarity_top_k=3,
            num_queries=1,  # set this to 1 to disable query generation
            mode="relative_score",
            use_async=False,
        )

        response_synthesizer = CompactAndRefine()

        query_engine = RetrieverQueryEngine(
            retriever=retriever,
            response_synthesizer=response_synthesizer,
        )

        return query_engine

    else:
        raise ValueError(f"did not find the databse with the name {title}")

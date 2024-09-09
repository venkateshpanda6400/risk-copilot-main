import warnings

warnings.filterwarnings("ignore")

from riskCopilot import logger
from llama_index.core import VectorStoreIndex
from llama_index.core.objects import ObjectIndex
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.agent.openai import OpenAIAgent
from llama_index.postprocessor.colbert_rerank import ColbertRerank
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.llms.openai import OpenAI
from llama_index.core import Settings
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from riskCopilot.components.rag.embeddings import load_text_embeddings, get_table_names


import os
from dotenv import load_dotenv

load_dotenv()

import nest_asyncio

nest_asyncio.apply()

import streamlit as st


def bot(verbose=True):
    """
    initialise the agents, and make every document as a tool
    """
    logger.info("Initializing randstad_bot")

    Settings.llm = OpenAI(model="gpt-4-turbo")
    Settings.embed_model = OpenAIEmbedding(model="text-embedding-ada-002")
    logger.debug("Settings initialized")

    agents = {}

    for title in get_table_names(
        os.path.join(os.environ["connection_string"], os.environ["db_name"])
    ):
        logger.info(f"Processing table: {title}")
        title = title.replace("data_", "")

        vector_query_engine = load_text_embeddings(
            title=title,
            connection_string=os.environ["connection_string"],
            db_name=os.environ["db_name"],
        )
        logger.debug(f"Vector query engine loaded for {title}")

        query_engine_tools = [
            QueryEngineTool(
                query_engine=vector_query_engine,
                metadata=ToolMetadata(
                    name="vector_tool",
                    description=(
                        f"Useful for questions related to specific aspects of {title}"
                    ),
                ),
            ),
        ]

        function_llm = OpenAI(model="gpt-4-turbo")
        agent = OpenAIAgent.from_tools(
            query_engine_tools,
            max_function_calls=1,
            llm=function_llm,
            verbose=verbose,
            system_prompt=f"You are a specialized agent designed to answer queries about {title}. You must ALWAYS use at least one of the tools provided when answering a question; do NOT rely on prior knowledge.",
        )
        logger.debug(f"Agent created for {title}")

        agents[title] = agent

    logger.info("Creating tools for each document agent")
    all_tools = []

    for title in agents:
        wiki_summary = f"This content contains contract document {title}. Use this tool if you want to answer any questions about {title}.\n"
        doc_tool = QueryEngineTool(
            query_engine=agents[title],
            metadata=ToolMetadata(
                name=f"{title}",
                description=wiki_summary,
            ),
        )
        all_tools.append(doc_tool)

    obj_index = ObjectIndex.from_objects(
        all_tools,
        index_cls=VectorStoreIndex,
    )
    logger.debug("Object index created")

    memory = ChatMemoryBuffer(token_limit=4000)

    logger.info("Initializing main OpenAI agent")
    agent = OpenAIAgent.from_tools(
        max_function_calls=1,
        tool_retriever=obj_index.as_retriever(
            similarity_top_k=2, node_postprocessors=[ColbertRerank(top_n=3)]
        ),
        system_prompt="You are an AI assistant designed to help users with service agreements inquiries. Always rely on the provided information and avoid making assumptions. Maintain a formal yet approachable tone, and structure your responses using bullet points or paragraphs as appropriate. Always give your answers in not more than 3 sentences When asked for a detailed explanation, provide a thorough answer without imposing an arbitrary sentence limit. Use markdown formatting correctly, especially for code snippets or structured data. Analyze the context carefully and tailor your responses accordingly. Your goal is to deliver clear, helpful, and human-like assistance while adhering to the provided guidelines. IMPORTANT: DONOT rely on prior knowledge !!use the tools to understand and give responce !",
        verbose=verbose,
        memory=memory,
    )
    logger.info("randstad_bot initialization complete")

    return agent

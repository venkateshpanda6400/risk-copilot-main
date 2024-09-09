from llama_index.core import (
    SimpleDirectoryReader,
)
import os
from riskCopilot import logger
import os
import re


def document_loader() -> dict:
    """
    Function loads the text documents from the folder and returns a dictory of policy name and the document object
    """
    data_dir = "data/staged"

    if os.listdir(data_dir):
        documents = SimpleDirectoryReader(
            input_dir=data_dir,
            recursive=True,
            exclude=[
                file for file in os.listdir(data_dir) if not file.endswith(".txt")
            ],
        ).load_data()

        policy_name = [
            documents[i].metadata["file_name"].split(".")[0]
            for i in range(len(documents))
        ]
        logger.info("documents loaded !!")
        return {key: [value] for key, value in zip(policy_name, documents)}
    else:
        logger.warning("No files to load ")

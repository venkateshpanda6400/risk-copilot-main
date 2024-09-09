from metaflow import FlowSpec, step, card, Parameter, resources
from dotenv import load_dotenv
import os
import shutil
from pathlib import Path
import psutil
import logging
from riskCopilot.components.data_handling.scanned_pdf_parser import scanned_pdf_parser
from riskCopilot.components.rag.document_loader import document_loader
from riskCopilot.components.rag.embeddings import (
    get_table_names,
    create_text_embeddings,
)
from riskCopilot import logger


# Load environment variables from .env file
load_dotenv()


def get_system_info():
    # Get the number of CPU cores
    cpu_cores = psutil.cpu_count(logical=True)
    # Get the amount of RAM in GB
    ram_info = psutil.virtual_memory()
    ram_gb = ram_info.total / (1024**3)
    return cpu_cores, ram_gb


class Pipeline(FlowSpec):
    files = Parameter("files", help="list of file paths", type=str)

    @step
    def start(self):
        """
        Convert the file paths to list
        """
        # convert the file paths into list
        self.file = self.files.split(",")
        logger.info(f"Starting pipeline with {len(self.file)} files")
        self.next(self.stage_files, foreach="file")

    @resources(memory=get_system_info()[1], cpu=get_system_info()[0])
    @step
    def stage_files(self):
        """
        Pre-Process the files to the staging folder
        """
        # passing the path through this function will convert scanned documents to text and save them at staged area
        logger.info(f"Processing file: {self.input}")
        scanned_pdf_parser(self.input)
        self.next(self.join)


    @step
    def join(self, inputs):
        """
        Collect results from all branches
        """
        logger.info("Joining results from all branches")
        logger.info(f"Input: {inputs}")
        self.next(self.embeddings)


    @step
    def embeddings(self):
        """
        Create embeddings
        """
        logger.info("Creating embeddings")
        # load the documents
        documents = document_loader()
        # load the documents to be embedded
        create_text_embeddings(documents)
        # log the list of available embeddings
        available_embeddings = [
            i.replace("data_", "")
            for i in get_table_names(
                os.path.join(os.environ["connection_string"], os.environ["db_name"])
            )
        ]
        logger.info(f"The available embeddings are: {available_embeddings}")
        self.next(self.end)


    @step
    def end(self):
        """
        End of pipeline
        """
        logger.info("Pipeline execution completed.")


if __name__ == "__main__":
    Pipeline()

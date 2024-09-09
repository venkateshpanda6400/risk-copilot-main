import pytesseract
from pdf2image import convert_from_path
import tempfile
from riskCopilot import logger
import re
import os


def remove_underscores(file_path):
    # Split the path into directory, filename, and extension
    directory = "./data/staged/"
    extension = ".txt"

    # Extract the part between directory and extension
    middle_part = file_path[len(directory) : -len(extension)]

    # Remove leading and trailing underscores
    middle_part = middle_part.strip("_")

    # Reconstruct the file path
    new_file_path = directory + middle_part + extension

    return new_file_path


def delete_files(path):
    """
    given a file path, delet the file
    """
    try:
        # Ensure the path exists
        if not os.path.exists(path):
            print(f"The path {path} does not exist.")
            return

        # Check if it's a file or directory
        if os.path.isfile(path):
            os.remove(path)
            print(f"Deleted file: {path}")
        elif os.path.isdir(path):
            for root, dirs, files in os.walk(path, topdown=False):
                for file in files:
                    file_path = os.path.join(root, file)
                    os.remove(file_path)
                    print(f"Deleted file: {file_path}")
            print(f"All files in {path} have been deleted.")
        else:
            print(f"The path {path} is neither a file nor a directory.")

    except Exception as e:
        print(f"An error occurred: {e}")


def scanned_pdf_parser(pdf_path):
    """
    This function converts the scanned pdf documents to the text file
    """
    logger.info(f"Starting to parse scanned PDF: {pdf_path}")
    try:
        images = convert_from_path(pdf_path)
        logger.info(f"Successfully converted PDF to {len(images)} images")
        extracted_text = ""
        for i, image in enumerate(images):
            logger.debug(f"Processing page {i+1}")
            # Use Tesseract to extract text from each image
            text = pytesseract.image_to_string(image)
            extracted_text += f"Page {i+1}:\n{text}\n\n"

        text_path = pdf_path.replace("raw", "staged")

        # Apply the required modifications to text_path
        text_path = text_path.lower()
        text_path = re.sub(r" ", "_", text_path)  # replace excess space with underscore
        text_path = re.sub(
            r"[^a-z_/]", "_", text_path
        )  # keep path separrator and lower case alphabets
        text_path = text_path.replace("pdf", ".txt")  # keep the extention

        text_path = remove_underscores(text_path)

        logger.info(f"Writing extracted text to {text_path}")
        # Open the file in write mode
        with open(text_path, "w", encoding="utf-8") as txt_file:
            # Write text to the file
            txt_file.write(extracted_text)
        logger.info(f"Successfully wrote extracted text to {text_path}")
    except Exception as e:
        logger.error(f"Error occurred while parsing PDF {pdf_path}: {str(e)}")
        raise
    logger.info(f"Finished parsing scanned PDF: {pdf_path}")

    # deleted file from the source
    delete_files(pdf_path)
    logger.info(f"Finished deleteing the pdf file: {pdf_path}")

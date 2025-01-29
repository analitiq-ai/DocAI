import os
import sqlite3
from pathlib import Path
from pytz import timezone
from doc_manager.utils.db import create_table, add_document_db
from doc_manager.document_processor import DocumentProcessor
from doc_manager.models import Document
from doc_manager.utils.general import move_file, get_file_creation_time, generate_directory_tree, ALL_LANGUAGES
from weaviate.util import generate_uuid5

# Define the CET timezone
cet_timezone = timezone("CET")

# ------------------------------------------------------------------------
# Configure Logging
# ------------------------------------------------------------------------
from doc_manager.logger_setup import setup_logger
import logging
# Configure the logger
setup_logger(log_file="errors.log", console_level=logging.INFO, file_level=logging.ERROR)


def remove_extension(filename):
    """
    Takes a filename as a string, checks if it has an extension,
    and removes the extension if it exists.

    :param filename: str - The input filename
    :return: str - Filename without the extension
    """
    # Use os.path.splitext to split the filename into name and extension
    name, extension = os.path.splitext(filename)

    # Check if an extension exists
    if extension:
        return name
    return filename

# ------------------------------------------------------------------------
# Orchestrating Directory & File Processing
# ------------------------------------------------------------------------
class DirectoryProcessor:
    """
    Orchestrates the scanning of files in a directory and dispatches them
    to the appropriate processing functions based on file extension.
    """

    def __init__(self, config: dict, llm_client, vector_store_client):
        """
        :param config: Configuration dictionary.
        :param dir_tree: Directory tree structure of the target directory
        """
        self.config = config
        self.user_lang = ALL_LANGUAGES[config['user_language']]
        self.dir_tree = generate_directory_tree(config.get("DIR_ORGANISED"))
        self.target_directory = config.get("TARGET_DIRECTORY", "")
        self.extensions = config.get("EXTENSIONS", [])
        self.excluded_dirs = config.get("EXCLUDED_DIRECTORIES", [])
        self.categories = config.get("CATEGORIES", [])
        self.document_processor = DocumentProcessor(config, llm_client, self.dir_tree)
        self.vs = vector_store_client

    def validate_config(self):
        """
        Validates that the target directory, extensions, and categories exist or are properly formatted.
        """
        if not os.path.isdir(self.target_directory):
            raise ValueError(f"The provided path '{self.target_directory}' is not a valid directory.")

        if not isinstance(self.extensions, list) or not all(isinstance(ext, str) for ext in self.extensions):
            raise ValueError("EXTENSIONS must be a list of strings.")

        if not isinstance(self.excluded_dirs, list):
            raise ValueError("EXCLUDED_DIRECTORIES must be a list of strings.")

        if not self.categories:
            logging.warning("No CATEGORIES provided in config. Defaulting to an empty list.")

    def walk_through_directory(self):
        """
        Walks through the target directory, filters out excluded directories,
        processes files that match the allowed extensions, and invokes the
        appropriate DocumentProcessor method (PDF, image, or text).
        """
        self.validate_config()
        # Create DB table if not present
        # create_table()

        # Normalize extensions to have a leading dot, e.g. '.pdf'
        extensions_normalized = [
            ext.lower() if ext.startswith('.') else f'.{ext.lower()}'
            for ext in self.extensions
        ]
        excluded_dirs_lower = [d.lower() for d in self.excluded_dirs]

        logging.debug(self.dir_tree)

        for root, dirs, files in os.walk(self.target_directory, followlinks=False):
            # Exclude directories starting with a dot or in the excluded list
            dirs[:] = [
                d for d in dirs
                if not d.startswith('.') and d.lower() not in excluded_dirs_lower
            ]

            for file in files:
                file_path = Path(root) / file
                file_extension = file_path.suffix.lower()
                file_name = file_path.stem

                # Skip files without an extension
                if not file_extension:
                    print(f"Skipping file without an extension: {file_path}")
                    continue

                # Check if file extension is in the allowed set
                if file_extension in extensions_normalized:
                    logging.info(f"""\n\n========== "{file_path}" ==========""")

                    try:
                        # Dispatch to the correct processor based on extension
                        if file_extension.lower() in ['.jpeg', '.jpg', '.png']:
                            document_original = self.document_processor.process_img(file_path)
                        elif file_extension.lower() == '.pdf':
                            document_original = self.document_processor.process_pdf(file_path)
                    except Exception as e:
                        logging.error(f"Error processing file '{file_path}': {e}")
                        continue

                    if not document_original:
                        logging.error(f"Document is None: {file_path}")
                        continue
                    if not hasattr(document_original, "text") or len(document_original.text) < 10:
                        logging.error(f"Document text is empty: {file_path}. Loaded text: {document_original.text}")
                        continue

                    logging.info(f"Loaded text length: {len(document_original.text)}")
                    tokens = len(document_original.text)/4
                    context_length = self.config.get("LLM_CONTEXT_LENGTH", 16000)
                    if tokens > context_length:
                        logging.error(f"Document length of {tokens} tokens exceeds context length of {context_length} tokens. Skipping.")
                        continue

                    # We use only original text ofr UUID generation.
                    uuid = generate_uuid5({"text": document_original.text})
                    logging.info(f"Generated UUID from the image text {uuid}")


                    # Translate into Base Language
                    logging.info(f"Translating to {self.user_lang} and summarizing.")
                    try:
                        document_structured = self.document_processor.process_document_text(document_original, self.user_lang)
                        # Define the new directory of the document
                        new_filename = remove_extension(document_structured.new_filename) + file_extension
                        new_filepath = Path(document_structured.directory) / new_filename
                    except Exception as e:
                        logging.error(f"Error getting structured document: {e}")
                        continue

                    #logging.info(f"Original Document: {document_original.model_dump_json(indent=2)}")
                    #logging.info(f"Structured Document: {document_structured.model_dump_json(indent=2)}")

                    # Create a dictionary for the Document
                    document_dict = {
                        "uuid": uuid,
                        "title": document_structured.title,
                        "summary": document_structured.summary,
                        "category": document_structured.category,
                        "tags": document_structured.tags,
                        "langs": document_original.langs,
                        "filepath": str(new_filepath),
                        "filepath_orig": str(file_path)
                    }

                    # If original document is in the same language as users language
                    if len(document_original.langs) == 1 and document_original.langs[0] == self.user_lang:
                        document_dict["text"] = document_original.text
                    elif hasattr(document_structured, 'text_user_lang') and len(document_structured.text_user_lang) > 10:
                        document_dict["text"] = document_structured.text_user_lang
                        document_dict["text_orig"] = document_original.text
                    else:
                        exit("Error")

                    # If timestamp is not available within the documents, use the file creation time
                    if not hasattr(document_structured, 'timestamp') or not document_structured.timestamp:
                        document_dict["timestamp"] = get_file_creation_time(file_path)
                    else:
                        document_dict["timestamp"] = document_structured.timestamp

                    if document_dict["timestamp"].tzinfo is None:  # If naive, define it as CET
                        document_dict["timestamp"] = cet_timezone.localize(document_dict["timestamp"])

                    #logging.info(f"Document dictionary: {document_dict}")

                    # Create and return the Document object from the dictionary
                    try:
                        document = Document(**document_dict)
                    except Exception as e:
                        logging.error(f"Failed to create Document object from dictionary: {e}. \n {document_dict} \n {document_dict}")

                    # Insert original and translated document data into DB
                    try:
                        last_row_id = add_document_db(document)
                    except sqlite3.IntegrityError as e:
                        # Handle the UNIQUE constraint error
                        logging.error(f"Duplicate: {file_path} already exists in the database. Skipping. Error: {e}")
                        continue
                    except Exception as e:
                        logging.error("Failed to insert document %s:\n%s \n%s \n%s\n\n", file_path, document,  e)
                        raise e

                    # Insert into Vector Store database:
                    self.vs.add_document_vdb(document, last_row_id)

                    # Move the file to new directory (organizing)
                    try:
                        new_dir_tree = move_file(file_path, f"{self.config.get('DIR_ORGANISED')}/{document.filepath}", new_filename)
                        if new_dir_tree:
                            self.dir_tree = generate_directory_tree(self.config.get("DIR_ORGANISED"))
                    except Exception as e:
                        logging.error("Failed to move document:\n\n%s \n\n%s", document, e)
                        raise e
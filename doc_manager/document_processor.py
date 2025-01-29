import json
import logging
import os
from typing import Dict
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from doc_manager.models import DocumentRaw, DocumentLlm, DocumentStructured, DocumentStructuredTranslated
from doc_manager.prompt import PROCESS_DOC_TEXT_PROMPT, COMMON_INSTRUCTIONS, PROCESS_TRANSLATE_DOC_TEXT_PROMPT
from doc_manager.items_manager import ItemsManager
from doc_manager.processors.ocr import OCRProcessor
from langdetect import detect_langs
from doc_manager.utils.general import ALL_LANGUAGES
from doc_manager.utils.pdf_to_img import pdf_to_page_imgs
from doc_manager.utils.img import resize_image_to_size

# ------------------------------------------------------------------------
# Document Processing
# ------------------------------------------------------------------------
class DocumentProcessor:
    """
    Handles reading and parsing documents of different types
    (Image, PDF, Text) and returning structured data via Pydantic models.
    """

    def __init__(self, config: dict, llm, dir_tree: str):
        """
        :param config: Configuration dictionary.
        :param llm: LLM interface for processing text-based documents.
        :param dir_tree: Directory tree string for insertion into prompts.
        """
        self.config = config
        self.llm = llm
        self.dir_tree = dir_tree
        self.parser = PydanticOutputParser(pydantic_object=DocumentLlm)

        self.tag_manager = ItemsManager(config.get("tags_list_filename"))
        self.categories_manager = ItemsManager(config.get("categories_list_filename"))

        #self.tags = self.tag_manager.get_all_items_str()
        self.categories = self.categories_manager.get_all_items_str()

        # Initialize the processor
        self.processor = OCRProcessor(self.config)

    def process_img(self, file_path: Path):
        result = None

        file_size_mb = os.path.getsize(file_path)
        img_limit_mb_in_bytes = self.config['img_mb_limit'] * 1024 * 1024  # 5 MB in bytes

        if file_size_mb > img_limit_mb_in_bytes:
            logging.info(f"Image is too large, resizing to {self.config['img_mb_limit']} MB limit.")
            resize_image_to_size(file_path, file_path, img_limit_mb_in_bytes)

        try:
            result = self.llm.invoke_img_from_path(file_path)
            logging.info(f"Obtained text from image: {result.text[:100]}{'...' if len(result.text) > 100 else ''}")
            return result
        except Exception as e:
            logging.error(f"Error processing image with LLM: {e}")

        logging.info("Falling back to OCR...")

        try:
            result = DocumentRaw(
                text=self.processor.load_img_file_and_perform_ocr(file_path),
                langs=self.config['document_languages']
            )
        except Exception as e:
            logging.error(f"Error processing image with OCR: {e}")

        return result


    def process_pdf(self, file_path: Path) -> DocumentRaw | None:
        """
        Processes a PDF file and returns a DocumentLlm.

        :param file_path: Path to the PDF file.
        :return: DocumentLlm object or None if an error occurred.
        """
        result = None
        logging.info("Initializing PDF Analysis.")

        # Attempt 1 - Use PDF Loader to load PDF text
        try:
            loader = PyPDFLoader(file_path)
            documents = loader.load()
            pages = len(documents)
            document_text = "\n\n".join(doc.page_content for doc in documents)
        except Exception as e:
            logging.error(f"Error while reading PDF file '{file_path}': {e}")
            return None

        if len(document_text) > 10:
            return DocumentRaw(
                text=document_text,
                langs=self.detect_languages_in_text(document_text)
            )

        # Attempt 2 - convert PDF to Image and use LLM vision to get the text
        # If the document is too small, that is a sign that PDF reader cannot recognise it.
        # This will happen is the document is a PDF image

        logging.info("Document is not recognised by PDF reader, trying to use image processing...")
        list_image_bytes = pdf_to_page_imgs(file_path)
        document = DocumentRaw(
            text="",
            langs=[]
        )
        seen = set(document.langs)

        for page_num, page_image_bytes in enumerate(list_image_bytes, 1):
            logging.info(f"Processing page {page_num}...")
            result = self.llm.invoke_img_from_binary(page_image_bytes, 'image/png')
            document.text += "\n\n" + result.text
            document.langs.extend(item for item in result.langs if item not in seen and not seen.add(item))

        if len(document.text) > 10:
            return document

    @staticmethod
    def detect_languages_in_text(document_text: str) -> list:
        try:
            # Get the probabilities of detected languages
            probabilities = detect_langs(document_text)
            # Extract the list of languages
            languages = [ALL_LANGUAGES[prob.lang] for prob in probabilities]
            logging.info(f"Detected languages: {languages}")
            return languages
        except Exception as e:
            # Escape parentheses in the file path manually
            logging.error(f"""Error while detecting languages: {e}""")
            return []


    def process_document_text(self, document_original: Dict, user_language :str) -> DocumentStructured:
        """
        Translates the given document_text to English and returns a Pydantic model with translation.

        :return: DocumentStructured object containing the translated text and summary.
        """
        if document_original.langs == user_language:
            prompt_template =  PROCESS_DOC_TEXT_PROMPT
            parser = PydanticOutputParser(pydantic_object=DocumentStructured)
        else:
            prompt_template =  PROCESS_TRANSLATE_DOC_TEXT_PROMPT
            parser = PydanticOutputParser(pydantic_object=DocumentStructuredTranslated)

        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["document_text"],
            partial_variables={
                "document_languages": document_original.langs,
                "user_language": user_language,
                "categories": self.categories,
                "dir_tree":self.dir_tree,
                "common_instructions": COMMON_INSTRUCTIONS,
                "format_instructions": parser.get_format_instructions()
            },
        )

        try:
            response = self.llm.invoke_llm(prompt, document_original.text, parser)
            return response
        except Exception as e:
            logging.error(f"Error during translation: {e}")
            return None

    @staticmethod
    def attempt_to_load_json(content):
        # Remove the surrounding markdown and newline characters
        json_str = content.strip('```json\n').strip('\n```')

        # Parse the JSON string
        data = json.loads(json_str)

        return DocumentLlm(**data)

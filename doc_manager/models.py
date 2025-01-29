from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date

class DocumentRaw(BaseModel):
    text: str = Field(..., description="The text of the document.")
    langs: List[str] = Field(description="The languages of the text in the document as an ISO 639-1 2 character abbreviation. Note that a document could have many languages")

class DocumentLlm(BaseModel):
    title: str = Field(..., description="The title of the document in document language. If none is available in the document, create the title from document text.")
    text: str = Field(..., description="The text of the document body.")
    category: str = Field(..., description="The category the document should belong to. Only 1 is allowed.")
    location: str = Field(..., description="Define the directory or folder where the document should be located to in order to keep it organised in the provided directory tree.")
    document_filename: str = Field(..., description="Define the proper filename for the document in english.")
    tags: List[str] = Field(default_factory=list, description="A small list of 2-5 tags or keywords in English for the document.")
    timestamp: Optional[datetime] = Field(None,description="Timestamp of the document in ISO format, if it is available in the document. Else leave blank.")
    lang: str = Field(description="The language of the document.")

class DocumentStructured(BaseModel):
    title: str = Field(..., description="Document title in the users language. If none is available in the document, create the title from document text.")
    summary: str = Field(..., description="A brief summary of the document in users language.")
    category: str = Field(..., description="The category the document should belong to. Only 1 is allowed.")
    extension: str = Field(..., description="The file extension/type of the document (e.g., .pdf, .jpg).")
    directory: str = Field(..., description="Define the directory or folder where the document should be located to in order to keep it organised in the provided directory tree.")
    new_filename: str = Field(..., description="Define the proper filename for the document in english.")
    tags: List[str] = Field(default_factory=list, description="A small list of 2-5 tags or keywords in the users language as the document for the document.")
    timestamp: Optional[datetime] = Field(None,description="Timestamp of the document in ISO format, if it is available in the document. Else leave blank.")

class DocumentStructuredTranslated(DocumentStructured):
    text_user_lang: str = Field(None, description="All of the document text translated into the users language.")

class Document(BaseModel):
    uuid: str = Field(..., description="Unique identifier for the document in Vector Database.")
    title: str = Field(..., description="The title of the document in user language.")
    text: str = Field(..., description="The text of the document body in user language.")
    summary: str = Field(..., description="A brief summary of the document in users language.")
    text_orig: Optional[str] = Field(None, description="Document text if original text is in language other than users language.")
    category: str = Field(..., description="The category the document should belong to. Only 1 is allowed.")
    tags: List[str] = Field(default_factory=list, description="A small list of 2-5 tags or keywords in users language for the document.")
    timestamp: Optional[datetime] = Field(None,description="Timestamp of the document in ISO format, if it is available in the document. Else leave blank.")
    langs: List[str] = Field(description="The languages of the document.")
    filepath: str = Field(..., description="Define the proper filename for the document in users language without the file extension.")
    filepath_orig: str = Field(..., description="The original file path of the document.")
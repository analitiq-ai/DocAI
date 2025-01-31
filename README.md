# AI Document Management and Search Application

"I was drowning in thousands of documents in four different languages—cluttering my shelves and buried in countless computer folders. Then one day, I'd had enough! But instead of organizing them myself (because let’s be real, I’m too lazy for that), I made AI do the hard work. And what happened next is this project... 👀🔥"

> **Transform your documents into structured, organized, and queryable knowledge!**  
This Python-based app helps you make sense of your PDFs and image files by automatically extracting text, summarizing content, tagging key details like language and topics, and organizing everything neatly into folders. It even compiles documents into a vector database, making them easy to search. Plus, with built-in multilingual support, it can translate foreign-language documents into your preferred language, so nothing gets lost in translation.

![Analitiq document Management AI Application](analitiq_doc_management.webp)

---

## Key Features

### 1. **Document Parsing and Text Extraction**
- **Input Types:** Works with PDFs and image files (.jpg, .jpeg, .png).
- Utilizes Optical Character Recognition (OCR) to extract text from images.
- Falls back to converting PDF pages into images for text extraction when PDFs are poorly formatted or image-based.

---

### 2. **Document Summarization & Tagging**
- Automatically summarizes documents for quick understanding.
- Generates 2–5 relevant tags to classify and categorize the content.
- Detects and extracts languages from multilingual documents.

---

### 3. **High-Level Organization**
- Organizes documents into pre-configured directories based on their content, tags, and categories.
- Automatically assigns directory paths for logical grouping—e.g., all tax documents are neatly stored under a `Taxes` directory.

#### Example:
```python
from pathlib import Path
from doc_ai.utils.general import move_file
# Organize a file into a categorized folder
new_directory = move_file(Path("input/document.pdf"), "Organized/Taxes", "document.pdf")
print("New Directory:", new_directory)
```

---

### 4. **Multi-Language Processing with Translation**
- **Language Detection:** Detects the languages within a document (supports ISO 639-1 standards).
- Translates content from any foreign language into the user's preferred base language for consistency.
- Available languages are customizable via the config (e.g., English, German, Russian).

---

### 5. **Integration with Weaviate Vector Database**
Pushes processed documents into a **Weaviate** vector database to enable efficient search and retrieval. Document content is vectorized using the Ollama embeddings.

- **Search Functions:** Add full-text or semantic search capabilities to your document collection. Perfect for RAG (Retrieval-Augmented Generation) applications.
- **Search Example:**
```python
from doc_ai.clients.vdb_client import VdbClient

vdb = VdbClient(collection_name="Documents")
results = vdb.langchain_search("Find documents related to taxes")
for doc, score in results:
  print(f"Document: {doc}, Score: {score}")
```

#### Weaviate Prerequisites:
Weaviate setup requires **Docker**. Ensure Ollama's embedding service is running:
```shell script
apk add curl
curl http://localhost:11434/api/embed -d '{
"model": "nomic-embed-text",
"input": "Llamas are members of the camelid family"
}'
```

---

### 6. **PDF to Image Conversion (Fallback)**
When facing unreadable PDFs, the application:
1. Splits the PDF into individual page images.
2. Processes pages one by one to extract textual content.
3. Combines results into a coherent document if required.

#### Example:
```python
from doc_ai.utils.pdf_to_img import pdf_to_page_imgs

images = pdf_to_page_imgs("unreadable.pdf")
for idx, img in enumerate(images):
    print(f"Page {idx + 1}: Processed successfully.")
```

---

### 7. **Image Compression (Size Optimization)**
For scanned image files exceeding size limits (e.g., 5 MB), the app resizes and compresses the image while retaining sharpness. Ideal for processing large documents.

#### Example:
```python
from doc_ai.utils.img import resize_image_to_size

resize_image_to_size("large_image.jpg", "optimized_image.jpg", max_size_mb=5)
print("Image successfully resized under 5MB!")
```

---

## Installation and Setup

### Prerequisites
- Python 3.9 or higher
- **Docker** (for running Weaviate locally)
- **Ollama LLM API** (for embeddings and advanced text generation)

### Installation
1. Clone the repository:
```shell script
git clone https://github.com/analitiq-ai/DocAI
```

2. Install dependencies via `poetry`:
```shell script
poetry install
```

3. Run Weaviate using Docker:
```shell script
docker run -d -p 8080:8080 semitechnologies/weaviate:latest
```
You will need to create weaviate collection and schema one time to store your documents. 
```python
from doc_ai.clients.vdb_client import VdbClient

vector_client = VdbClient()
try:
  vector_client.create_collection()
except Exception as e:
  print(e)
```

4. Install Ollama and pull `nomic-embed-text` encoder and `llama3.2` llm.
```shell script
ollama pull nomic-embed-text, llama3.2
ollama pull llama3.2
start-ollama --model llama3.2
```

5. Set up configuration that is unique to you:
   - Rename `.env_template` into `.env` and set up API keys for Bedrock LLM. The default model is using Mistral on AWS Bedrock. 
   - Rename `config_template.json` into `config.json` and set up the parameters for your LLMs.


6. Set up `COMMON_INSTRUCTIONS` in prompts.py. These are general instructions about what the model should know about you. For example "I have a company called Acme Enterprises."


7. Run `python first_run.py` to set up your Weaviate Collection and Sqlite DB that will keep track of your documents.


8. Run `python main.py` to launch DocAi application and make it organise your documents.

---

## Configuration

The application's behavior is controlled through a `config.json` file. Below is an example:

```json
{
   "TARGET_DIRECTORY": "/path/to/documents",
   "DIR_ORGANISED": "/path/to/organized/documents", 
   "EXTENSIONS": [".pdf", ".jpeg", ".jpg", ".png"], 
   "EXCLUDED_DIRECTORIES": ["node_modules", "venv"], 
   "CATEGORIES": ["my_category1"], 
   "USER_LANGUAGE": "en",
   "DOCUMENT_LANGUAGES": ["de", "en", "ru", "bu", "ro"],
   "TESSDATA_DIR": "../tmp/",
   "LLM_CONTEXT_LENGTH": 200000,
   "IMG_MB_LIMIT": 4,
   "SQLDB_DB_PATH": "../documents.db",
   "SQLITE_TABLE_NAME": "documents"
}
```
1. **`TARGET_DIRECTORY`:** Defines the main directory path where the application scans for the input documents and images to process.
2. **`EXTENSIONS`:** A list of file extensions to process (e.g., `.pdf`, `.jpeg`, `.png`), specifying supported document and image types.
3. **`EXCLUDED_DIRECTORIES`:** Names of directories to exclude from scanning, such as typical folders for temporary or unrelated files (e.g., `node_modules`, `venv`).
4. **`LLM_CONTEXT_LENGTH`:** Maximum context length supported by the LLM for text processing, ensuring efficient handling of large documents.
5. **`DIR_ORGANISED`:** Path to the directory where organized or categorized documents are stored after processing.
6. **`CATEGORIES`:** Name of the JSON file that holds the list of predefined categories for document organization.
7. **`USER_LANGUAGE`:** The base language selected by the user (e.g., `en`) for translations.
8. **`DOCUMENT_LANGUAGES`:** A list of languages (ISO 639-1 codes) that the application can detect and process for multilingual document support.
9. **`IMG_MB_LIMIT`:** The maximum size (in MB) allowed by LLM for image files during processing, ensuring large files are resized or compressed as required.
10. **`SQLDB_DB_PATH`:** Path to where Sqlite database will be created.
11. **`SQLITE_TABLE_NAME`:** Name of the table in the database that will store your documents.

---

## Example Workflow

### Processing Documents
```python
from doc_ai.processors.directory_processor import DirectoryProcessor
from doc_ai.clients.vdb_client import VdbClient
from doc_ai.clients.bedrock_client import BedrockClient

llm_client = BedrockClient()
vector_store_client = VdbClient()
config = {}  # Load your configuration from config.json
directory_processor = DirectoryProcessor(config, llm_client, vector_store_client)
directory_processor.walk_through_directory()
```

### Searching Documents
```python
from doc_ai.clients.vdb_client import VdbClient

vdb = VdbClient(collection_name="Documents")
results = vdb.langchain_search("Find tax-related documents")
for doc, score in results:
    print(f"Document Title: {doc}, Score: {score}")
```

---

## Use Cases

1. **Document Organization**
   - Automatically categorize and move documents into logical folders.
2. **Multi-Language Support**
   - Seamlessly deal with foreign-language documents.
3. **Semantic Search**
   - Enable intelligent queries using vector databases.

---
## Key functions
### PDF to Image Conversion
When a PDF contains images of text that cannot be processed by standard PDF readers (e.g., OCR-based or image-only PDFs), these fallback functions are used to convert the PDF into images for further processing:
1. **`pdf_to_page_imgs(file_path: str)` **:
   - Converts each page of the PDF into a binary (black and white) image and returns a list of byte-represented images.
   - **Use Case**: For long PDFs, where processing each page as a separate image is necessary to avoid exceeding the context limits of an LLM.

2. **`pdf_to_combined_img(file_path: str)`**:
   - **Combines all pages of the PDF into a single vertically stacked, binary image and returns the binary data of the combined image in PNG format.
     -** **Use Case**: For short PDFs, where the entire document can be converted into one long image for more efficient processing by an LLM.

3. **`resize_image_to_size`**: Designed to optimize scanned document images so they can fit within a file size limit, such as the 5 MB limit commonly imposed by some LLMs. This function ensures that the image file is compressed and resized while maintaining as much of its original quality and sharpness as possible, preserving text readability in the process.
   - **File Compression**: Reduces the file size to be just under the specified limit (e.g., 5 MB) without significant loss of quality.
   - **Text Readability**: Uses advanced resizing methods to ensure that scanned documents with text remain crisp and legible.
   - **Iterative Optimization**: Dynamically adjusts image dimensions and compression quality to achieve the target size.
   - **High-Quality Resizing**: Uses the LANCZOS filter for resizing, which is ideal for reducing dimensions without sacrificing detail.
   - **Error Handling**: Safeguards against invalid file paths or unsupported formats.


---

## FAQs
### Can I run this on local LLM?
You can run it locally, but you need to find a suitable model for Image to Text detection.

### Vectorization is not working
Test that Ollama embedding are working:
```shell
apk add curl

curl http://localhost:11434/api/embed -d '{
"model": "nomic-embed-text",
"input": "Llamas are members of the camelid family"
}'
```

---

## Contribution

Contributions are welcome! Feel free to open issues or submit pull requests.

---

### License

This project is licensed under the MIT License.

---

## Acknowledgements

Special thanks to:
- [Weaviate](https://weaviate.io) for the vector database platform.
- [Ollama](https://ollama.ai/) for LLM and embeddings support.
- The open-source community for various tools integrated into this project.







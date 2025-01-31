import weaviate
from weaviate.classes.config import Configure
from doc_ai.configs.models import Document
from langchain_weaviate.vectorstores import WeaviateVectorStore
from langchain_ollama import OllamaEmbeddings
from langchain_ollama.llms import OllamaLLM

class VdbClient:
    def __init__(self, collection_name="Documents"):
        """Initialize the Weaviate client."""
        self.client = weaviate.connect_to_local()
        self.model = OllamaLLM(model="llama3.2")
        self.collection_name = collection_name
        self.embeddings = OllamaEmbeddings(model='nomic-embed-text')

    def create_collection(self):
        """Create a new collection."""
        self.client.collections.create(
            name=self.collection_name,
            vectorizer_config=Configure.Vectorizer.text2vec_ollama(     # Configure the Ollama embedding integration
                name="title_vector",
                source_properties=["text"],
                api_endpoint="http://host.docker.internal:11434",       # Allow Weaviate from within a Docker container to contact your Ollama instance
                model="nomic-embed-text",                               # The model to use
            ),
            generative_config=Configure.Generative.ollama(              # Configure the Ollama generative integration
                api_endpoint="http://host.docker.internal:11434",       # Allow Weaviate from within a Docker container to contact your Ollama instance
                model="llama3.2",                                       # The model to use
            )
        )

        self.client.close()  # Free up resources

    def delete_collection(self):
        """Delete a collection."""
        self.client.collections.delete(self.collection_name)
        self.client.close()

    def add_document_vdb(self, document: Document, last_row_id: int = None):
        """Add a document to Weaviate."""
        self.client.connect()
        collection = self.client.collections.get(self.collection_name)
        data = document.model_dump()

        # add title to search term text
        data['text'] = data['title']  + "\n\n" + data['text']
        data['db_id'] = last_row_id

        with collection.batch.dynamic() as batch:
            # because of the variation in LLM interpretation of data, we use only original text ofr UUID generation.
            batch.add_object(
                properties=data,
                uuid=document.uuid
            )

        self.client.close()

    def get_all_objects(self, include_vector = False):
        collection = self.client.collections.get(self.collection_name)

        for item in collection.iterator(
                include_vector=include_vector  # If using named vectors, you can specify ones to include e.g. ['title', 'body'], or True to include all
        ):
            print(item.properties)
            print(item.vector)

    def search_documents(self, query: str):
        """Search for documents based on a query."""
        self.client.connect()
        collection = self.client.collections.get(self.collection_name)

        try:
            response = collection.query.near_text(query="food", limit=3)

            return response
        finally:
            self.client.close()

    def delete_objects(self, uuids_to_delete: list):
        collection = self.client.collections.get(self.collection_name)
        # Deleting objects by UUID
        for uuid in uuids_to_delete:
            try:
                collection.data.delete_by_id(
                    uuid
                )
                print(f"Successfully deleted object with UUID: {uuid}")
            except Exception as e:
                print(f"Failed to delete object with UUID: {uuid}. Error: {str(e)}")

        self.client.close()  # Free up resources

    def get_weavaiate_class_object(self):
        return WeaviateVectorStore.from_documents(
            [],
            self.embeddings,
            client=self.client,
            index_name=self.collection_name,
        )

    def langchain_search(self, query: str):
        db = self.get_weavaiate_class_object()
        docs = db.similarity_search_with_score(query, k=5)
        self.client.close()
        return docs

    def close(self):
        self.client.close()

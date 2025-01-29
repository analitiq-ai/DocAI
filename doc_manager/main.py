from utils.general import load_config
from directory_processor import DirectoryProcessor
from vdb_client import VdbClient
#from langchain_openai import ChatOpenAI
from langchain.globals import set_debug
from llm_models.bedrock import BedrockClient

# ------------------------------------------------------------------------
# Configure Logging
# ------------------------------------------------------------------------
from logger_setup import setup_logger
import logging
# Configure the logger
setup_logger(log_file="errors.log", console_level=logging.INFO, file_level=logging.ERROR)

#set_debug(True)

# ------------------------------------------------------------------------
# Main Execution
# ------------------------------------------------------------------------
def main():
    """
    Main function to load config, generate directory tree, and process files in the directory.
    """
    config_file = "config.json"  # Path to the configuration file
    config = load_config(config_file)

    vector_client = VdbClient()
    vector_client.close()
    """
    # Run this one time to create weaviate collection and schema
    try:
        vs.create_collection()
    except Exception as e:
        print(e)

    """

    """
    llm_client = ChatOpenAI(
        api_key=config["OPENAI_API_KEY"],
        temperature=0.5,
        model=config.get("MODEL_NAME", "gpt-4o"),
        max_tokens=config.get("MAX_TOKENS", 2024)
    )
    """

    llm_client = BedrockClient()

    processor = DirectoryProcessor(config, llm_client, vector_client)
    processor.walk_through_directory()


if __name__ == "__main__":
    main()

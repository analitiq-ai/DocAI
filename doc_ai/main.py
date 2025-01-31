from utils.general import load_config
from utils.logger_setup import setup_logger
from processors.directory_processor import DirectoryProcessor
from clients.vdb_client import VdbClient
from clients.bedrock_client import BedrockClient

# ------------------------------------------------------------------------
# Configure Logging
# ------------------------------------------------------------------------

import logging
# Configure the logger
setup_logger(log_file="errors.log", console_level=logging.INFO, file_level=logging.ERROR)

# ------------------------------------------------------------------------
# Main Execution
# ------------------------------------------------------------------------
def main():
    """
    Main function to load config, generate directory tree, and process files in the directory.
    """
    config_file = "configs/config.json"  # Path to the configuration file
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

    llm_client = BedrockClient()

    processor = DirectoryProcessor(config, llm_client, vector_client)
    processor.walk_through_directory()


if __name__ == "__main__":
    main()

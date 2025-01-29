import boto3
import logging
from langchain_aws import ChatBedrock
from doc_manager.llm_models.base_llm import BaseLlm

class BedrockClient(BaseLlm):
    """Wrapper for Large language models."""

    def connect(self):
        region = 'eu-central-1'

        client = boto3.client(
            "bedrock-runtime",
            region_name=region
        )

        return ChatBedrock(
            client=client,
            region_name=region,
            provider='anthropic',
            model_id='anthropic.claude-3-5-sonnet-20240620-v1:0',
            model_kwargs={
                "temperature": 0,
                "max_tokens": 16000,
            },
            streaming=False,
        )

        logging.info(f"LLM is set to {params['type']}")

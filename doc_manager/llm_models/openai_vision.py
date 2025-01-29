import base64
from langchain.chains import TransformChain
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langchain_core.runnables import chain

@chain
def image_model(inputs: dict) -> str | list[str] | dict:
    """Invoke model with image and prompt."""
    model = ChatOpenAI(api_key=inputs["api_key"],
                       temperature=0.5,
                       model="gpt-4o",
                       max_tokens=1024)
    msg = model.invoke(
        [HumanMessage(
            content=[
                {"type": "text", "text": inputs["prompt"]},
                {"type": "text", "text": inputs["parser"].get_format_instructions()},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{inputs['image']}"}},
            ])]
    )
    return msg.content


def load_image(inputs: dict) -> dict:
    """Load image from file and encode it as base64."""
    image_path = inputs["image_path"]

    def encode_image(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    image_base64 = encode_image(image_path)
    return {"image": image_base64}


load_image_chain = TransformChain(
    input_variables=["image_path"],
    output_variables=["image"],
    transform=load_image
)

class OpenAIClient:
    """A class for analyzing images by piping tasks into a chain."""

    def __init__(self, config, parser):
        self.config = config
        self.parser = parser

    def invoke_img(self, prompt, image_path: str) -> dict:

        # Compose the pipeline:
        vision_chain = (
                load_image_chain       # returns { "image": base64_image }
                | image_model          # passes { "image": ..., "prompt": ... }
                | self.parser
        )
        return vision_chain.invoke(
            {
                "api_key": self.config["OPENAI_API_KEY"],
                "parser": self.parser,
                "image_path": image_path,
                "prompt": prompt,
            }
        )

import os
import base64
import requests
import logging.config

from omegaconf import OmegaConf


logging_config = OmegaConf.to_container(OmegaConf.load("./src/rag_api/conf/logging_config.yaml"), resolve=True)
logging.config.dictConfig(logging_config)
logger = logging.getLogger(__name__)


# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


class OpenAI:
    def __init__(self, model_name: str, prompt_template: str, max_tokens: int = 400):
        self.base_url = "https://api.openai.com/v1/chat/completions"
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        if OPENAI_API_KEY is None:
            logger.error("OPENAI_API_KEY is not set in the environment variables.")
            raise ValueError("OPENAI_API_KEY is not set in the environment variables.")
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_API_KEY}"
        }
        self.model_name = model_name
        self.prompt_template = prompt_template
        self.max_tokens = max_tokens

    def invoke(self, query: str, document_text: list[str], document_name: list[str]):
        """Run the LLM model with the given query and document."""

        prompt = self.prompt_template.format(
                        query=query,
                        document_name=document_name[0],
                        document_text=document_text[0]
                    )

        payload = {
            "model": self.model_name,
            "messages": [
                {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
                }
            ],
            "max_tokens": self.max_tokens
        }


        response = requests.post(self.base_url, headers=self.headers, json=payload)

        # Check if the response code is not 200
        if response.status_code != 200:
            raise Exception(f"Request failed with status code {response.status_code}: {response.text}")

        response_json = response.json()
        return response_json["choices"][0]["message"]["content"]

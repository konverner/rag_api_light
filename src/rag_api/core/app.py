import logging.config
from omegaconf import OmegaConf

# Load logging configuration with OmegaConf
logging_config = OmegaConf.to_container(OmegaConf.load("src/llm_chatbot_api/conf/logging_config.yaml"), resolve=True)
logging.config.dictConfig(logging_config)
logger = logging.getLogger(__name__)

class App:
    def __init__(self, hello_message: str):
        self.hello_message = hello_message

    def run(self, name: str) -> str:
        logger.info(f"Running with name: {name}")
        return f"{self.hello_message}: {name}"

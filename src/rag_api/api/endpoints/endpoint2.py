import logging
from datetime import datetime

from fastapi import APIRouter
from rag_api.db.crud import add_client
from rag_api.core.app import App
from omegaconf import OmegaConf

from src.rag_api.api.schemas import Endpoint2Response, Endpoint2Request
from src.rag_api.db.crud import read_client

# Load logging configuration with OmegaConf
logging_config = OmegaConf.to_container(
    OmegaConf.load("src/rag_api/conf/logging_config.yaml"),
    resolve=True
)
logging.config.dictConfig(logging_config)
logger = logging.getLogger(__name__)

router = APIRouter()
app = App(hello_message="Hello from the endpoint2")
@router.post("/endpoint2", operation_id="ENDPOINT-2")
def endpoint2(request: Endpoint2Request) -> Endpoint2Response:
    client_name = request.client_name
    content = request.content

    # Check if the client already exists
    db_client = read_client(client_name)
    if db_client is None:
        logger.info(f"Client {client_name} does not exist.")
        add_client(client_name)
        logger.info(f"User {client_name} added successfully.")
    app_output = app.run(client_name)
    response = Endpoint2Response(message=app_output, timestamp=datetime.now())
    return response

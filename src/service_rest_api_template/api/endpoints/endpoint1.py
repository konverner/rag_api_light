import logging
from datetime import datetime

from fastapi import APIRouter
from service_rest_api_template.db.crud import add_client
from service_rest_api_template.core.app import App
from omegaconf import OmegaConf

from src.service_rest_api_template.api.schemas import Endpoint1Response, Endpoint1Request
from src.service_rest_api_template.db.crud import read_client

# Load logging configuration with OmegaConf
logging_config = OmegaConf.to_container(
    OmegaConf.load("src/service_rest_api_template/conf/logging_config.yaml"),
    resolve=True
)
logging.config.dictConfig(logging_config)
logger = logging.getLogger(__name__)

router = APIRouter()
app = App(hello_message="Hello from the endpoint1")

@router.post("/endpoint1", operation_id="ENDPOINT-1")
def endpoint1(request: Endpoint1Request) -> Endpoint1Response:
    client_name = request.client_name
    content = request.content

    # Check if the client already exists
    db_client = read_client(client_name)
    if db_client is None:
        logger.info(f"Client {client_name} does not exist.")
        add_client(client_name)
        logger.info(f"User {client_name} added successfully.")
    app_output = app.run(client_name)
    response = Endpoint1Response(message=app_output, timestamp=datetime.now())
    return response


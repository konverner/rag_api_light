import logging

import uvicorn
from fastapi import FastAPI
from omegaconf import OmegaConf
from service_rest_api_template.api.endpoints import endpoint1, endpoint2
from service_rest_api_template.db.database import create_tables


# Load logging configuration with OmegaConf
logging_config = OmegaConf.to_container(
    OmegaConf.load("./src/service_rest_api_template/conf/logging_config.yaml"),
    resolve=True
)
logging.config.dictConfig(logging_config)
logger = logging.getLogger(__name__)

def create_app(config_path: str = "src/service_rest_api_template/conf/config.yaml") -> FastAPI:
    """
    Create a FastAPI application with the specified configuration.
    Args:
        config_path: The path to the configuration file in yaml format

    Returns:
        FastAPI: The FastAPI application instance.
    """
    config = OmegaConf.load(config_path)

    app = FastAPI(title=config.api.title, description=config.api.description, version=config.api.version)

    app.include_router(endpoint1.router)
    app.include_router(endpoint2.router)

    return app


if __name__ == "__main__":
    config_path = "src/service_rest_api_template/conf/config.yaml"
    config = OmegaConf.load(config_path)
    create_tables()
    app = create_app(config_path)
    logger.info("Starting the API server...")
    uvicorn.run(app, host=config.api.host, port=config.api.port, log_level="info")
    logger.info("API server stopped.")

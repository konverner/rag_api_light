import logging

import uvicorn
from fastapi import FastAPI
from omegaconf import OmegaConf
from rag_api.api.endpoints import documents, llm, users
from rag_api.db.database import create_tables


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def create_app(config_path: str = "src/rag_api/conf/config.yaml") -> FastAPI:
    """
    Create a FastAPI application with the specified configuration.
    Args:
        config_path: The path to the configuration file in yaml format

    Returns:
        FastAPI: The FastAPI application instance.
    """
    config = OmegaConf.load(config_path)

    app = FastAPI(
        title=config.api.title,
        description=config.api.description,
        version=config.api.version
    )

    app.include_router(documents.router)
    app.include_router(users.router)
    app.include_router(llm.router)

    return app


if __name__ == "__main__":
    config_path = "src/rag_api/conf/config.yaml"
    config = OmegaConf.load(config_path)
    create_tables()
    app = create_app(config_path)
    logger.info("Starting the API server...")
    uvicorn.run(app, host=config.api.host, port=config.api.port, log_level="info")
    logger.info("API server stopped.")

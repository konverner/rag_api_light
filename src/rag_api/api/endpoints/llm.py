import logging
from http.client import HTTPException
from hydra.utils import instantiate

from fastapi import APIRouter
from omegaconf import OmegaConf
from rag_api.api.schemas import QueryRequest, QueryResponse, Document
from rag_api.utils.exceptions import UserDoesNotExist
from rag_api.db import crud


# Load logging configuration with OmegaConf
logging_config = OmegaConf.to_container(
    OmegaConf.load("src/rag_api/conf/logging_config.yaml"),
    resolve=True
)
logging.config.dictConfig(logging_config)
logger = logging.getLogger(__name__)

cfg = OmegaConf.load("src/rag_api/conf/config.yaml")

router = APIRouter()
llm = instantiate(cfg.llm)
vector_store = instantiate(cfg.vector_store)

@router.post("/query", operation_id="QUERY")
async def query(request: QueryRequest) -> QueryResponse:

    username = request.username
    query = request.query

    logger.info(f"Received query: '{query}' from user {username}")

    # check if the user exists
    db_user = crud.read_user(username)
    if not db_user:
        raise UserDoesNotExist

    retriever_results = vector_store.query(query, 1, username)
    if not retriever_results["documents"]:
        raise HTTPException(status_code=404, detail="No relevant documents found.")

    document_text = retriever_results["documents"][0]
    document_name = retriever_results["metadatas"][0][0]["name"]

    response = llm.run(query, document_text, document_name)

    return QueryResponse(response=response, source=document_name)

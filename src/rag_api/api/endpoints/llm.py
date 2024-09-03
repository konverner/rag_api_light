import logging
from http.client import HTTPException

from fastapi import APIRouter
from omegaconf import OmegaConf
from rag_api.api.schemas import QueryRequest, QueryResponse
from rag_api.core.llm import FireworksLLM
from rag_api.core.vector_store import VectorStore
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
llm = FireworksLLM(model_name=cfg.llm.model_name, prompt_template=cfg.llm.prompt_template)
vector_store = VectorStore(embedding_model_name=cfg.retriever.model_name)

@router.post("/query/", operation_id="QUERY")
async def query(request: QueryRequest) -> QueryResponse:

    user = request.user
    query = request.query

    logger.info(f"Received query: '{query}' from user {user.name}")

    # check if the user exists
    db_user = crud.read_user(user.name)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found.")

    retriever_results = vector_store.query(query, 1, user.name)
    if not retriever_results["documents"]:
        raise HTTPException(status_code=404, detail="No relevant documents found.")

    document_text = retriever_results["documents"][0]
    document_name = retriever_results["metadatas"][0]
    response = llm.run(query, document_text, document_name)

    return {"response": response}

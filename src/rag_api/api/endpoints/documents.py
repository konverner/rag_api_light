import logging
from http.client import HTTPException
from io import BytesIO

from fastapi import APIRouter, File, UploadFile
from langchain_text_splitters import RecursiveCharacterTextSplitter
from omegaconf import OmegaConf
from rag_api.core.file_parser import FileParser
from rag_api.core.vector_store import VectorStore
from rag_api.utils.exceptions import UnsupportedFileTypeException

# Load logging configuration with OmegaConf
logging_config = OmegaConf.to_container(
    OmegaConf.load("src/rag_api/conf/logging_config.yaml"),
    resolve=True
)
logging.config.dictConfig(logging_config)
logger = logging.getLogger(__name__)

cfg = OmegaConf.load("src/rag_api/conf/config.yaml")

file_parser = FileParser(max_file_size_mb=10, allowed_file_types={"txt", "doc", "docx", "pdf"})
text_splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=10)
vector_store = VectorStore(embedding_model_name=cfg.retriever.model_name)

router = APIRouter()


@router.post("/upload_document")
async def load_document(
    file: UploadFile = File(...),
    username: str = "default_user"  # you can pass the username as a query parameter or from a dependency
):
    logger.info(
        f"Received document: {file.filename} with type {file.content_type} from user `{username}`"
    )
    try:
        uploaded_file = UploadFile(
            filename=file.filename,
            file=BytesIO(await file.read()),
            size=file.size,
            headers={"content-type": file.content_type}
        )
        document_text = file_parser.extract_content(uploaded_file)
        document_chunks = text_splitter.split_text(document_text)
        vector_store.upsert_documents(
            documents_text=document_chunks,
            documents_name=[file.filename]*len(document_chunks),
            collection_name=username
        )

        logger.info(f"Document {file.filename} has been upserted to ChromaDB")
        return {"message": "Document uploaded successfully."}
    except UnsupportedFileTypeException:
        logger.error(f"Document {file.filename} has NOT been upserted to ChromaDB")
        raise HTTPException(status_code=400, detail="Please upload a valid text file (txt, doc, docx, pdf).")


@router.post("/get_documents", operation_id="GET-DOCUMENTS")
async def get_docs(username: str):
    logger.info(f"Request to list documents for user `{username}`")
    documents = vector_store.get_document_names(username)
    if not documents:
        return {"message": "You have no uploaded documents."}
    else:
        return {"documents": documents}

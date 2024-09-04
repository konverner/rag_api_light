import logging
from http.client import HTTPException
from io import BytesIO

from fastapi import APIRouter, File, UploadFile
from omegaconf import OmegaConf
from hydra.utils import instantiate
from rag_api.utils.exceptions import UnsupportedFileTypeException


# Load logging configuration with OmegaConf
logging_config = OmegaConf.to_container(
    OmegaConf.load("src/rag_api/conf/logging_config.yaml"),
    resolve=True
)
logging.config.dictConfig(logging_config)
logger = logging.getLogger(__name__)

cfg = OmegaConf.load("src/rag_api/conf/config.yaml")

file_parser = instantiate(cfg.file_parser)
text_splitter = instantiate(cfg.text_splitter)
vector_store = instantiate(cfg.vector_store)

router = APIRouter()


@router.post("/upload_document/{username}", operation_id="UPLOAD-DOCUMENT")
async def upload_document(
    username: str,
    file: UploadFile = File(...)
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


@router.post("/get_documents/{username}", operation_id="GET-DOCUMENTS")
async def get_docs(username: str):
    logger.info(f"Request to list documents for user `{username}`")
    documents = vector_store.get_document_names(username)
    if not documents:
        return {"message": "You have no uploaded documents."}
    else:
        return {"documents": documents}

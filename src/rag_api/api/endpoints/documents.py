import logging
from datetime import datetime

from fastapi import APIRouter
from rag_api.db.crud import add_client
from rag_api.core.app import App
from omegaconf import OmegaConf

from src.rag_api.api.schemas import Endpoint1Response, Endpoint1Request
from src.rag_api.db.crud import read_client


# Load logging configuration with OmegaConf
logging_config = OmegaConf.to_container(
    OmegaConf.load("src/rag_api/conf/logging_config.yaml"),
    resolve=True
)
logging.config.dictConfig(logging_config)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/upload-document/")
async def load_document(
    file: UploadFile = File(...),
    username: str = "default_user"  # you can pass the username as a query parameter or from a dependency
):
    logger.info(
        f"[load_document] Received document: {file.filename} with type {file.content_type} from user {username}"
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


@router.get("/get-docs/")
async def get_docs(username: str):
    logger.info(f"[get_docs] Request to list documents for user {username}")
    documents = vector_store.get_document_names(username)
    if not documents:
        return {"message": "You have no uploaded documents."}
    else:
        return {"documents": documents}


@router.post("/ask-question/")
async def ask_question(question: str, username: str):
    logger.info(f"[ask_question] Received question: '{question}' from user {username}")
    retriever_results = vector_store.query(question, 1, username)
    if not retriever_results["documents"]:
        raise HTTPException(status_code=404, detail="No relevant documents found.")
    
    document_text = retriever_results["documents"][0]
    document_name = retriever_results["metadatas"][0]
    response = llm.run(question, document_text, document_name)
    
    log_message(username, question)  # Log the question
    add_user(username)  # Assuming you have the user data
    
    return {"response": response}

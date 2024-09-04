import logging

from fastapi import APIRouter, HTTPException
from omegaconf import OmegaConf
from rag_api.api.schemas import User
from rag_api.db import crud

# Load logging configuration with OmegaConf
logging_config = OmegaConf.to_container(
    OmegaConf.load("src/rag_api/conf/logging_config.yaml"),
    resolve=True
)
logging.config.dictConfig(logging_config)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/add_user", operation_id="ADD-USER")
async def add_user(user: User):
    db_user = crud.add_user(user.name)
    if db_user:
        return {"message": "User created successfully.", "user": db_user}
    else:
        raise HTTPException(status_code=400, detail="User creation failed.")

@router.post("/delete_user", operation_id="DELETE-USER")
async def delete_user(username: str):
    db_user = crud.read_user(username)
    if db_user:
        crud.delete_user(username)
        return {"message": "User deleted successfully."}
    else:
        raise HTTPException(status_code=404, detail="User not found.")

@router.get("/get_users", operation_id="GET-USERS")
async def get_users():
    users = crud.get_all_users()
    return {"users": users}
import logging

import sqlalchemy
from fastapi import APIRouter, HTTPException
from omegaconf import OmegaConf
from rag_api.api.schemas import User
from rag_api.db import crud
from rag_api.utils.exceptions import UserExistsException, UserDoesNotExist


# Load logging configuration with OmegaConf
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/add_user")
async def add_user(user: User):
    try:
        crud.add_user(user.name)
        logger.info(f"User `{user.name}` added successfully.")
    except Exception as e:
        if isinstance(e, sqlalchemy.exc.IntegrityError):
            logger.error(f"Error adding user: {e}")
            raise UserExistsException(user.name)


@router.post("/delete_user")
async def delete_user(username: str):
    db_user = crud.read_user(username)
    if db_user:
        crud.delete_user(username)
        logger.info(f"User `{username}` deleted successfully.")
        return {"message": f"User `{username}` deleted successfully."}
    else:
        logger.error(f"User `{username}` does not exist.")
        raise UserDoesNotExist


@router.get("/get_users")
async def get_users():
    users = crud.get_all_users()
    logger.info(f"Retrieved all users")
    return {"users": users}

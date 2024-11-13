# app/core/config.py

from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()





class Settings(BaseSettings):
    """
    This Settings class is designed to load and manage environment variables for an
    application using Pydantic's BaseSettings and python-dotenv

    write all your env variables here so you can access them easily.

    """


    OPENAI_API_KEY:str = os.environ.get("OPENAI_API_KEY")
    OPENAI_MODEL_NAME:str = os.environ.get("OPENAI_MODEL_NAME")
    PINECONE_API_KEY : str = os.environ.get("PINECONE_API_KEY")

    PG_HOST : str = os.environ.get("PG_HOST")
    PG_PORT : str = os.environ.get("PG_PORT")
    PG_USER : str = os.environ.get("PG_USER_NAME")
    PG_PASSWORD : str = os.environ.get("PG_PASSWORD")
    PG_DATABASE : str = os.environ.get("PG_DATABASE")


    class Config:
        env_file = ".env"

settings = Settings()



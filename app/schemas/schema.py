# use pydantic schemas for validation and serialization
from pydantic import BaseModel

class QueryInput(BaseModel):
    query: str
    collection_name: str
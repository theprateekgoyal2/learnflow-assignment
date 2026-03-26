"""Common response schemas shared across features."""

from pydantic import BaseModel


class MessageOut(BaseModel):
    message: str

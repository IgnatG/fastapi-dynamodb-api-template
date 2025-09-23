from pydantic import BaseModel


class TestMessage(BaseModel):
    """Simple test message model for template demonstration."""

    message: str

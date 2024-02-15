from pydantic import BaseModel


class Command(BaseModel):
    command: str
    silent: bool = False
    message: str | None = None

from pydantic import BaseModel


class Command(BaseModel):
    command: str
    silent: bool = False
    message: str | None = None

    def to_bash_string(self) -> str:
        suffix = f"|| {{ echo '{self.message}' ; exit 1; }}" if self.message else ""
        return f"{self.command} {' >/dev/null 2>&1' if self.silent else ''}{suffix}"

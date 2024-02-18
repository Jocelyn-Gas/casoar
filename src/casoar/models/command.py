from pydantic import BaseModel


class Command(BaseModel):
    command: str
    silent: bool = False
    message: str | None = None

    def to_bash_string(self) -> str:
        if self.silent and self.message is not None:
            suffix = f"|| {{ echo '{self.message}' ; exit 1; }}" if self.message else ""
            return f"{self.command} >/dev/null 2>&1 {suffix}"

        if self.silent:
            return f"{self.command} >/dev/null 2>&1"

        if self.message is not None:
            return f"""command_output=$({self.command} 2>&1)
            command_exit_code=$?
            if [ $command_exit_code -ne 0 ]; then
                echo '{self.message}'
                echo "$command_output"
                exit 1
            fi"""

        return self.command

from pathlib import Path
from typing import Generator, Tuple

from pydantic import BaseModel, ConfigDict, Field, field_serializer

from .command import Command


class Hooks(BaseModel):
    virtual_env: Path | None = None
    pre_commit: list[Command] = Field(alias="pre-commit", default_factory=list)
    commit_msg: list[Command] = Field(alias="commit-msg", default_factory=list)
    pre_push: list[Command] = Field(alias="pre-push", default_factory=list)

    model_config = ConfigDict(populate_by_name=True)

    @field_serializer("virtual_env", return_type=str)
    def serialize_virtualenv(virtual_env) -> str:
        return str(virtual_env)

    def __iter__(self) -> Generator[Tuple[str, list[Command]], None, None]:
        for hook_type, infos in self.model_fields.items():
            if hook_type != "virtual_env":
                yield infos.alias or hook_type, getattr(self, hook_type)

    @classmethod
    def get_sample(cls) -> "Hooks":
        return cls(
            virtual_env=Path(".venv"),
            pre_commit=[
                Command(
                    command="echo 'Hello, world!'",
                ),
            ],
        )

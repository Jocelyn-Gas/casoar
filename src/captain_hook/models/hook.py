from enum import Enum
from pathlib import Path

from pydantic import BaseModel

from .command import Command


class HookType(str, Enum):
    PRE_COMMIT = "pre-commit"
    COMMIT_MSG = "commit-msg"
    PRE_PUSH = "pre-push"


class Hook(BaseModel):
    hook_type: HookType
    commands: list[Command]


class HookConfig(BaseModel):
    hooks: list[Hook]
    virtualenv: Path | None = None

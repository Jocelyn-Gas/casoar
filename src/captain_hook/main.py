from pathlib import Path

import tomlkit
import yaml

from captain_hook.models import Command, Hooks
from captain_hook.writer import write_hooks


class NoConfigFoundError(Exception):
    pass


class TooManyConfigFilesError(Exception):
    pass


# if __name__ == "__main__":
#     config = Hooks(
#         virtual_env=".venv",
#         pre_commit=[
#             Command(
#                 command="echo 'Hello, world!'",
#                 silent=True,
#                 message="Hello, world! failed",
#             ),
#             Command(command="echo 'Hello, Universe!'"),
#         ],
#     )
#     with open("pyproject.toml", "r") as toml_file:
#         pyproject_data = toml.load(toml_file)

#     pyproject_data["tool"]["captain-hook"] = config.model_dump()
#     print(config.model_dump_json(indent=2))
#     with open("pyproject.toml", "w") as toml_file:
#         toml.dump(pyproject_data, toml_file)

#     write_hooks(config, hooks_folder=".git/hooks")
#     # for hook in config.hooks:
#     # write_hook(hook, config.virtualenv)


def read_config() -> Hooks:
    config_file = Path("./.captain-hook.yml")
    pyproject_file = Path("./pyproject.toml")
    pyproject_data = tomlkit.loads(pyproject_file.read_text())

    if "tool" not in pyproject_data.keys():
        pyproject_data.add("captain-hook")

    d = pyproject_data.get("tool")
    if d is None:
        raise NoConfigFoundError("No configuration found for captain-hook")

    if "captain-hook" in d.keys():
        if config_file.exists():
            raise TooManyConfigFilesError(
                "Both .captain-hook.yml and pyproject.toml have configuration for captain-hook"
            )
        return Hooks.model_validate(pyproject_data["tool"]["captain-hook"])

    if config_file.exists():
        return Hooks.model_validate(yaml.safe_load(config_file.read_text()))

    raise NoConfigFoundError("No configuration found for captain-hook")


def create_sample_config(path: Path):
    config = Hooks(
        virtual_env=".venv",
        pre_commit=[
            Command(
                command="echo 'Hello, world!'",
            ),
        ],
    )
    with open(path, "w") as config_file:
        yaml.safe_dump(
            config.model_dump(by_alias=True, exclude_unset=True), config_file
        )
    print(toml.dumps(config.model_dump()))

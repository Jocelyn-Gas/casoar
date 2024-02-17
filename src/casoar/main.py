from pathlib import Path

import tomlkit
import yaml

from casoar.models import Command, Hooks


class NoConfigFoundError(Exception):
    pass


class TooManyConfigFilesError(Exception):
    pass

def read_config() -> Hooks:
    config_file = Path("./.casoar.yml")
    pyproject_file = Path("./pyproject.toml")
    pyproject_data = tomlkit.loads(pyproject_file.read_text())

    if "tool" not in pyproject_data.keys():
        pyproject_data.add("casoar")

    d = pyproject_data.get("tool")
    if d is None:
        raise NoConfigFoundError("No configuration found for casoar")

    if "casoar" in d.keys():
        if config_file.exists():
            raise TooManyConfigFilesError(
                "Both .casoar.yml and pyproject.toml have configuration for casoar"
            )
        return Hooks.model_validate(pyproject_data["tool"]["casoar"])

    if config_file.exists():
        return Hooks.model_validate(yaml.safe_load(config_file.read_text()))

    raise NoConfigFoundError("No configuration found for casoar")


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
    print(tomlkit.dumps(config.model_dump()))

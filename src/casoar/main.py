from pathlib import Path

import tomlkit

from casoar.models import Hooks


class NoConfigFoundError(Exception):
    pass


class TooManyConfigFilesError(Exception):
    pass


def read_config() -> Hooks:
    config_file = Path("./.casoar.toml")
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
                "Both .casoar.toml and pyproject.toml have configuration for casoar"
            )
        return Hooks.model_validate(pyproject_data["tool"]["casoar"])

    if config_file.exists():
        return Hooks.model_validate(tomlkit.loads(config_file.read_text()))

    raise NoConfigFoundError("No configuration found for casoar")

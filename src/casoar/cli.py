from enum import Enum
from pathlib import Path
from typing import Annotated

import tomlkit
from rich import print
from rich.progress import Progress, SpinnerColumn, TextColumn
from typer import Argument, Option, Typer

from casoar.main import (
    NoConfigFoundError,
    TooManyConfigFilesError,
    read_config,
)
from casoar.models import Hooks
from casoar.writer import write_hooks

app = Typer()


class ConfigFileName(str, Enum):
    PYPROJECT = "pyproject.toml"
    CUSTOM = ".casoar.toml"


@app.command()
def install():
    try:
        config = read_config()
        write_hooks(config, hooks_folder=".git/hooks")
    except NoConfigFoundError:
        print("[red]Error: No configuration found for [b]casoar [/red]")
        print(
            "[yellow]Hint:[/yellow] Run [green]casoar init[/green] to create a configuration file"
        )
    except TooManyConfigFilesError:
        print(
            "[red]Error: Both .casoar.yml and pyproject.toml have configuration for casoar[/red]"
        )
        print(
            "[yellow]Hint:[/yellow] Remove one of the configuration files to fix this error"
        )


@app.command()
def init(
    config_file: Annotated[ConfigFileName, Argument()] = ConfigFileName.PYPROJECT.value,
    force: Annotated[bool, Option("--force")] = False,
) -> None:
    pyproject_path = Path(ConfigFileName.PYPROJECT.value)
    custom_config_path = Path(ConfigFileName.CUSTOM.value)

    if custom_config_path.exists():
        if not force:
            print(
                f"[red]Error: Configuration file {custom_config_path} already exists. To bypass this error, use '--force' option[/red]"
            )
            raise SystemExit(1)

        else:
            custom_config_path.unlink()

    pyproject_data = {}
    if pyproject_path.exists():
        pyproject_data = tomlkit.loads(pyproject_path.read_text())

    if "tool" in pyproject_data and "casoar" in pyproject_data["tool"]:
        if not force:
            print(
                "[red]Error: Configuration for casoar already exists in pyproject.toml[/red]"
            )
            raise SystemExit(1)
        else:
            del pyproject_data["tool"]["casoar"]
            with open(pyproject_path, "wt") as file:
                tomlkit.dump(pyproject_data, file)

    config = Hooks.get_sample()

    match config_file:
        case ConfigFileName.PYPROJECT:
            if not pyproject_path.exists():
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                ) as progress:
                    task = progress.add_task(
                        description="Creating pyproject.toml file...", total=1
                    )
                    pyproject_path.touch()
                    progress.update(
                        task, completed=1, description="Creating pyproject.toml file ✅"
                    )

            if "tool" not in pyproject_data:
                pyproject_data["tool"] = tomlkit.table()

            if "casoar" in pyproject_data["tool"] and not force:
                print(
                    f"[red]Error: Configuration for casoar already exists in {config_file.value}[/red]"
                )
                raise SystemExit(1)
            sample = Hooks.get_sample()
            pyproject_data["tool"]["casoar"] = tomlkit.table()
            for k, v in sample.model_dump(by_alias=True, exclude_unset=True).items():
                pyproject_data["tool"]["casoar"][k] = v

            # pyproject_data.get("tool")["casoar"].add("virtual_env", ".venv")

            with open(pyproject_path, "wt") as file:
                tomlkit.dump(pyproject_data, file)
        case ConfigFileName.CUSTOM:
            with open(custom_config_path, "w") as file:
                tomlkit.dump(config.model_dump(exclude_unset=True, by_alias=True), file)


if __name__ == "__main__":
    app()

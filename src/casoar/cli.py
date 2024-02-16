from enum import Enum
from pathlib import Path
from typing import Annotated

import tomlkit
import yaml
from rich import print
from rich.progress import Progress, SpinnerColumn, TextColumn
from typer import Argument, Option, Typer

from casoar.main import (
    NoConfigFoundError,
    TooManyConfigFilesError,
    create_sample_config,
    read_config,
)
from casoar.models import Hooks
from casoar.writer import write_hooks

app = Typer()


class ConfigFileName(str, Enum):
    TOML = "pyproject.toml"
    YAML = ".captain-hook.yml"


@app.command()
def install():
    try:
        config = read_config()
        write_hooks(config, hooks_folder=".git/hooks")
    except NoConfigFoundError:
        print("[red]Error: No configuration found for [b]captain-hook [/red]")
        print(
            "[yellow]Hint:[/yellow] Run [green]captain-hook init[/green] to create a configuration file"
        )
    except TooManyConfigFilesError:
        print(
            "[red]Error: Both .captain-hook.yml and pyproject.toml have configuration for captain-hook[/red]"
        )
        print(
            "[yellow]Hint:[/yellow] Remove one of the configuration files to fix this error"
        )


@app.command()
def init(
    config_file: Annotated[ConfigFileName, Argument()] = ConfigFileName.YAML.value,
    force: Annotated[bool, Option("--force")] = False,
) -> None:
    pyproject_path = Path(ConfigFileName.TOML.value)
    custom_config_path = Path(ConfigFileName.YAML.value)

    if custom_config_path.exists() and not force:
        print(
            f"[red]Error: Configuration file {custom_config_path} already exists. To bypass this error, use '--force' option[/red]"
        )
        raise SystemExit(1)

    elif custom_config_path.exists and force:
        custom_config_path.unlink()
    config = Hooks.get_sample()

    match config_file:
        case ConfigFileName.TOML:
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
            pyproject_data = tomlkit.loads(pyproject_path.read_text())

            if "tool" not in pyproject_data:
                pyproject_data["tool"] = tomlkit.table()

            if "captain-hook" in pyproject_data["tool"]:
                print(
                    f"[red]Error: Configuration for captain-hook already exists in {config_file}[/red]"
                )
                raise SystemExit(1)
            sample = Hooks.get_sample()
            pyproject_data["tool"]["captain-hook"] = tomlkit.table()
            for k , v in sample.dict(by_alias=True, exclude_unset=True).items():
                pyproject_data["tool"]["captain-hook"][k] = v

            # pyproject_data.get("tool")["captain-hook"].add("virtual_env", ".venv")

            with open(pyproject_path, "wt") as file:
                tomlkit.dump(pyproject_data, file)
        case ConfigFileName.YAML:
            with open(custom_config_path, "w") as file:
                yaml.safe_dump(
                    config.model_dump(by_alias=True, exclude_unset=True),
                    file,
                )


if __name__ == "__main__":
    app()

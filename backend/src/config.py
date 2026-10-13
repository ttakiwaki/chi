# config.py
import dataclasses
import tomllib
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
path = BASE_DIR.parent / "./chi.config.toml"


def load_settings(path):
    with open(path, "rb") as toml_file:
        config = tomllib.load(toml_file)
    return Settings(
        lrclib=config["lrclib"],
        preview=config["preview"],
        host=config["host"],
        port=config["port"],
        demucs_model=config["demucs_model"],
        data_dir=Path(path).parent / config["data_dir"],
    )


@dataclasses.dataclass(frozen=True)
class Settings:
    # Network Settings
    lrclib: str
    preview: str
    host: str
    port: int

    # Preferences
    demucs_model: str

    # Paths
    data_dir: Path


print(load_settings(path=path).data_dir)

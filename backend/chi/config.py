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

    @property
    def song_dir(self) -> Path:
        return self.data_dir / "songs"

    @property
    def tmp_dir(self) -> Path:
        return self.data_dir / "tmp"

    @property
    def user_path(self) -> Path:
        return self.data_dir / "user.json"

    @property
    def sessions_path(self) -> Path:
        return self.data_dir / "sessions.jsonl"


if __name__ == "__main__":
    s = load_settings(path)
    print(s.sessions_path)
    print(s.song_dir)

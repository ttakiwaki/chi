# songstore.py
import copy
import json
import os
import re
import tempfile
import threading
import unicodedata
from datetime import UTC, datetime
from pathlib import Path


# Folder Name Helper Functions
def folder_name(title: str) -> str:
    legal_title = (
        unicodedata.normalize("NFC", re.sub(r'[\\/:*?"<>|\x00-\x1f]', "_", title))
        .encode("utf-8")[:200]
        .decode("utf-8", errors="ignore")
        .rstrip(". ")
    )
    return legal_title or "Untitled"


def unique_folder_name(title: str, artist: str, existing: set[str]) -> str:
    taken = {n.casefold() for n in existing}

    candidate = (
        folder_name(f"{title.strip()} - {artist.strip()}")
        if artist
        else folder_name(f"{title.strip()}")
    )
    if candidate.casefold() not in taken:
        return candidate

    index = 2
    index_candidate = (
        f"{folder_name(f'{title.strip()} - {artist.strip()}')} ({index})"
        if artist
        else f"{folder_name(f'{title.strip()}')} ({index})"
    )
    while True:
        if index_candidate.casefold() not in taken:
            return index_candidate
        index += 1


# Read / Writing to State Helper Functions
class StateError(Exception):
    pass


def _utc_now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_state(folder):
    path = Path(folder) / "state.json"

    try:
        with open(path, "r", encoding="utf8") as file:
            state = json.load(file)
    except OSError as e:
        raise StateError(f"OS Error at {path}") from e
    except json.JSONDecodeError as e:
        raise StateError(f"JSONDecode Error at {path}") from e
    if not isinstance(state, dict):
        raise StateError(f"State is not type: dict at {path}")
    elif state.get("version") != 1:
        raise StateError(f"Unknown version number at {path}")
    return state


def _write_state(folder, state):
    state_path = Path(folder) / "state.json"
    tmp_path = Path(folder) / "state.json.tmp"

    try:
        state["updated_at"] = _utc_now()
        with open(tmp_path, "w", encoding="utf8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, state_path)
    finally:
        tmp_path.unlink(missing_ok=True)


def new_state(
    track_hash: str,
    original_filename: str,
    original_ext: str,
    kind: str = "full",
    demucs_model: str = "htdemucs",
) -> dict:
    time_now = _utc_now()
    state = {
        "version": 1,
        "id": track_hash,
        "hash": track_hash,
        "original_filename": original_filename,
        "original_ext": original_ext,
        "kind": kind,
        "demucs_model": demucs_model,
        "stages": {
            "separation": {
                "state": "pending",
                "skipped": kind == "instrumental",
                "error": None,
                "updated_at": time_now,
            },
            "lyrics": {
                "state": "pending",
                "reason": None,
                "source": "lrclib",
                "lrclib_id": None,
                "chosen_by": "auto",
                "synced": None,
                "updated_at": time_now,
            },
        },
        "created_at": time_now,
        "updated_at": time_now,
    }
    return state


# Updating State Functions
_lock = threading.Lock()


def _update_state(folder, fn):
    with _lock:
        state = _read_state(folder)
        fn(state)
        _write_state(folder, state)
        return copy.deepcopy(state)


def set_stage(folder, stage, **fields):
    def apply(state):
        if stage not in ("separation", "lyrics"):
            raise ValueError(f"Passed stage {stage} is not a valid stage.")
        stage_data = state["stages"][stage]
        stage_data.update(fields)
        stage_data["updated_at"] = _utc_now()

    return _update_state(folder, apply)


if __name__ == "__main__":
    print(unique_folder_name("私がオバさんになっても", "森高千里", set()))  # Song

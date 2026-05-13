from __future__ import annotations

import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
PROJECT_ROOT = SKILL_DIR.parents[2]
DATA_DIR = PROJECT_ROOT / ".invoice-data"


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def load_contractor() -> dict[str, Any]:
    return load_json(DATA_DIR / "contractor.json")


def load_accounts() -> dict[str, Any]:
    return load_json(DATA_DIR / "accounts.json")["accounts"]


def load_client(client_id: str) -> dict[str, Any]:
    return load_json(DATA_DIR / "clients" / f"{client_id}.json")


def require_confirmed_account(accounts: dict[str, Any], account_id: str) -> dict[str, Any]:
    account = accounts.get(account_id)
    if not account:
        raise SystemExit(f"Unknown account id: {account_id}")
    if not account.get("confirmed"):
        raise SystemExit(f"Refusing to use unconfirmed account: {account_id}")
    return account


def run_json(cmd: list[str]) -> dict[str, Any]:
    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    if not result.stdout.strip():
        return {}
    return json.loads(result.stdout)


def run_text(cmd: list[str]) -> str:
    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    return result.stdout


def timestamp_slug() -> str:
    return datetime.now().strftime("%Y-%m-%d-%H%M%S")


def clean_filename(value: str) -> str:
    keep = []
    for char in value:
        if char.isalnum() or char in (" ", "-", "_", ".", "#"):
            keep.append(char)
        else:
            keep.append("-")
    return " ".join("".join(keep).split()).strip()

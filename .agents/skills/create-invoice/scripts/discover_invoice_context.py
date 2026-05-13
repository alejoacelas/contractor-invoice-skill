# /// script
# requires-python = ">=3.11"
# ///

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from _common import DATA_DIR, run_json, timestamp_slug, write_json


def gmail_search(query: str, max_results: int, account: str | None) -> dict[str, Any]:
    cmd = ["gog", "gmail", "search", "--json", "--max", str(max_results)]
    if account:
        cmd.extend(["--account", account])
    cmd.append(query)
    return run_json(cmd)


def gmail_thread_get(
    thread_id: str,
    out_dir: Path,
    download: bool,
    account: str | None,
) -> dict[str, Any]:
    cmd = ["gog", "gmail", "thread", "get", "--json", "--full"]
    if download:
        out_dir.mkdir(parents=True, exist_ok=True)
        cmd.extend(["--download", "--out-dir", str(out_dir)])
    if account:
        cmd.extend(["--account", account])
    cmd.append(thread_id)
    return run_json(cmd)


def drive_search(query: str, max_results: int, account: str | None) -> dict[str, Any]:
    cmd = ["gog", "drive", "search", "--json", "--max", str(max_results)]
    if account:
        cmd.extend(["--account", account])
    cmd.append(query)
    return run_json(cmd)


def main() -> None:
    parser = argparse.ArgumentParser(description="Discover invoice context in Gmail and Drive.")
    parser.add_argument("--client", default="general", help="Client id for output naming.")
    parser.add_argument("--gmail-query", help="Gmail query to search.")
    parser.add_argument("--drive-query", help="Drive query to search.")
    parser.add_argument("--thread-id", help="Specific Gmail thread to fetch.")
    parser.add_argument("--download", action="store_true", help="Download Gmail attachments.")
    parser.add_argument("--max", type=int, default=10, help="Max search results per source.")
    parser.add_argument("--account", help="Google account for gog commands.")
    parser.add_argument("--out-dir", type=Path, help="Attachment output directory.")
    args = parser.parse_args()

    attachments_dir = args.out_dir or (
        DATA_DIR / "outputs" / "discovered" / args.client / timestamp_slug()
    )
    result: dict[str, Any] = {
        "client": args.client,
        "gmail_query": args.gmail_query,
        "drive_query": args.drive_query,
        "thread_id": args.thread_id,
        "downloaded_attachments_dir": str(attachments_dir) if args.download else None,
        "gmail_search": None,
        "gmail_thread": None,
        "drive_search": None,
    }

    if args.gmail_query:
        result["gmail_search"] = gmail_search(args.gmail_query, args.max, args.account)

    thread_id = args.thread_id
    if not thread_id and result["gmail_search"]:
        threads = result["gmail_search"].get("threads") or []
        if threads:
            thread_id = threads[0].get("id")

    if thread_id:
        result["gmail_thread"] = gmail_thread_get(
            thread_id,
            attachments_dir,
            args.download,
            args.account,
        )

    if args.drive_query:
        result["drive_search"] = drive_search(args.drive_query, args.max, args.account)

    output_path = DATA_DIR / "jobs" / f"{timestamp_slug()}-discover-{args.client}.json"
    write_json(output_path, result)
    print(output_path)


if __name__ == "__main__":
    main()

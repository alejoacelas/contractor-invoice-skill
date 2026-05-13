# /// script
# requires-python = ">=3.11"
# ///

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

from _common import load_client, load_contractor


def default_body(contractor: dict, client: dict, attachments: list[Path]) -> str:
    suggested_to = ", ".join(client.get("default_to", [])) or "(not configured)"
    suggested_cc = ", ".join(client.get("default_cc", [])) or "(none)"
    attachment_lines = "\n".join(f"- {path.name}" for path in attachments)
    return (
        f"Suggested To: {suggested_to}\n"
        f"Suggested Cc: {suggested_cc}\n\n"
        "Hi,\n\n"
        "Attached are the invoice files.\n\n"
        f"{attachment_lines}\n\n"
        "Best regards,\n"
        f"{contractor['display_name']}\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Send a guarded invoice test email.")
    parser.add_argument("--client", required=True)
    parser.add_argument("--subject", help="Email subject.")
    parser.add_argument("--body", help="Plain text email body.")
    parser.add_argument("--body-file", type=Path, help="Plain text body file.")
    parser.add_argument("--attach", action="append", default=[], type=Path)
    parser.add_argument("--to", help="Override recipient.")
    parser.add_argument("--cc", help="CC recipients.")
    parser.add_argument("--allow-external", action="store_true", help="Allow non-test recipient.")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    contractor = load_contractor()
    client = load_client(args.client)
    attachments = [path.resolve() for path in args.attach]
    for path in attachments:
        if not path.exists():
            raise SystemExit(f"Missing attachment: {path}")

    test_to = client.get("delivery", {}).get("send_test_to") or contractor["test_email"]
    to = args.to or test_to
    if not args.allow_external and to != test_to and to != contractor["test_email"]:
        raise SystemExit("Refusing external send without --allow-external.")

    subject = args.subject or client.get("delivery", {}).get("default_subject") or "Invoice"
    if args.body_file:
        body = args.body_file.read_text(encoding="utf-8")
    else:
        body = args.body or default_body(contractor, client, attachments)

    cmd = [
        "gog",
        "gmail",
        "send",
        "--account",
        contractor["email"],
        "--to",
        to,
        "--subject",
        subject,
        "--body",
        body,
    ]
    if args.cc:
        cmd.extend(["--cc", args.cc])
    for attachment in attachments:
        cmd.extend(["--attach", str(attachment)])

    if args.dry_run:
        print(" ".join(cmd[:8] + ["..."]))
        print(body)
        return

    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    print(result.stdout)


if __name__ == "__main__":
    main()

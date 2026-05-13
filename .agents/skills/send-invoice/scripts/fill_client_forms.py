# /// script
# requires-python = ">=3.11"
# ///

from __future__ import annotations

import argparse
import json

from _common import load_client


def main() -> None:
    parser = argparse.ArgumentParser(description="Client-specific invoice form automation entry point.")
    parser.add_argument("--client", required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    client = load_client(args.client)
    forms = client.get("forms", [])
    configured = [form for form in forms if form.get("status") == "configured"]
    if not configured:
        print(json.dumps({"ok": False, "reason": "No configured form profile.", "forms": forms}, indent=2))
        raise SystemExit(2)

    if args.dry_run:
        print(json.dumps({"ok": True, "forms": configured, "action": "dry-run"}, indent=2))
        return

    raise SystemExit("Form profile exists, but browser automation has not been implemented for this client.")


if __name__ == "__main__":
    main()

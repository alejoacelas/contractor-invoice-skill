# /// script
# requires-python = ">=3.11"
# ///

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


def run_text(cmd: list[str]) -> str:
    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    return result.stdout


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate text and previews for an invoice PDF.")
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--expect", action="append", default=[], help="Required substring in PDF text.")
    parser.add_argument("--preview-dir", type=Path, help="Render a PNG preview into this directory.")
    parser.add_argument("--preview-prefix", help="Preview filename prefix.")
    args = parser.parse_args()

    text = run_text(["pdftotext", str(args.pdf), "-"])
    info = run_text(["pdfinfo", str(args.pdf)])
    missing = [expected for expected in args.expect if expected not in text]
    previews: list[str] = []

    if args.preview_dir:
        args.preview_dir.mkdir(parents=True, exist_ok=True)
        prefix = args.preview_prefix or args.pdf.stem
        output_prefix = args.preview_dir / prefix
        subprocess.run(
            ["pdftoppm", "-png", "-r", "150", str(args.pdf), str(output_prefix)],
            check=True,
            capture_output=True,
            text=True,
        )
        previews = [str(path) for path in sorted(args.preview_dir.glob(f"{prefix}-*.png"))]

    result = {
        "pdf": str(args.pdf),
        "ok": not missing,
        "missing": missing,
        "previews": previews,
        "text_chars": len(text),
        "info": info,
    }
    print(json.dumps(result, indent=2))
    if missing:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

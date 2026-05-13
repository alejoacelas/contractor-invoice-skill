# Repository Guardrails

This repository is intended to be public. Treat privacy preservation as a hard requirement.

## Never Commit

- `.invoice-data/`
- `sent/`
- `work/`
- `notes/`
- generated invoices, PDFs, previews, raw Gmail/Drive downloads, or form screenshots
- real bank details, account numbers, sort codes, routing numbers, IBANs, tax IDs, client payment history, or private invoice email threads

Use `examples/invoice-data/` for documentation and tests. Keep those values fake.

## Before Committing

Run:

```bash
git status --short --ignored
git diff --cached --name-only
```

Check that only public-safe docs, scripts, examples, and skill files are staged.

Search staged text for sensitive terms when changing examples or docs:

```bash
git diff --cached -- ':(exclude)*.pdf' | rg -i 'account number|sort code|routing|iban|wise|bank address|tax id|ssn'
```

If a real invoice PDF or private data file is staged, stop and unstage it.

## Python

Use `uv run` for all Python script execution.

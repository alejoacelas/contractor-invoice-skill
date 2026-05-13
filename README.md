# Contractor Invoice Skill

Public-safe Codex skill for creating contractor invoices from local client profiles, validating generated PDFs, and preparing forward-ready test emails.

## Layout

- `.agents/skills/send-invoice/` - repo-local Codex skill for discovering invoice context, rendering invoices, validating PDFs, and preparing test emails.
- `examples/invoice-data/` - fake example runtime config. Copy this to `.invoice-data/` and replace values locally.
- `.invoice-data/` - private runtime config, bank details, client profiles, and generated drafts. Ignored by git.
- `sent/` - local final invoice PDFs grouped by recipient or client. Ignored by git.
- `work/` - raw downloads, previews, and scratch files. Ignored by git.

## Setup

```bash
cp -R examples/invoice-data .invoice-data
```

Then edit `.invoice-data/contractor.json`, `.invoice-data/accounts.json`, and `.invoice-data/clients/*.json` with your real local details.

## Privacy Model

The repo tracks reusable skill code and fake examples only. Real invoice data lives beside the repo as ignored local state.

Do not commit generated invoices, raw Gmail/Drive downloads, previews, or real payment details.

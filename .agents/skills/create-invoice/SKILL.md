---
name: create-invoice
description: Create, discover, render, validate, organize, and prepare contractor invoices using local invoice profiles. Use when the user asks to create invoices, reuse invoice templates, scan Gmail or Drive for invoice context, prepare invoice emails, validate generated invoice PDFs, or submit client-specific invoice forms.
---

# Create Invoice

## Core Rule

Treat invoice creation as a stateful workflow. Reuse local config from `.invoice-data/`, but confirm any missing or unconfirmed payment details before using them. Send only test emails to the contractor by default; direct external sends require an explicit current-turn instruction.

## Data

Runtime data is stored at the repository root:

- `.invoice-data/contractor.json`
- `.invoice-data/accounts.json`
- `.invoice-data/clients/<client-id>.json`
- `.invoice-data/jobs/`
- `.invoice-data/outputs/`

Read `references/data-schema.md` when adding or changing stored data.

## Workflow

Read `references/workflow.md` for the full sequence. The usual flow is:

1. Discover prior context from Gmail/Drive when setting up a client or resolving ambiguity.
2. Ask for only missing high-risk fields: client, month, hours, description, invoice number, invoice date, account, external send permission, and form submission intent.
3. Render invoice PDFs.
4. Validate extracted PDF text and preview image before sending.
5. Send a forward-ready test email to the contractor.
6. If requested, use client-specific form automation only after the form profile is configured.

## Tools

Before the first manual use of a `gog` subcommand in a conversation, run its `--help` command. The scripts call `gog` with structured JSON where possible.

Use these scripts from the skill directory:

- `scripts/discover_invoice_context.py`: search Gmail/Drive, download email attachments, and save normalized context.
- `scripts/render_invoice.py`: render one invoice PDF from client/account config and explicit invoice fields.
- `scripts/validate_invoice.py`: extract PDF text, check expected values, and optionally render a PNG preview.
- `scripts/send_test_email.py`: send a guarded test email. Default recipient is the contractor test email.
- `scripts/fill_client_forms.py`: fail-closed entry point for client-specific form automation.

Invoke scripts with `uv run`.

## Sensible Defaults

- Use `sent/<client-folder>/` for final PDFs the contractor has sent or is ready to forward.
- Use `.invoice-data/outputs/` for drafts and intermediate generated files.
- Use one invoice per month when a client asks for separate months.
- Use the client's configured `default_due_days` when no due date is specified.
- Do not advance invoice number state automatically unless the user confirms the invoice was sent externally.
- Prefer confirmed bank accounts; refuse unconfirmed account profiles.
- Include suggested forwarding recipients in test emails.

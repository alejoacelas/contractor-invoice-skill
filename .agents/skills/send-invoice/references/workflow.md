# Invoice Workflow

## Setup

1. Search Gmail and Drive for prior invoice context.
2. Download source invoice PDFs and attachments.
3. Extract the surrounding email instructions, recipients, CCs, form requirements, and invoice corrections.
4. Store confirmed reusable facts in `.invoice-data/`.
5. Store source invoice/template artifacts under `.invoice-data/templates/<client-id>/` because they may contain private payment details.

## Generation

1. Load contractor, account, and client config.
2. Ask for missing fields: work period, hours, work description, invoice number, invoice date, and account if there is ambiguity.
3. Use one invoice per month when the client requires separate months.
4. Keep invoice dates inside the service month when the client requires that.
5. Render PDFs into `sent/<client-folder>/` or `.invoice-data/outputs/`.

## Validation

Run PDF text extraction and check:

- invoice number
- invoice date
- work period
- hours
- rate
- balance due
- bank account details

Render a PNG preview and inspect for collisions before sending.

## Delivery

Default to sending a test email only to the contractor's test email. The body should be readable by the real recipient and include a short forwarding note with suggested `To` and `Cc` values.

Never send directly to an external client unless the user explicitly requests it in the current turn.

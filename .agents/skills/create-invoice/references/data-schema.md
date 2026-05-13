# Invoice Data Schema

Runtime data lives at the repository root in `.invoice-data/`.

## contractor.json

- `display_name`: Name to use in email text.
- `legal_name`: Name to use for bank account and invoice identity.
- `email`: Sender account.
- `test_email`: Default recipient for generated test emails.

## accounts.json

`accounts` is keyed by a stable account id such as `wise_gbp`.

Required fields for a usable account:

- `confirmed: true`
- `currency`
- `currency_symbol`
- `account_holder_name`
- account-specific payment fields, such as `sort_code` and `account_number`

Do not use an account with `confirmed: false` on an invoice.

## clients/<client-id>.json

Required fields:

- `display_name`
- `folder_name`
- `bill_to`
- `default_to`
- `default_account`
- `default_rate`
- `unit`
- `date_rules.default_due_days`
- `delivery.send_test_to`

Useful optional fields:

- `default_cc`
- `default_work_description`
- `invoice_number`
- `source_context`
- `forms`

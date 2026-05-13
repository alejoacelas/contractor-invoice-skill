# /// script
# requires-python = ">=3.11"
# dependencies = ["reportlab>=4.2"]
# ///

from __future__ import annotations

import argparse
import calendar
from datetime import date, datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Paragraph, Table, TableStyle

from _common import (
    PROJECT_ROOT,
    clean_filename,
    load_accounts,
    load_client,
    load_contractor,
    require_confirmed_account,
    timestamp_slug,
    write_json,
)


def ordinal(value: int) -> str:
    if 10 <= value % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(value % 10, "th")
    return f"{value}{suffix}"


def human_date(value: date) -> str:
    return f"{value.strftime('%B')} {ordinal(value.day)}, {value.year}"


def parse_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def parse_month(value: str) -> tuple[int, int]:
    parsed = datetime.strptime(value, "%Y-%m")
    return parsed.year, parsed.month


def default_invoice_date(year: int, month: int) -> date:
    today = date.today()
    if today.year == year and today.month == month:
        return today
    last_day = calendar.monthrange(year, month)[1]
    return date(year, month, last_day)


def default_work_period(year: int, month: int, invoice_date: date) -> str:
    month_name = date(year, month, 1).strftime("%b")
    last_day = calendar.monthrange(year, month)[1]
    end_day = invoice_date.day if (invoice_date.year, invoice_date.month) == (year, month) else last_day
    return f"1 {month_name} - {end_day} {month_name}"


def money(value: Decimal, symbol: str) -> str:
    quantized = value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return f"{symbol}{quantized:.2f}"


def draw_wrapped(canvas: Canvas, text: str, x: float, y: float, width: float, style: ParagraphStyle) -> float:
    paragraph = Paragraph(text, style)
    _, height = paragraph.wrap(width, 1000)
    paragraph.drawOn(canvas, x, y - height)
    return y - height


def draw_right_label(canvas: Canvas, label: str, value: str, y: float) -> None:
    label_x = 405
    value_x = 560
    canvas.setFont("Helvetica-Bold", 9)
    canvas.drawString(label_x, y, label)
    canvas.setFont("Helvetica", 9)
    value_width = stringWidth(value, "Helvetica", 9)
    canvas.drawString(value_x - value_width, y, value)


def render_pdf(spec: dict[str, Any], output_path: Path) -> None:
    client = spec["client"]
    account = spec["account"]
    canvas = Canvas(str(output_path), pagesize=letter)
    canvas.setTitle(spec["title"])
    width, height = letter

    left = 0.75 * inch
    right = width - 0.75 * inch
    top = height - 0.75 * inch

    canvas.setFont("Helvetica-Bold", 24)
    canvas.drawString(left, top, "INVOICE")

    normal = ParagraphStyle(
        "normal",
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=colors.black,
    )
    small = ParagraphStyle("small", parent=normal, fontSize=8, leading=11)

    y = top - 42
    canvas.setFont("Helvetica-Bold", 9)
    canvas.drawString(left, y, "INVOICE TO:")
    y -= 15
    draw_wrapped(canvas, "<br/>".join(client["bill_to"]), left, y, 240, normal)

    meta_y = top - 42
    draw_right_label(canvas, "Invoice Number", spec["invoice_number"], meta_y)
    draw_right_label(canvas, "Date of Invoice", human_date(spec["invoice_date"]), meta_y - 18)
    draw_right_label(canvas, "Due Date", human_date(spec["due_date"]), meta_y - 36)
    draw_right_label(canvas, "Unit:", client["unit"], meta_y - 54)
    draw_right_label(canvas, "Week", spec["work_period"], meta_y - 72)

    table_data = [
        ["DESCRIPTION OF WORK UNDERTAKEN", "HOURS"],
        [Paragraph(spec["description"], normal), spec["hours_display"]],
        ["TOTAL HOURS", spec["hours_display"]],
        ["AGREED RATE", money(spec["rate"], account["currency_symbol"])],
        ["OTHER", ""],
        ["BALANCE DUE", money(spec["balance_due"], account["currency_symbol"])],
    ]
    table = Table(table_data, colWidths=[350, 100], rowHeights=[28, 64, 28, 28, 28, 34])
    table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 2), (-1, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("ALIGN", (1, 0), (1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LINEABOVE", (0, 0), (-1, 0), 1.0, colors.black),
                ("LINEBELOW", (0, 0), (-1, 0), 1.0, colors.black),
                ("LINEBELOW", (0, 1), (-1, -1), 0.5, colors.HexColor("#b5b5b5")),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f2f2f2")),
                ("BACKGROUND", (0, 5), (-1, 5), colors.HexColor("#f2f2f2")),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    table.wrapOn(canvas, right - left, 500)
    table.drawOn(canvas, left, 365)

    notes_y = 330
    canvas.setFont("Helvetica-Bold", 9)
    canvas.drawString(left, notes_y, "Notes:")
    notes_y -= 16
    bank_lines = [
        "Bank account",
        f"Account Holder Name: {account['account_holder_name']}",
        f"Receiving currency: {account['receiving_currency']}",
    ]
    if account.get("sort_code"):
        bank_lines.append(f"Sort code: {account['sort_code']}")
    if account.get("account_number"):
        bank_lines.append(f"Account number: {account['account_number']}")
    if account.get("bank_address"):
        bank_lines.append(f"Bank address: {account['bank_address']}")
    draw_wrapped(canvas, "<br/>".join(bank_lines), left, notes_y, right - left, small)
    canvas.save()


def main() -> None:
    parser = argparse.ArgumentParser(description="Render a contractor invoice PDF.")
    parser.add_argument("--client", required=True, help="Client id in .invoice-data/clients.")
    parser.add_argument("--month", required=True, help="Service month as YYYY-MM.")
    parser.add_argument("--hours", required=True, type=Decimal)
    parser.add_argument("--description", help="Description of work.")
    parser.add_argument("--invoice-number", help="Invoice number, e.g. #008.")
    parser.add_argument("--use-next-number", action="store_true")
    parser.add_argument("--invoice-date", help="Invoice date as YYYY-MM-DD.")
    parser.add_argument("--due-date", help="Due date as YYYY-MM-DD.")
    parser.add_argument("--work-period", help="Human-readable work period.")
    parser.add_argument("--rate", type=Decimal, help="Hourly rate.")
    parser.add_argument("--account", help="Account id from accounts.json.")
    parser.add_argument("--out", type=Path, help="Output PDF path.")
    parser.add_argument("--record", action="store_true", help="Write a job record.")
    args = parser.parse_args()

    contractor = load_contractor()
    client = load_client(args.client)
    accounts = load_accounts()
    account_id = args.account or client["default_account"]
    account = require_confirmed_account(accounts, account_id)

    year, month = parse_month(args.month)
    invoice_date = parse_date(args.invoice_date) if args.invoice_date else default_invoice_date(year, month)
    due_days = int(client["date_rules"]["default_due_days"])
    due_date = parse_date(args.due_date) if args.due_date else invoice_date + timedelta(days=due_days)

    if client["date_rules"].get("invoice_date_within_work_month"):
        if (invoice_date.year, invoice_date.month) != (year, month):
            raise SystemExit("Invoice date must be inside the service month for this client.")

    invoice_number = args.invoice_number
    if args.use_next_number:
        invoice_number = client.get("invoice_number", {}).get("next")
    if not invoice_number:
        raise SystemExit("Provide --invoice-number or --use-next-number.")

    description = args.description or client["default_work_description"]
    rate = args.rate or Decimal(str(client["default_rate"]))
    balance_due = args.hours * rate
    month_label = date(year, month, 1).strftime("%B %Y")
    output_path = args.out
    if not output_path:
        filename = clean_filename(f"{client['display_name']} Invoice - {month_label}.pdf")
        output_path = PROJECT_ROOT / "sent" / client["folder_name"] / filename
    output_path.parent.mkdir(parents=True, exist_ok=True)

    spec = {
        "contractor": contractor,
        "client": client,
        "account": account,
        "account_id": account_id,
        "invoice_number": invoice_number,
        "invoice_date": invoice_date,
        "due_date": due_date,
        "work_period": args.work_period or default_work_period(year, month, invoice_date),
        "description": description,
        "hours": str(args.hours),
        "hours_display": f"{args.hours:g}",
        "rate": rate,
        "balance_due": balance_due,
        "title": f"{client['display_name']} Invoice - {month_label}",
        "output_path": str(output_path),
    }
    render_pdf(spec, output_path)

    if args.record:
        record = {
            key: value
            for key, value in spec.items()
            if key not in {"client", "account", "contractor", "invoice_date", "due_date", "rate", "balance_due"}
        }
        record.update(
            {
                "client": args.client,
                "invoice_date": invoice_date.isoformat(),
                "due_date": due_date.isoformat(),
                "rate": str(rate),
                "balance_due": str(balance_due),
            }
        )
        write_json(PROJECT_ROOT / ".invoice-data" / "jobs" / f"{timestamp_slug()}-render-{args.client}.json", record)

    print(output_path)


if __name__ == "__main__":
    main()

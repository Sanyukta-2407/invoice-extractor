from fastapi import FastAPI
from pydantic import BaseModel
import re
from datetime import datetime

app = FastAPI(title="Invoice Extractor")


class ExtractRequest(BaseModel):
    text: str


class ExtractResponse(BaseModel):
    vendor: str
    amount: float
    currency: str
    date: str


@app.get("/")
def root():
    return {"message": "Invoice Extractor API running"}


@app.post("/extract", response_model=ExtractResponse)
def extract(req: ExtractRequest):
    text = req.text

    if not text.strip():
        return ExtractResponse(
            vendor="",
            amount=0.0,
            currency="USD",
            date="1970-01-01"
        )

    # ---------------- Vendor ----------------
    vendor = ""
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    for line in lines:
        m = re.search(r"vendor[:\-]?\s*(.+)", line, re.IGNORECASE)
        if m:
            vendor = m.group(1).strip()
            break

    if not vendor:
        vendor = lines[0] if lines else ""

    # ---------------- Currency ----------------
    currency = "USD"
    m = re.search(r"\b(USD|EUR|GBP)\b", text, re.IGNORECASE)
    if m:
        currency = m.group(1).upper()

    # ---------------- Amount ----------------
    amount = 0.0

    amount_patterns = [
        r"(?:total\s*due|amount\s*due|total|grand\s*total|balance\s*due)\D*([0-9]+(?:\.[0-9]{2})?)",
        r"\b(?:USD|EUR|GBP)\s*([0-9]+(?:\.[0-9]{2})?)",
        r"([0-9]+\.[0-9]{2})",
    ]

    for pattern in amount_patterns:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            amount = float(m.group(1))
            break

    # ---------------- Date ----------------
    date = "1970-01-01"

    m = re.search(r"(\d{4}-\d{2}-\d{2})", text)
    if m:
        date = m.group(1)
    else:
        m = re.search(r"(\d{2}/\d{2}/\d{4})", text)
        if m:
            try:
                date = datetime.strptime(
                    m.group(1),
                    "%d/%m/%Y"
                ).strftime("%Y-%m-%d")
            except:
                pass

    return ExtractResponse(
        vendor=vendor,
        amount=amount,
        currency=currency,
        date=date
    )
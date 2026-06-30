from fastapi import FastAPI
from pydantic import BaseModel
import re
from datetime import datetime

app = FastAPI()


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
            amount=0,
            currency="USD",
            date="1970-01-01"
        )

    vendor = ""

    lines = [l.strip() for l in text.splitlines() if l.strip()]
    if lines:
        vendor = lines[0]

    amount = 0.0
    m = re.search(r'(\d+(?:\.\d+)?)', text)
    if m:
        amount = float(m.group(1))

    currency = "USD"
    m = re.search(r'\b(USD|EUR|GBP)\b', text, re.IGNORECASE)
    if m:
        currency = m.group(1).upper()

    date = "1970-01-01"
    m = re.search(r'(\d{4}-\d{2}-\d{2})', text)
    if m:
        date = m.group(1)
    else:
        try:
            d = re.search(r'(\d{2}/\d{2}/\d{4})', text)
            if d:
                date = datetime.strptime(
                    d.group(1),
                    "%d/%m/%Y"
                ).strftime("%Y-%m-%d")
        except Exception:
            pass

    return ExtractResponse(
        vendor=vendor,
        amount=amount,
        currency=currency,
        date=date
    )
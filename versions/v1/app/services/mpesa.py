"""Safaricom Daraja M-Pesa STK Push service."""
import base64
import httpx
from datetime import datetime
from app.core.config import settings


def _get_timestamp() -> str:
    return datetime.now().strftime("%Y%m%d%H%M%S")


def _get_password(shortcode: str, passkey: str, timestamp: str) -> str:
    raw = f"{shortcode}{passkey}{timestamp}"
    return base64.b64encode(raw.encode()).decode()


async def get_access_token() -> str:
    """Fetch OAuth token from Daraja."""
    url = f"{settings.MPESA_BASE_URL}/oauth/v1/generate?grant_type=client_credentials"
    async with httpx.AsyncClient() as client:
        r = await client.get(
            url,
            auth=(settings.MPESA_CONSUMER_KEY, settings.MPESA_CONSUMER_SECRET),
            timeout=10,
        )
        r.raise_for_status()
        return r.json()["access_token"]


async def initiate_stk_push(
    phone: str,
    amount: float,
    account_reference: str,
    transaction_desc: str,
    callback_url: str,
) -> dict:
    """
    Initiate Lipa Na M-Pesa Online (STK Push).
    Returns the Daraja API response dict.
    """
    token = await get_access_token()
    timestamp = _get_timestamp()
    password = _get_password(
        settings.MPESA_SHORTCODE,
        settings.MPESA_PASSKEY,
        timestamp,
    )
    # Normalize phone: 07XXXXXXXX → 2547XXXXXXXX
    if phone.startswith("0"):
        phone = "254" + phone[1:]
    elif phone.startswith("+"):
        phone = phone[1:]

    payload = {
        "BusinessShortCode": settings.MPESA_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": int(amount),
        "PartyA": phone,
        "PartyB": settings.MPESA_SHORTCODE,
        "PhoneNumber": phone,
        "CallBackURL": callback_url,
        "AccountReference": account_reference[:12],
        "TransactionDesc": transaction_desc[:13],
    }
    url = f"{settings.MPESA_BASE_URL}/mpesa/stkpush/v1/processrequest"
    async with httpx.AsyncClient() as client:
        r = await client.post(
            url,
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
            timeout=15,
        )
        r.raise_for_status()
        return r.json()

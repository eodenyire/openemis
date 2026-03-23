"""
Africa's Talking SMS service.
Docs: https://developers.africastalking.com/docs/sms/sending
"""
import httpx
from datetime import datetime
from typing import List, Optional
from app.core.config import settings


AT_SMS_URL = "https://api.africastalking.com/version1/messaging"
AT_SMS_SANDBOX_URL = "https://api.sandbox.africastalking.com/version1/messaging"


def _sms_url() -> str:
    return AT_SMS_SANDBOX_URL if settings.AT_USERNAME == "sandbox" else AT_SMS_URL


def _normalize_phone(phone: str) -> str:
    """Normalize Kenyan phone numbers to +254XXXXXXXXX format."""
    phone = phone.strip().replace(" ", "").replace("-", "")
    if phone.startswith("07") or phone.startswith("01"):
        return "+254" + phone[1:]
    if phone.startswith("254"):
        return "+" + phone
    if phone.startswith("+254"):
        return phone
    return phone


async def send_sms(
    recipients: List[str],
    message: str,
    sender_id: Optional[str] = None,
) -> dict:
    """
    Send SMS via Africa's Talking.
    Returns AT API response dict with 'SMSMessageData'.
    Falls back gracefully if AT_API_KEY is not configured (sandbox/dev mode).
    """
    if not settings.AT_API_KEY:
        # Dev mode — simulate success without hitting AT
        return {
            "SMSMessageData": {
                "Message": f"Sent to {len(recipients)} recipients (dev mode)",
                "Recipients": [
                    {"number": r, "status": "Success", "messageId": f"dev-{i}",
                     "cost": "KES 0.8000"}
                    for i, r in enumerate(recipients)
                ],
            }
        }

    normalized = [_normalize_phone(p) for p in recipients if p]
    if not normalized:
        return {"error": "No valid recipients"}

    headers = {
        "apiKey": settings.AT_API_KEY,
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "username": settings.AT_USERNAME,
        "to": ",".join(normalized),
        "message": message,
    }
    if sender_id or settings.AT_SENDER_ID:
        data["from"] = sender_id or settings.AT_SENDER_ID

    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.post(_sms_url(), data=data, headers=headers)
        r.raise_for_status()
        return r.json()


async def send_single_sms(phone: str, message: str) -> dict:
    """Convenience wrapper for single recipient."""
    return await send_sms([phone], message)


def parse_at_response(response: dict) -> dict:
    """
    Parse Africa's Talking response into a summary dict.
    Returns: {sent: int, failed: int, cost: float, recipients: list}
    """
    data = response.get("SMSMessageData", {})
    recipients = data.get("Recipients", [])
    sent = sum(1 for r in recipients if r.get("status") == "Success")
    failed = len(recipients) - sent
    # Cost format: "KES 0.8000" — sum all
    total_cost = 0.0
    for r in recipients:
        cost_str = r.get("cost", "KES 0")
        try:
            total_cost += float(cost_str.replace("KES", "").strip())
        except (ValueError, AttributeError):
            pass
    return {
        "sent": sent,
        "failed": failed,
        "cost": round(total_cost, 4),
        "recipients": recipients,
    }


# ── Pre-built message builders ────────────────────────────────────────────────

def build_fee_reminder(student_name: str, amount: float, due_date: str,
                       school_name: str = "School") -> str:
    return (
        f"Dear Parent, {student_name}'s school fees balance of "
        f"KES {amount:,.0f} is due on {due_date}. "
        f"Pay via M-Pesa Paybill. - {school_name}"
    )


def build_attendance_alert(student_name: str, date_str: str,
                            school_name: str = "School") -> str:
    return (
        f"Dear Parent, {student_name} was marked ABSENT on {date_str}. "
        f"Please contact the school if this is an error. - {school_name}"
    )


def build_exam_result(student_name: str, exam_name: str, score: float,
                      grade: str, school_name: str = "School") -> str:
    return (
        f"Dear Parent, {student_name} scored {score:.1f}% ({grade}) "
        f"in {exam_name}. Visit the parent portal for full results. - {school_name}"
    )


def build_announcement_sms(title: str, school_name: str = "School") -> str:
    return f"[{school_name}] New announcement: {title}. Log in to the parent portal for details."

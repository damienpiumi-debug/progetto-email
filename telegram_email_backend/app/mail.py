from fastapi_mail import (
    FastMail,
    MessageSchema,
    ConnectionConfig,
    MessageType
)
from pydantic import EmailStr
from typing import List
import os

# ─────────────── UTILS ───────────────

def get_port() -> int:
    port = os.getenv("MAIL_PORT")
    if port and port.isdigit():
        return int(port)
    return 465

def get_bool_env(key: str, default: bool = False) -> bool:
    value = os.getenv(key, str(default)).lower()
    return value in ("true", "1", "yes")

# ─────────────── CONFIG SMTP ───────────────

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_SERVER=os.getenv("MAIL_SERVER"),
    MAIL_PORT=get_port(),
    MAIL_FROM_NAME=os.getenv("MAIL_FROM_NAME", "Telegram Mail Bot"),
    MAIL_STARTTLS=get_bool_env("MAIL_STARTTLS", False),
    MAIL_SSL_TLS=get_bool_env("MAIL_SSL_TLS", True),
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)

fm = FastMail(conf)

# ─────────────── SEND EMAIL ───────────────

async def send_email(
    to: EmailStr,
    subject: str,
    body: str,
    pdf_path: str,
):
    """
    Invia una mail con allegato PDF
    """
    message = MessageSchema(
        subject=subject,
        recipients=[to],
        body=body.replace("\n", "<br>"),
        subtype=MessageType.html,
        attachments=[pdf_path],
    )

    await fm.send_message(message)

import os
from dotenv import load_dotenv
from fastapi_mail import ConnectionConfig

load_dotenv()

mail_conf = ConnectionConfig(
    MAIL_USERNAME=os.environ["MAIL_USERNAME"],
    MAIL_PASSWORD=os.environ["MAIL_PASSWORD"],
    MAIL_FROM=os.environ["MAIL_FROM"],
    MAIL_SERVER=os.environ["MAIL_SERVER"],
    MAIL_PORT=int(os.environ.get("MAIL_PORT", 465)),

    # ⚠️ QUESTO È IL FIX
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,

    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)
DATABASE_URL=os.environ["DATABASE_URL"]

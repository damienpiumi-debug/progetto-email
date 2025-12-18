from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from database import Base


class MailLog(Base):
    __tablename__ = "mail_logs"


    id = Column(Integer, primary_key=True)
    telegram_user = Column(String(100))
    recipient = Column(String(200))
    subject = Column(String(200))
    body = Column(String(2000))
    pdf_path = Column(String(300))
    created_at = Column(DateTime, default=datetime.utcnow)

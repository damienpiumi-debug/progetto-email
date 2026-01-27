from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from models import MailLog


router = APIRouter(prefix="/mails", tags=["Mails"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
def list_mails(db: Session = Depends(get_db)):
    return db.query(MailLog).all()


@router.get("/{mail_id}")
def get_mail(mail_id: int, db: Session = Depends(get_db)):
    mail = db.query(MailLog).filter(MailLog.id == mail_id).first()
    if not mail:
        return {"error": "Mail non trovata"}
    return mail
from telegram import Update, Document
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters,
)

import os
import subprocess

from mail import send_email
from database import SessionLocal
from models import MailLog

# Stati della conversazione
EMAIL, SUBJECT, TEXT, FILE, CONFIRM = range(5)

UPLOAD_DIR = "/tmp"
MAX_FILE_SIZE_MB = 20  # limite massimo PDF

# ─────────────── START ───────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📧 Inserisci l'indirizzo email del destinatario:"
    )
    return EMAIL

# ─────────────── EMAIL ───────────────

async def get_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["email"] = update.message.text
    await update.message.reply_text("📝 Inserisci l'oggetto della mail:")
    return SUBJECT

# ─────────────── SUBJECT ───────────────

async def get_subject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["subject"] = update.message.text
    await update.message.reply_text("✉️ Inserisci il testo della mail:")
    return TEXT

# ─────────────── TEXT ───────────────

async def get_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["text"] = update.message.text
    await update.message.reply_text(
        "📎 Ora carica un file (PDF, DOCX, JPG, PNG):"
    )
    return FILE

# ─────────────── FILE ───────────────

async def get_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    document: Document = update.message.document

    # controllo dimensione file
    if document.file_size > MAX_FILE_SIZE_MB * 1024 * 1024:
        await update.message.reply_text(
            "❌ Il file è troppo grande e non può essere mandato.\n"
            f"Dimensione massima consentita: {MAX_FILE_SIZE_MB} MB"
        )
        return ConversationHandler.END

    file = await document.get_file()
    original_path = os.path.join(UPLOAD_DIR, document.file_name)
    await file.download_to_drive(original_path)

    # conversione in PDF se necessario
    if not original_path.lower().endswith(".pdf"):
        subprocess.run(
            [
                "libreoffice",
                "--headless",
                "--convert-to",
                "pdf",
                "--outdir",
                UPLOAD_DIR,
                original_path,
            ],
            check=True,
        )
        pdf_path = original_path.rsplit(".", 1)[0] + ".pdf"
    else:
        pdf_path = original_path

    # controllo dimensione PDF finale
    if os.path.getsize(pdf_path) > MAX_FILE_SIZE_MB * 1024 * 1024:
        await update.message.reply_text(
            "❌ Il PDF supera la dimensione massima consentita "
            "e non può essere mandato."
        )
        return ConversationHandler.END

    context.user_data["pdf_path"] = pdf_path

    await update.message.reply_text(
        "👀 Confermi l'invio?\nScrivi *si* per inviare o *no* per annullare",
        parse_mode="Markdown",
    )
    return CONFIRM

# ─────────────── CONFIRM ───────────────

async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    risposta = update.message.text.lower()

    if risposta not in ["si", "sì", "yes"]:
        await update.message.reply_text("❌ Invio annullato")
        return ConversationHandler.END

    # invio email
    await send_email(
        to=context.user_data["email"],
        subject=context.user_data["subject"],
        body=context.user_data["text"],
        pdf_path=context.user_data["pdf_path"],
    )

    # salvataggio DB
    db = SessionLocal()
    log = MailLog(
        telegram_user=str(update.effective_user.id),
        recipient=context.user_data["email"],
        subject=context.user_data["subject"],
        body=context.user_data["text"],
        pdf_path=context.user_data["pdf_path"],
    )
    db.add(log)
    db.commit()
    db.close()

    await update.message.reply_text("✅ Email inviata con successo!")
    return ConversationHandler.END

# ─────────────── BOT START ───────────────

async def start_bot(token: str):
    application = Application.builder().token(token).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("send", start)],
        states={
            EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_email)],
            SUBJECT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_subject)],
            TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_text)],
            FILE: [MessageHandler(filters.Document.ALL, get_file)],
            CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm)],
        },
        fallbacks=[],
    )

    application.add_handler(conv_handler)
    await application.run_polling()

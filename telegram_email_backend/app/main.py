from fastapi import FastAPI
import asyncio


from database import Base, engine
from telegram_bot import start_bot
from config import TELEGRAM_TOKEN
from routers.send_mail import router


app = FastAPI(title="Telegram Mail Backend")


Base.metadata.create_all(bind=engine)
app.include_router(router)


@app.on_event("startup")
async def startup():
    asyncio.create_task(start_bot(TELEGRAM_TOKEN))
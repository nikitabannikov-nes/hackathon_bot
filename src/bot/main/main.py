from contextlib import asynccontextmanager

import uvicorn
from aiogram import Dispatcher, Bot
from aiogram.types import Update
from fastapi import FastAPI, Request

from admin_panel.routers.panel import router as panel_router
from admin_panel.routers.del_person import router as del_per_router
from admin_panel.routers.add_person import router as add_per_router
from admin_panel.routers.add_check_list import router as add_checklist_router
from admin_panel.routers.schedule_work import router as schedule_work_router

bot = Bot(token="7953741570:AAFJfVKKB7L4CO1UvjE1i7gZAuaVNJMsntc")
dp = Dispatcher()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await bot.set_webhook(url="https://9zzlyf-185-158-216-29.ru.tuna.am/webhook",
                          allowed_updates=dp.resolve_used_update_types(),
                          drop_pending_updates=True)

    yield
    await bot.delete_webhook()


app = FastAPI(lifespan=lifespan)

@app.post("/webhook")
async def webhook(request: Request) -> None:
    update = Update.model_validate(await request.json(), context={"bot": bot})
    await dp.feed_update(bot, update)

if __name__ == "__main__":
    dp.include_router(del_per_router)
    dp.include_router(panel_router)
    dp.include_router(add_checklist_router)
    dp.include_router(schedule_work_router)

    dp.include_router(add_per_router)

    uvicorn.run(app, host="127.0.0.1", port=80)

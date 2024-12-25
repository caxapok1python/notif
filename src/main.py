import uvicorn
from fastapi import FastAPI
from database import Base, engine
from routers import auth, notifications, users

# Создаём таблицы в БД, если их ещё нет.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Notification Service",
    version="1.0.0",
    description="Сервис для отправки уведомлений (внутренние, SMS, email)."
)

app.include_router(auth.router)
app.include_router(notifications.router)
app.include_router(users.router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
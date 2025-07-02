from fastapi import FastAPI
from src.presentation.api.health import router as health_router
from src.presentation.api.todo import router as todo_router

app = FastAPI()

app.include_router(health_router)
app.include_router(todo_router)

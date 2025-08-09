from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.presentation.api.health import router as health_router
from src.presentation.api.todo import router as todo_router
from src.presentation.api.task import router as task_router
from src.presentation.api.auth import router as auth_router
from src.containers import Container
from dotenv import load_dotenv

load_dotenv()


container = Container()
container.config.from_yaml("config.yml")

app = FastAPI(docs_url="/api/documentation", openapi_url="/api/openapi.json")
app.container = container  # type: ignore

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(todo_router)
app.include_router(task_router)
app.include_router(auth_router)

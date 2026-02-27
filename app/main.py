from fastapi import FastAPI

from app.database import Base, engine
from app.routers import telemetry


def create_app() -> FastAPI:
    application = FastAPI(
        title="Game Telemetry API",
        version="0.1.0",
        description="Backend service for collecting and querying game telemetry.",
    )

    application.include_router(telemetry.router)
    application.include_router(telemetry.admin_router)
    application.include_router(telemetry.admin_ui_router)

    @application.on_event("startup")
    def on_startup() -> None:
        # Automatically create database tables on startup
        Base.metadata.create_all(bind=engine)

    return application


app = create_app()


from contextlib import asynccontextmanager

from dotenv import load_dotenv

load_dotenv()

from dependency_injector import providers
from fastapi import FastAPI

from config.applicationConfig import ApplicationSettings
from controllers.auth_controller import router as auth_router
from controllers.health_controller import router as health_router
from core.di.container import Container
from startups.initialize_models import initialize_models
from startups.validator import run_all_validators
from utils.logger import configure_logging, get_logger

_log = get_logger(__name__)

def register_controllers(app: FastAPI, container: Container) -> None:
    app.include_router(health_router)
    _log.info("Health routes mounted on application")
    app.include_router(auth_router)
    _log.info("Auth routes mounted on application")


def create_app() -> FastAPI:
    configure_logging()
    _log.info("Bootstrapping application (config + DI)")

    settings = ApplicationSettings()
    container = Container(settings=providers.Object(settings))

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        _log.info("Startup: running validators")
        run_all_validators(container)
        _log.info("Startup: validators completed")
        initialize_models(container.db_connection().engine)
        yield

    app = FastAPI(title="gaserp", lifespan=lifespan)
    app.state.settings = settings
    app.state.container = container

    register_controllers(app, container)

    return app


app = create_app()


def main():
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)


if __name__ == "__main__":
    main()

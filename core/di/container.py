from dependency_injector import containers, providers

from config.applicationConfig import ApplicationSettings
from core.di.configInjector import create_postgresql_connection
from services.auth_service import AuthService


class Container(containers.DeclarativeContainer):
    settings = providers.Singleton(ApplicationSettings)
    db_connection = providers.Singleton(create_postgresql_connection, settings)
    auth_service = providers.Factory(
        AuthService,
        connection=db_connection,
        settings=settings,
    )

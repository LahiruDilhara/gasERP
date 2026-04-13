from config.applicationConfig import ApplicationSettings
from db.postgresql import PostgreSQLConnection


def create_postgresql_connection(settings: ApplicationSettings) -> PostgreSQLConnection:
    return PostgreSQLConnection(
        database_url=settings.database_url,
        db_host=settings.db_host,
        db_port=settings.db_port,
        db_name=settings.db_name,
        db_user=settings.db_user,
        db_password=settings.db_password.get_secret_value(),
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
        pool_timeout=settings.db_pool_timeout,
        pool_recycle=settings.db_pool_recycle,
    )

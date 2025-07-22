import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy import MetaData

from app.config import settings

"""

Данный модуль используется для создания БД "test_task" и подключения к ней.

"""


def create_database():
    # dialect+driver://username:password@host:port/database

    # Устанавливаем соединение с postgres
    connection = psycopg2.connect(
        user=f"{settings.postgres_user}",
        password=f"{settings.postgres_password}",
        host=f"{settings.docker_postgres_host}"
    )
    connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

    # Создаем курсор для выполнения операций с базой данных
    cursor = connection.cursor()

    # Создаем базу данных
    sql_create_database = cursor.execute(f'create database {settings.postgres_db_name}')

    # Закрываем соединение
    cursor.close()
    connection.close()


def create_testing_database():
    connection = psycopg2.connect(
        user=f"{settings.postgres_user}",
        password=f"{settings.postgres_password}"
    )
    connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = connection.cursor()
    sql_create_database = cursor.execute(f'create database {settings.test_postgres_db_name}')
    cursor.close()
    connection.close()


convention = {
    'all_column_names': lambda constraint, table: '_'.join([
        column.name for column in constraint.columns.values()
    ]),
    'ix': 'ix__%(table_name)s__%(all_column_names)s',
    'uq': 'uq__%(table_name)s__%(all_column_names)s',
    'ck': 'ck__%(table_name)s__%(constraint_name)s',
    'fk': (
        'fk__%(table_name)s__%(all_column_names)s__'
        '%(referred_table_name)s'
    ),
    'pk': 'pk__%(table_name)s'
}

# Registry for all tables
metadata = MetaData(naming_convention=convention)

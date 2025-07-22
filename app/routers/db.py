from fastapi import APIRouter, Depends, Path, Query
from sqlmodel import SQLModel, Field, create_engine, Session
from contextlib import asynccontextmanager
from typing import Annotated
from psycopg2.errors import DuplicateDatabase
from sqlalchemy.exc import IntegrityError, NoResultFound

from .db_connection import create_database
from ..config import settings


class WalletBalance(SQLModel, table=True):
    """ Таблица с основной информацией о сотрудниках """
    id: int | None = Field(default=None, primary_key=True)
    wallet_balance: int


database_url = settings.get_db_url()


engine = create_engine(
    f"postgresql+psycopg2://"
    f"{settings.postgres_user}:"
    f"{settings.postgres_password}@"
    # f"{settings.postgres_host}:" # Хост для работы без Docker
    f"{settings.docker_postgres_host}:"
    f"{settings.postgres_port}/"
    f"{settings.postgres_db_name}",
)


def create_db_and_tables():
    try:
        # create_database()
        metadata = SQLModel.metadata.create_all(engine)
        return metadata
    except DuplicateDatabase:
        print('Attempt to create existing database. Nothing to worry about)')


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


@asynccontextmanager
async def lifespan(router: APIRouter):
    create_db_and_tables()
    yield


router = APIRouter(tags=['Взаимодействие с БД'], lifespan=lifespan)


@router.post('/api/v1/wallets/{wallet_id}/operation')
def deposit(
        wallet_id: Annotated[
            int,
            Path(title='Идентификатор кошелька, всего их 1000(условно)',
                 gt=0,
                 le=1000
                 )
        ],
        session: SessionDep,
        query_balance: Annotated[
            int,
            Query(title='Сумма зачисления на баланс кошелька от 0 до 50000 рублей (условно)',
                  gt=0,
                  le=50000
                  )
        ]
):
    """
    Создание записи в таблице walletbalance. Используется при инициализации счета.
    Небольшое отступление от условия задания:
    Вместо отправки фиксированного значения amount: 1000 решил ввести параметр запроса query_balance,
    содержащий сумму, которую необходимо добавить на счет.
    """
    try:
        session.add(WalletBalance(id=wallet_id, wallet_balance=query_balance))
        session.commit()
        return {"message": "money submitted succesfully!"}
    except IntegrityError:
        session.rollback()
        return {"message": "attempt to rewrite existing record, try PATCH method instead"}


@router.get('/api/v1/wallets/{wallet_id}')
def get_wallet_balance(
        wallet_id: Annotated[
            int,
            Path(title='Идентификатор кошелька, всего их 1000(условно)',
                 gt=0,
                 le=1000
                 )
        ],
        session: SessionDep
):
    """
    Ручка чтения баланса из таблицы walletbalance
    """
    try:
        current_wallet_balance = session.query(WalletBalance).filter(WalletBalance.id == wallet_id).one()
        return current_wallet_balance.wallet_balance
    except NoResultFound:
        session.rollback()
        return {'message': 'the mentioned above wallet id does not exist'}


@router.patch('/api/v1/wallets/{wallet_id}/operation')
def update_user(
        wallet_id: Annotated[
            int,
            Path(title='Идентификатор кошелька, всего их 1000(условно)',
                 gt=0,
                 le=1000
                 )
        ],
        session: SessionDep,
        query_balance: Annotated[
            int,
            Query(title='Сумма зачисления на баланс кошелька от 0 до 50000 рублей (условно)',
                  gt=0,
                  le=50000
                  )
        ]
):
    """
    Ручка обновления баланса кошелька в БД
    """
    try:
        db_data = session.get(WalletBalance, wallet_id)
        print(db_data, type(db_data))
        db_data.sqlmodel_update({'wallet_balance': query_balance})
        session.add(db_data)
        session.commit()
        session.refresh(db_data)
        return {'message': 'data updated successfully'}
    except IntegrityError:
        session.rollback()
        return {"message": "something went wrong..."}


@router.delete("/api/v1/wallets/{wallet_id}/operation")
def delete_user(
        wallet_id: Annotated[
            int,
            Path(title='Идентификатор кошелька, всего их 1000(условно)',
                 gt=0,
                 le=1000
                 )
        ],
        session: SessionDep,
):
    """
    Ручка удаления записи о балансе кошелька из БД
    """
    try:
        db_data = session.get(WalletBalance, wallet_id)
        session.delete(db_data)
        session.commit()
        return {'message': 'row deleted successfully!'}
    except IntegrityError:
        session.rollback()
        return {"message": "something went wrong..."}

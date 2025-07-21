import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session, StaticPool
from app.main import app
from app.routers.db import get_session as get_db_session, WalletBalance
from app.routers.db_connection import create_testing_database
from psycopg2.errors import DuplicateDatabase
from fastapi.encoders import jsonable_encoder
from app.config import settings


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        f"postgresql+psycopg2://"
        f"{settings.postgres_user}:"
        f"{settings.postgres_password}@"
        f"{settings.postgres_host}:"
        f"{settings.postgres_port}/"
        f"{settings.test_postgres_db_name}",
    )
    try:
        create_testing_database()
        SQLModel.metadata.create_all(engine)
    except DuplicateDatabase:
        print('Attempt to create existing database. Nothing to worry about)')
    finally:
        with Session(engine) as session:
            yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_db_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def test_deposit_duplicate(client: TestClient):
    response = client.post("/api/v1/wallets/1/operation?query_balance=15000")
    response_2 = client.post("/api/v1/wallets/1/operation?query_balance=5000")
    client.delete("/api/v1/wallets/1/operation")
    assert response.status_code == 200
    assert response.json() == {"message": "money submitted succesfully!"}
    assert response_2.status_code == 200
    assert response_2.json() == {"message": "attempt to rewrite existing record, try PATCH method instead"}


def test_deposit_incomplete(client: TestClient):
    response = client.post("/api/v1/wallets/1/operation")
    assert response.status_code == 422
    assert response.json() == {
        'detail': [{'type': 'missing', 'loc': ['query', 'query_balance'], 'msg': 'Field required', 'input': None}]}


def test_deposit_invalid_query(client: TestClient):
    response = client.post("/api/v1/wallets/1/operation?query_balance=52000")
    assert response.status_code == 422
    assert response.json() == {'detail': [{'type': 'less_than_equal', 'loc': ['query', 'query_balance'],
                                           'msg': 'Input should be less than or equal to 50000', 'input': '52000',
                                           'ctx': {'le': 50000}}]}


def test_deposit_invalid_path(client: TestClient):
    response = client.post("/api/v1/wallets/1007/operation?query_balance=26000")
    assert response.status_code == 422


def test_get_wallet_balance(client: TestClient):
    client.post("/api/v1/wallets/3/operation?query_balance=26000")
    response = client.get('/api/v1/wallets/3')
    client.delete("/api/v1/wallets/3/operation")
    assert response.status_code == 200
    assert int(response.text) == 26000


def test_get_wallet_balance_incomplete(client: TestClient):
    response = client.get('/api/v1/wallets/')
    assert response.status_code == 404


def test_get_wallet_balance_invalid(client: TestClient):
    response = client.get('/api/v1/wallets/4')
    assert response.status_code == 200
    assert response.json() == {'message': 'the mentioned above wallet id does not exist'}


def test_update_record(client: TestClient):
    client.post("/api/v1/wallets/5/operation?query_balance=26000")
    patch_response = client.patch("/api/v1/wallets/5/operation?query_balance=30000")
    get_response = client.get('/api/v1/wallets/5')
    client.delete("/api/v1/wallets/5/operation")
    assert patch_response.status_code == 200
    assert patch_response.json() == {'message': 'data updated successfully'}
    assert get_response.status_code == 200
    assert int(get_response.text) == 30000


def test_update_record_invalid(client: TestClient):
    client.post("/api/v1/wallets/5/operation?query_balance=26000")
    patch_response = client.patch("/api/v1/wallets/5/operation?query_balance=53000")
    client.delete("/api/v1/wallets/5/operation")
    assert patch_response.status_code == 422


def test_update_record_incomplete(client: TestClient):
    client.post("/api/v1/wallets/5/operation?query_balance=26000")
    patch_response = client.patch("/api/v1/wallets/5/operation")
    client.delete("/api/v1/wallets/5/operation")
    assert patch_response.status_code == 422


def test_delete_record(client: TestClient):
    client.post("/api/v1/wallets/33/operation?query_balance=13339")
    response = client.delete("/api/v1/wallets/33/operation")
    assert response.status_code == 200
    assert response.json() == {'message': 'row deleted successfully!'}


def test_delete_record_invalid(client: TestClient):
    response = client.delete("/api/v1/wallets/0/operation")
    assert response.status_code == 422
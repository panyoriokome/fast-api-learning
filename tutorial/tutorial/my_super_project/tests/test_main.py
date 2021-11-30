from fastapi.testclient import TestClient
import pytest
from sql_app.main import app
from sql_app.models import User

client = TestClient(app)


def test_read_users_empty(test_db):
    response = client.get("/users/")
    assert response.status_code == 200
    assert response.json() == []

def test_read_users(test_db):
    # テスト用のデータを用意
    user1 = User(email="user1@example.com", hashed_password="unsecurepass")
    user2 = User(email="user2@example.com", hashed_password="unsecurepass")
    test_db.add_all([user1, user2])
    test_db.flush()
    test_db.commit()

    # テスト対象の処理を実行
    response = client.get("/users/")

    # 処理の結果の確認
    assert response.status_code == 200
    assert response.json() == [
        {"email": "user1@example.com", "id": 1, "is_active": True, "items": []},
        {"email": "user2@example.com", "id": 2, "is_active": True, "items": []},
    ]
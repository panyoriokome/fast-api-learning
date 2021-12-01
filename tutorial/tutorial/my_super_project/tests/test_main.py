from fastapi.testclient import TestClient
import pytest
from sql_app.main import app
from sql_app.models import User, Item
from sql_app import schemas

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


def test_read_users_with_items(test_db):
    """userとuserに紐づくアイテムが返されることを確認する"""
    # テスト用のデータを用意
    user1 = User(email="user1@example.com", hashed_password="unsecurepass")
    item1 = Item(title="テストアイテム", description="テストのためのアイテム", owner_id=1)
    test_db.add_all([user1, item1])
    test_db.flush()
    test_db.commit()

    # テスト対象の処理を実行
    response = client.get("/users/")

    assert response.status_code == 200
    assert response.json() == [
        {
            "email": "user1@example.com",
            "id": 1,
            "is_active": True,
            "items": [{"title": "テストアイテム", "description": "テストのためのアイテム", "id": 1, "owner_id": 1}],
        },
    ]


class TestCreateUser:
    def test_create_user_can_create_single_user(test_db):
        user1 = {"email": "user1@example.com", "password": "testpassword"}

        response = client.post("/users/", json=user1)

        # 処理結果の確認
        assert response.status_code == 200

    def test_create_user_can_create_single_user(test_db):
        """同一ユーザを二重に作成できないことを確認"""
        user1 = {"email": "user1@example.com", "password": "testpassword"}

        response = client.post("/users/", json=user1)

        # 処理結果の確認
        assert response.status_code == 200

        response = client.post("/users/", json=user1)

        # 処理結果の確認
        assert response.status_code == 400
        assert response.json() == {"detail": "Email already registered"}

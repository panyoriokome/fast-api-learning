from uuid import uuid4

import pytest
from sqlalchemy import orm
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, scoped_session, sessionmaker
from sqlalchemy.orm.session import close_all_sessions

from sql_app.main import app, get_db
from sql_app.models import Base

class TestingSession(Session):
    def commit(self):
        # テストなので永続化しない
        self.flush()
        self.expire_all()


@pytest.fixture(scope="function")
def test_db():
    engine = create_engine("sqlite:///./sql_app_test.db", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)

    # テストケースごとに異なるスコープを持たせる
    function_scope = uuid4().hex
    TestSessionLocal = scoped_session(
        sessionmaker(class_=TestingSession, autocommit=False, autoflush=False, bind=engine),
        scopefunc=lambda: function_scope,
    )
    Base.query = TestSessionLocal.query_property()

    # sql_app/main.py の get_db() を差し替える
    # https://fastapi.tiangolo.com/advanced/testing-dependencies/
    def get_db_for_testing():
        db = TestSessionLocal()
        try:
            yield db
            db.commit()
        except SQLAlchemyError as e:
            assert e is not None
            db.rollback()

    # TestingSessionクラスをテスト内で使用するため
    # リクエストハンドラ内でセッションインスタンスを取得するための処理を上書き
    app.dependency_overrides[get_db] = get_db_for_testing

    # テストケース実行
    yield TestSessionLocal()

    # 後処理
    TestSessionLocal().rollback()
    TestSessionLocal.remove()
    close_all_sessions()
    engine.dispose()
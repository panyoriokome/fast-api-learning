import sqlalchemy
from uuid import uuid4
from sqlalchemy import orm
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, scoped_session, sessionmaker
from sqlalchemy.orm.session import close_all_sessions
from factory.alchemy import SQLAlchemyModelFactory
from factory import Faker, Sequence, SubFactory, Iterator, SelfAttribute
from sql_app.models import User, Item
from tests_with_factory.conftest import Session
from sql_app.models import Base

class TestingSession(Session):
    def commit(self):
        # テストなので永続化しない
        self.flush()
        self.expire_all()

engine = create_engine("sqlite:///./sql_app_test.db", connect_args={"check_same_thread": False})
Base.metadata.create_all(bind=engine)

# テストケースごとに異なるスコープを持たせる
function_scope = uuid4().hex
TestSessionLocal = scoped_session(
    sessionmaker(class_=TestingSession, autocommit=False, autoflush=False, bind=engine),
    scopefunc=lambda: function_scope,
)

class UserFactory(SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session = TestSessionLocal
    
    id = Sequence(lambda n: n)
    email = Sequence(lambda n: f'address_{n}@hogemail.com')
    hashed_password = Sequence(lambda n: f'hashed_password{n}')
    is_active = Sequence(lambda n: True)

class ItemFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Item
        sqlalchemy_session = TestSessionLocal
    
    id = Sequence(lambda n: n)
    title = Sequence(lambda n: f'title_{n}')
    description = Sequence(lambda n: n)
    owner = SubFactory(UserFactory)
    owner_id = SelfAttribute('owner.id')

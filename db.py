from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./pirate.db" #chỗ lưu -> instance


#khởi tạo engine -> kết nối python với sql
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args = {"check_same_thread":False}
)

#nhà máy tạo session mỗi request fastapi cần một session và nó là ngừoi tạo
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush = False,
    bind = engine
)

#một cái khuôn nếu class con thừa hưởng thì nó sẽ được coi là một sql model
class Base(DeclarativeBase):
    pass


#tạo session
def get_db():
    with SessionLocal() as db:
        yield db


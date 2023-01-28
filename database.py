from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from dotenv import load_dotenv
import os

load_dotenv()

HOST = os.environ.get('HOST')
PORT = os.environ.get('PORT')
DB_NAME = os.environ.get('DB_NAME')
DB_USER = os.environ.get('DB_USER')
PASSWORD = os.environ.get('PASSWORD')

uri = f'mysql+pymysql://{DB_USER}:{PASSWORD}@{HOST}/{DB_NAME}?charset=utf8'
ENGINE = create_engine(
    uri,
    encoding='utf-8',
    echo=True
)

session = scoped_session(
    sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=ENGINE
    )
)

Base = declarative_base()
Base.query = session.query_property()
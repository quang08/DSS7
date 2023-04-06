from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database

import sqlalchemy

engine = create_engine('mysql+pymysql://root:north@localhost:3306/decision_tree')

if not database_exists(engine.url):
    create_database(engine.url)

connection = engine.connect()

inspect = sqlalchemy.inspect(engine)

Base = declarative_base()

SessionLocal = sessionmaker(bind = engine)
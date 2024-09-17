from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dbs_assignment.configuration import conf

SQLALCHEMY_DATABASE_URL = f"postgresql://{conf.DATABASE_USER}:{conf.DATABASE_PASSWORD}@{conf.DATABASE_HOST}:{conf.DATABASE_PORT}/{conf.DATABASE_NAME}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(engine)

Base = declarative_base()

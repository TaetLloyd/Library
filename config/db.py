from sqlalchemy import MetaData, create_engine
from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

#users database
SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://root@localhost:3306/bank"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
meta =MetaData()
conn = engine.connect()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

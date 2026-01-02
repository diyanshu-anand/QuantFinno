from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
# from dotenv import load_dotenv


# load_dotenv()


# DATABASE_URL = os.getenv("DATABSE_URL")

DATABASE_URL = "sqlite:///./finance.db"


engine = create_engine(DATABASE_URL, connect_args = {"check_same_thread":False} ) # Required fore sqlite and FastApi
SessionLocal = sessionmaker(bind = engine)

Base = declarative_base()
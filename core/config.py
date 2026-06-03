import os
from dotenv import load_dotenv

load_dotenv()

MASTER_DATABASE_URL = os.getenv(
    "MASTER_DATABASE_URL", "postgresql://employee:secret123@localhost:5432/mydatabase"
)
REPLICA_DATABASE_URL = os.getenv(
    "REPLICA_DATABASE_URL", "postgresql://employee:secret123@localhost:5433/mydatabase"
)


class Config:
    DEBUG = os.getenv("DEBUG", "true").lower() == "true"
    SQLALCHEMY_DATABASE_URI = MASTER_DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_SORT_KEYS = False
    MASTER_DATABASE_URL = MASTER_DATABASE_URL
    REPLICA_DATABASE_URL = REPLICA_DATABASE_URL

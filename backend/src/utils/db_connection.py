import os

from dotenv import load_dotenv
import mysql.connector

load_dotenv()

def get_db_config():
    return {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", "3307")),
        "user": os.getenv("DB_USER", "cineAdmin"),
        "password": os.getenv("DB_PASSWORD", "cinePass1234"),
        "database": os.getenv("DB_NAME", "cine_paradiso_db"),
        "charset": "utf8mb4",
        "autocommit": False,
        "use_pure": True,
    }


def get_db_connection():
    return mysql.connector.connect(**get_db_config())

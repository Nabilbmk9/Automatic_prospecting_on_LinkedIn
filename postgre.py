import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

def connect_db():
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        dbname= os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"))
    return conn


def search_link_from_db():
    pass

conn = connect_db()
cur = conn.cursor()

cur.close()
conn.commit()
conn.close()
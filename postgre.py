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

def retrieve_keyword_used():
    cur.execute("""
        SELECT keyword_used, id FROM lead_search_links_infos WHERE search_link = %s
    """, (os.getenv("SEARCH_LINK"),))
    return cur.fetchone()[0]

def retrieve_link_search_id():
    cur.execute("""
        SELECT keyword_used, id FROM lead_search_links_infos WHERE search_link = %s
    """, (os.getenv("SEARCH_LINK"),))
    return cur.fetchone()[1]


def retrieve_current_page():
    cur.execute("""
        SELECT current_page FROM lead_search_links_infos WHERE search_link = %s
    """, (os.getenv("SEARCH_LINK"),))
    return cur.fetchone()[0]


def retrieve_messages_sent():
    cur.execute("""
        SELECT messages_sent FROM lead_search_links_infos WHERE search_link = %s
    """, (os.getenv("SEARCH_LINK"),))
    return cur.fetchone()[0]


def search_link_from_db():
    pass

conn = connect_db()
cur = conn.cursor()

cur.close()
conn.commit()
conn.close()
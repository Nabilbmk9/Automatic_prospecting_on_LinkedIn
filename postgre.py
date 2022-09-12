import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

# Connect to database
def connect_db():
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        dbname= os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"))
    return conn

# Retrieve some data from database functions
def retrieve_keyword_used(cursor):
    cursor.execute("""
        SELECT keyword_used, id FROM lead_search_links_infos WHERE search_link = %s
    """, (os.getenv("SEARCH_LINK"),))
    return cursor.fetchone()[0]

def retrieve_link_search_id(cursor):
    cursor.execute("""
        SELECT keyword_used, id FROM lead_search_links_infos WHERE search_link = %s
    """, (os.getenv("SEARCH_LINK"),))
    return cursor.fetchone()[1]

def retrieve_current_page(cursor):
    cursor.execute("""
        SELECT current_page FROM lead_search_links_infos WHERE search_link = %s
    """, (os.getenv("SEARCH_LINK"),))
    return cursor.fetchone()[0]

def retrieve_messages_sent(cursor):
    cursor.execute("""
        SELECT messages_sent FROM lead_search_links_infos WHERE search_link = %s
    """, (os.getenv("SEARCH_LINK"),))
    return cursor.fetchone()[0]

def check_profile_exist_in_db(cursor, profile_link):
    cursor.execute("""
        SELECT * FROM linkedin_leads WHERE linkedin_link = %s
    """, (profile_link,))
    return cursor.fetchone()

def retrieve_nb_messages_sent_by_date(cursor, date):
    cursor.execute("""
        SELECT COUNT(*) FROM linkedin_leads WHERE last_message = %s
    """, (str(date),))
    return cursor.fetchone()[0]

# Insert data in database functions
def insert_new_profile_in_db(cursor, connexion, first_name, last_name, profile_link, message_sent_true_or_false, date, keyword_used, link_search_id, error=False):
    cursor.execute("""
        INSERT INTO linkedin_leads (first_name, last_name, linkedin_link, message_sent, last_message, category, link_search_id, error) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (first_name, last_name, profile_link, message_sent_true_or_false, str(date), keyword_used, int(link_search_id), False))
    connexion.commit()

# Update data in database functions
def update_current_page_in_db(cursor, connexion, current_page):
    cursor.execute("""
        UPDATE lead_search_links_infos SET current_page = %s WHERE search_link = %s
    """, (current_page, os.getenv("SEARCH_LINK")))
    connexion.commit()

def update_messages_sent_in_db(cursor, connexion, messages_sent):
    cursor.execute("""
        UPDATE lead_search_links_infos SET messages_sent = %s WHERE search_link = %s
    """, (messages_sent, os.getenv("SEARCH_LINK")))
    connexion.commit()

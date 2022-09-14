import os
from dotenv import load_dotenv
import psycopg2
from postgre import connect_db

load_dotenv()

conn = connect_db()
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS lead_search_links_infos (

    id SERIAL PRIMARY KEY,
    keyword_used TEXT,
    average_search_result INTEGER,
    messages_sent INTEGER DEFAULT 0,
    current_page INTEGER,
    max_pages INTEGER,
    search_link VARCHAR(300) UNIQUE
    );
""")

cur.execute(""" 
CREATE TABLE IF NOT EXISTS linkedin_leads (

    id SERIAL PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    linkedin_link VARCHAR(200) UNIQUE,
    message_sent BOOLEAN DEFAULT FALSE,
    follow_up_1 BOOLEAN DEFAULT FALSE,
    follow_up_2 BOOLEAN DEFAULT FALSE,
    follow_up_3 BOOLEAN DEFAULT FALSE,
    replied BOOLEAN DEFAULT FALSE,
    last_message DATE,
    category TEXT,
    error BOOLEAN DEFAULT FALSE,
    linkedin_sales_navigator_link VARCHAR(300),
    link_search_id INTEGER REFERENCES lead_search_links_infos(id)
    );
""")

try:
    #retrieve the id and message_sent of the line containing the search link
    cur.execute("SELECT id, messages_sent, current_page, max_pages FROM lead_search_links_infos WHERE search_link = %s", (os.getenv("SEARCH_LINK"),))
    search_link_id, messages_sent, current_page, max_pages = cur.fetchone()
    print(f"Le lien de recherche est déjà utilisé avec l'id n° {search_link_id}")
    print(f"Vous avez envoyé {messages_sent} messages avec ce lien de recherche")
    print(f"Vous êtes à la page {current_page} sur {max_pages}")

except:
    keyword_used = os.getenv("KEYWORD_USED")
    average_search_result = os.getenv("AVERAGE_SEARCH_RESULT")
    current_page = os.getenv("CURRENT_PAGE")
    max_page = os.getenv("MAX_PAGE")
    search_link = os.getenv("SEARCH_LINK")
    cur.execute("""
    INSERT INTO lead_search_links_infos (keyword_used, average_search_result, current_page, max_pages, search_link) 
    VALUES (%s, %s, %s, %s, %s)""", (keyword_used, average_search_result, current_page, max_page, search_link))


cur.close()
conn.commit()
conn.close()
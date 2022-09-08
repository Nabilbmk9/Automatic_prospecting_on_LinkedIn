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


conn = connect_db()
cur = conn.cursor()

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
    category VARCHAR(50),
    error BOOLEAN DEFAULT FALSE,
    linkedin_sales_navigator_link VARCHAR(300)
    );
""")

cur.close()
conn.commit()
conn.close()
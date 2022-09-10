from datetime import datetime
from distutils.spawn import spawn
import os
from unicodedata import category
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from selenium.webdriver.common.by import By

from api import click_ajouter_note, connection_compte, ecrire_message, envoi_message
from postgre import *
from pprint import pprint
from api_normal_search_link import *

load_dotenv()

conn = connect_db()
cur = conn.cursor()

today= datetime.now().strftime("%Y-%m-%d")

keyword_used = retrieve_keyword_used()
link_search_id = retrieve_link_search_id()

messages_sent = retrieve_messages_sent()


# Login to linkedin
username = os.getenv("LINKEDIN_EMAIL")
password = os.getenv("LINKEDIN_PASSWORD")
browser = connection_compte(username,password)

# Go to leads search page
current_page = retrieve_current_page()
search_link = os.getenv("SEARCH_LINK") + f"&page={current_page}"
browser.get(search_link)

# Retrieve all profiles found in <li> tags
all_profiles = analyze_and_retrieve_all_profiles_li_tags(browser)

tour = 0
for profile in all_profiles:
    if tour ==4:
        break
    
    profile_link = retrieve_profile_link(profile)

    #Récupérer le nom du profil
    full_name = retrieve_full_name(profile)
    first_name = full_name.split(' ')[0]
    last_name = full_name.split(' ')[1]

    #Récupérer le span qui contient le texte "Se connecter"
    button_name = get_button_name(profile)

    if "Se connecter" in button_name or "Connect" in button_name:
        message = os.getenv("MESSAGE_TO_SEND")
        personalized_message = replace_first_name(message, first_name)

        click_connect_button(browser, profile)
        click_ajouter_note(browser)
        ecrire_message(browser, message)
        envoi_message(browser)

    #Vérifier si le profil existe dans la base de données
    cur.execute("""
         SELECT * FROM linkedin_leads WHERE linkedin_link = %s
    """, (profile_link,))
    profile_exists = cur.fetchone()

    #Si le profil n'existe pas, on l'ajoute à la base de données
    if not profile_exists:
        cur.execute("""
            INSERT INTO linkedin_leads (first_name, last_name, linkedin_link, message_sent, last_message, category, link_search_id) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (first_name, last_name, profile_link, "true", str(today), keyword_used, int(link_search_id)))
        conn.commit()
    
    # add 1 to messages_sent in database
    messages_sent += 1
    cur.execute("""
        UPDATE lead_search_links_infos SET messages_sent = %s WHERE search_link = %s
    """, (messages_sent, os.getenv("SEARCH_LINK")))
    conn.commit()
       
    tour += 1


cur.close()
conn.commit()
conn.close()
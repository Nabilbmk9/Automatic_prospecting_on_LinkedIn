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

keyword_used = retrieve_keyword_used(cur)
link_search_id = retrieve_link_search_id(cur)

# Login to linkedin
username = os.getenv("LINKEDIN_EMAIL")
password = os.getenv("LINKEDIN_PASSWORD")
browser = connection_compte(username,password)

# Go to leads search page
current_page = retrieve_current_page(cur)
search_link = os.getenv("SEARCH_LINK") + f"&page={current_page}"
browser.get(search_link)

# Retrieve all profiles found in <li> tags
all_profiles = analyze_and_retrieve_all_profiles_li_tags(browser)

for profile in all_profiles:
  
    profile_link = retrieve_profile_link(profile)
    profile_exists = check_profile_exist_in_db(cur, profile_link)
    if profile_exists:
        continue

    #Récupérer le nom du profil
    full_name = retrieve_full_name(profile)
    first_name = full_name.split(' ')[0]
    last_name = full_name.split(' ')[1]

    #Récupérer le span qui contient le texte "Se connecter"
    button_name = get_button_name(profile)

    if "Se connecter" in button_name:
        message = os.getenv("MESSAGE_TO_SEND")
        personalized_message = replace_first_name(message, first_name)

        click_connect_button(browser, profile)
        click_ajouter_note(browser)
        ecrire_message(browser, personalized_message)
        envoi_message(browser)

        insert_new_profile_in_db(cur, conn, first_name, last_name, profile_link, True, today, keyword_used, link_search_id)
        number_of_message_sent = retrieve_messages_sent(cur)+1
        update_messages_sent_in_db(cur, conn, number_of_message_sent)



cur.close()
conn.commit()
conn.close()
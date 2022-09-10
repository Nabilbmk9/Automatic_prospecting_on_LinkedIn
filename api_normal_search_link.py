from datetime import datetime
from distutils.spawn import spawn
import os
from unicodedata import category
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from selenium.webdriver.common.by import By

from api import click_ajouter_note, connection_compte, ecrire_message, envoi_message
from postgre import connect_db
from pprint import pprint

load_dotenv()

conn = connect_db()
cur = conn.cursor()

today= datetime.now().strftime("%Y-%m-%d")





search_link = os.getenv("SEARCH_LINK") + f"&page={current_page}"


#######################################################################################
def analyze_and_retrieve_all_profiles_li_tags(browser):
    soup = BeautifulSoup(browser.page_source, "html.parser")
    return soup.find_all('li', {'class': 'reusable-search__result-container'})

tour = 0
for li in all_li:
    if tour ==4:
        break
    #Récupérer le lien de chaque profil
    def retrieve_profile_link(li_tag):
        a = li_tag.find('a', {'class': 'app-aware-link'})
        return a.get('href').split('?')[0]

    #Récupérer le nom du profil
    def retrieve_full_name(li_tag):
        return li_tag.find('span', {'aria-hidden': 'true'}).text

    #Récupérer le span qui contient le texte "Se connecter"
    def get_button_name(li_tag):
        action_button = li_tag.find('button', {'class': 'artdeco-button'})
        return action_button.find('span', {'class': 'artdeco-button__text'}).text

    def replace_first_name(message, first_name):
        return message.replace("{first_name}", first_name)


    def click_connect_button(browser, li_tag):
        action_button = li_tag.find('button', {'class': 'artdeco-button'})
        id_button = action_button['id']
        browser.find_element(By.ID, id_button).click()


    if "Se connecter" in span_button:
        message = os.getenv("MESSAGE_TO_SEND")
        message = message.replace("{first_name}", first_name)
        id_button = action_button['id']
        browser.find_element(By.ID, id_button).click()
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
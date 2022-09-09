from distutils.spawn import spawn
import os
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from selenium.webdriver.common.by import By

from api import click_ajouter_note, connection_compte, ecrire_message, envoi_message
from postgre import connect_db
from pprint import pprint

load_dotenv()

conn = connect_db()
cur = conn.cursor()

username = os.getenv("LINDEDIN_EMAIL")
password = os.getenv("LINDEDIN_PASSWORD")

browser = connection_compte(username,password)

current_page = cur.execute("""
    SELECT current_page FROM lead_search_links_infos WHERE search_link = %s
""", (os.getenv("SEARCH_LINK"),))
current_page = cur.fetchone()[0]

search_link = os.getenv("SEARCH_LINK") + f"&page={current_page}"


browser.get(search_link)

#Trouver toutes les balises <li>
soup = BeautifulSoup(browser.page_source, "html.parser")
all_li = soup.find_all('li', {'class': 'reusable-search__result-container'})


for li in all_li:
    #Récupérer le lien de chaque profil
    a = li.find('a', {'class': 'app-aware-link'})
    profile_link = a.get('href').split('?')[0]

    #Récupérer le nom du profil
    full_name = li.find('span', {'aria-hidden': 'true'}).text
    first_name = full_name.split(' ')[0]
    last_name = full_name.split(' ')[1]

    #Récupérer le span qui contient le texte "Se connecter"
    action_button = li.find('button', {'class': 'artdeco-button'})
    span_button = action_button.find('span', {'class': 'artdeco-button__text'}).text

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
         SELECT * FROM linkedin_profile_infos WHERE profile_link = %s
    """, (profile_link,))
    profile_exists = cur.fetchone()

    #Si le profil n'existe pas, on l'ajoute à la base de données
    if not profile_exists:
        cur.execute("""
            INSERT INTO linkedin_profile_infos (profile_link, first_name, last_name, search_link) VALUES (%s, %s, %s, %s)
        """, (profile_link, first_name, last_name, os.getenv("SEARCH_LINK")))
        conn.commit()


cur.close()
conn.commit()
conn.close()
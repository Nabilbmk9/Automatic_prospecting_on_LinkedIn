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

cur.execute("""
    SELECT keyword_used, id FROM lead_search_links_infos WHERE search_link = %s
""", (os.getenv("SEARCH_LINK"),))
result = cur.fetchone()
keyword_used = result[0]
link_search_id = result[1]

username = os.getenv("LINKEDIN_EMAIL")
password = os.getenv("LINKEDIN_PASSWORD")

browser = connection_compte(username,password)

current_page = cur.execute("""
    SELECT current_page FROM lead_search_links_infos WHERE search_link = %s
""", (os.getenv("SEARCH_LINK"),))
current_page = cur.fetchone()[0]

messages_sent = cur.execute("""
    SELECT messages_sent FROM lead_search_links_infos WHERE search_link = %s
""", (os.getenv("SEARCH_LINK"),))
messages_sent = cur.fetchone()[0]
print(messages_sent)

search_link = os.getenv("SEARCH_LINK") + f"&page={current_page}"


browser.get(search_link)

#Trouver toutes les balises <li>
soup = BeautifulSoup(browser.page_source, "html.parser")
all_li = soup.find_all('li', {'class': 'reusable-search__result-container'})

tour = 0
for li in all_li:
    if tour ==4:
        break
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
import os, random, sys, time

import win32clipboard
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from api import connection_compte
from postgre import connect_db

load_dotenv()

conn = connect_db()
cur = conn.cursor()

username = os.getenv("LINKEDIN_USERNAME")
password = os.getenv("LINKEDIN_PASSWORD")

browser = connection_compte(username, password)

delay = 30
page = 25
save = 0

while page < 36:

    #Aller a la page du sales navigator

    browser.get(f"https://www.linkedin.com/sales/search/people?page={str(page)}&query=(recentSearchParam%3A(id%3A1550111828%2CdoLogHistory%3Atrue)%2Ckeywords%3Atech%2520recruteur)&sessionId=UymhsAxYSFSL64dmhCnbkA%3D%3D")

    WebDriverWait(browser, delay).until(EC.presence_of_element_located((By.ID, 'search-results-container')))

    # Scroller la page pour charger les profils

    for i in range(20):
        browser.execute_script("document.getElementById('search-results-container').scrollBy(0, 250)")

    
    #Rechercher tous les profiles
    soup = BeautifulSoup(browser.page_source)
    div_total = soup.find_all('li', {'class': 'artdeco-list__item'})
    #Récupérer chaque lien sales navigator des profils
    for link in div_total:
        a = link.find_all('div', {'class': 'artdeco-entity-lockup__title'})
  
        #Boucler sur chaque profils
        for x in a :
            b = x.find('a', {'class': 'ember-view'})
            link_sales_navigator = b.get('href')
            full_sales_link = "https://www.linkedin.com" + link_sales_navigator


            if Linkedin_Profile_Info.objects.filter(sales_navigator_link=full_sales_link).exists():
                continue

            browser.get(full_sales_link)

            try : 
                #Récupère l'ID des 3 petits point
                WebDriverWait(browser, delay).until(EC.presence_of_element_located((By.CLASS_NAME, 'profile-topcard-actions')))
                soup = BeautifulSoup(browser.page_source)
                petit_point = soup.find('div', {'class': 'profile-topcard-actions'})
                ID_petit_point = petit_point.select_one("button[class*=right-actions-overflow-menu-trigger]")['id']
                browser.find_element(By.ID, ID_petit_point).click()

                #Récupère l'ID du "copy link"
                copy_link_id = petit_point.select_one("div[data-control-name*=copy_linkedin]")['id']

                WebDriverWait(browser, delay).until(EC.presence_of_element_located((By.CLASS_NAME, 'inverse-link-on-a-light-background')))
                browser.find_element(By.ID, copy_link_id).click()
                time.sleep(1)

                win32clipboard.OpenClipboard()
                linkedin_link = win32clipboard.GetClipboardData() + "/"
                win32clipboard.CloseClipboard()

                if Linkedin_Profile_Info.objects.filter(linkedin_link=linkedin_link, associated_account=compte_save).exists():
                    continue

                name_div = soup.find('span', {'class': 'profile-topcard-person-entity__name t-24 t-black t-bold'})
                full_name = name_div.get_text().strip()
                first_name = full_name.split()[0]
                last_name = ' '.join(full_name.split()[1:])

                ajout_bdd = cur.execute(f"""
                    INSERT INTO linkedin_leads (first_name, last_name, linkedin_link, sales_navigator_link)
                    VALUES ('{first_name}', '{last_name}', '{linkedin_link}', '{full_sales_link}')
                """)

                save += 1
                print(f"Sauvegarde n: {save}")
                
            except:
                print("error")
                pass
      
    print(f"Page n: {page}")
    page += 1
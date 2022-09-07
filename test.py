import datetime, sys
import time, random
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from Publication.Linkedin_automation.api import click_ajouter_note, click_connect_on_actionbar, click_connect_on_page, click_connect_on_plus, click_plus, connection_compte, ecrire_message, envoi_message, error_bdd, sauvegarde_BDD
from Publication.models import Linkedin_Account, Linkedin_Profile_Info
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


compte = Linkedin_Account.objects.get(pk=3)
browser = connection_compte(compte=compte)

def connaissez_vous(browser=browser):
    #cliquer sur le boutton "We don't know each other"
    soup = BeautifulSoup(browser.page_source, "html.parser")
    action_bar = soup.find('div', {'class': 'artdeco-pill-choice-group'})
    for x in action_bar: # type: ignore
        if x.text.strip() == "We don't know each other":
            id_a_cliquer = x['id']
    
    browser.find_element_by_id(id_a_cliquer).click() # type: ignore

    #cliquer sur le bouton "se connecter"
    soup = BeautifulSoup(browser.page_source, "html.parser")
    action_bar = soup.find('div', {'class': 'artdeco-modal__actionbar'})
    for x in action_bar: # type: ignore
        if x.text.strip() == "Se connecter":
            id_seconnecter = x['id']

    browser.find_element_by_id(id_seconnecter).click() # type: ignore
    return


def message1(browser, compte):
    print("lancement du fichier Message 1 ")
    delay=15

    aujourdhui = datetime.date.today()
    message_envoye = len(Linkedin_Profile_Info.objects.filter(last_message=aujourdhui, associated_account=compte))

    profil_a_visiter = Linkedin_Profile_Info.objects.filter(error=False, message_sent=False, associated_account=compte)

    #Boucle de message
    for profil in profil_a_visiter:

        if message_envoye > compte.message_send:
            print(f"Tu as déjà envoyé {message_envoye} aujourd'hui pour le compte {compte.linkedin_account}")
            return

        print(f"Nombre de message envoyé ajd : {message_envoye} pour le compte {compte.linkedin_account}")

        Message = compte.message1
        if '{first_name}' in Message:
            Message = Message.replace('{first_name}', profil.first_name)

        try : 
            browser.get("https://www.linkedin.com/in/stephanie-pradon-62b67415/")
            WebDriverWait(browser, delay).until(EC.presence_of_element_located((By.CLASS_NAME, 'pv-top-card-v2-ctas')))
        
        except:
            error_bdd(profil=profil)
            print("error")
            continue

        try: #Essaye de cliquer sur le "Se connecter" de la page
            soup = BeautifulSoup(browser.page_source, 'html.parser')
            zone = soup.find('div', {'class': 'ph5'})
            text = zone.select_one("span[class*=artdeco-button__text]").text.strip() # type: ignore
            if text == "Se connecter":
                click_connect_on_page(browser=browser)
                click_ajouter_note(browser=browser)
                ecrire_message(browser=browser, message=Message)
                envoi_message(browser=browser)
                sauvegarde_BDD(profil=profil, associated_account=compte)

                message_envoye = len(Linkedin_Profile_Info.objects.filter(last_message=aujourdhui, associated_account=compte))
                time.sleep(random.uniform(12, 30))
                continue
            else:
                text = zone.select_one("spsdgfsdgsdggsn__text]").text.strip() # type: ignore

        except:
            try: #Essayer de se connetcer en passant par le "Plus"
                click_plus(browser=browser)
                click_connect_on_plus(browser=browser)

                try:
                    connaissez_vous(browser=browser)
                    click_connect_on_actionbar(browser)
                    click_ajouter_note(browser=browser)
                except:
                    click_ajouter_note(browser=browser)

                ecrire_message(browser=browser, message=Message)
                envoi_message(browser=browser)
                sauvegarde_BDD(profil=profil, associated_account=compte)

                message_envoye = len(Linkedin_Profile_Info.objects.filter(last_message=aujourdhui, associated_account=compte))
                time.sleep(random.uniform(12, 30))
                continue
            except:   
                error_bdd(profil=profil)
                print("error")
                continue
            
    return message_envoye

message1(browser=browser, compte=compte)
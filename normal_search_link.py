from datetime import datetime
from distutils.spawn import spawn
import os, time, random
from unicodedata import category
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from selenium.webdriver.common.by import By

from api import click_ajouter_note, click_connect_on_actionbar, click_connect_on_plus, click_plus, connaissez_vous, connection_compte, ecrire_message, envoi_message
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

max_messages_per_day = int(os.getenv("MAX_MESSAGES_PER_DAY"))
messages_sent_today = retrieve_nb_messages_sent_by_date(cur, today)


while messages_sent_today < max_messages_per_day:

    # Go to leads search page
    current_page = retrieve_current_page(cur)
    search_link = os.getenv("SEARCH_LINK") + f"&page={current_page}"
    browser.get(search_link)

    # Retrieve all profiles found in <li> tags
    all_profiles = analyze_and_retrieve_all_profiles_li_tags(browser)

    for profile in all_profiles:
        messages_sent_today = retrieve_nb_messages_sent_by_date(cur, today)
        if messages_sent_today >= max_messages_per_day:
            print(f"Maximum messages sent per day reached : {messages_sent_today} ")
            exit()

        try :
            profile_link = retrieve_profile_link(profile)
            profile_exists = check_profile_exist_in_db(cur, profile_link)
            if profile_exists:
                continue

            # Retrieve profile name
            full_name = retrieve_full_name(profile)
            first_name = full_name.split(' ')[0]
            last_name = full_name.split(' ')[1]

            # Retrieve action button "Connect" or "Follow"
            button_name = get_button_name(profile)
            message = os.getenv("MESSAGE_TO_SEND")
            personalized_message = replace_first_name(message, first_name)

            if "Se connecter" in button_name:
                click_connect_button(browser, profile)
                try:
                    connaissez_vous(browser)
                except:
                    pass
                try:
                    click_connect_on_actionbar(browser)
                    click_ajouter_note(browser)
                except:
                    click_ajouter_note(browser)
                click_ajouter_note(browser)
                ecrire_message(browser, personalized_message)
                envoi_message(browser)

                insert_new_profile_in_db(cur, conn, first_name, last_name, profile_link, True, today, keyword_used, link_search_id)
                number_of_message_sent = retrieve_messages_sent(cur)+1
                update_messages_sent_in_db(cur, conn, number_of_message_sent)

            elif "Suivre" in button_name or "Message" in button_name:
                browser.get(profile_link)
                click_plus(browser)
                click_connect_on_plus(browser)
                try:
                    connaissez_vous(browser)
                except:
                    pass
                try:
                    click_connect_on_actionbar(browser)
                    click_ajouter_note(browser)
                except:
                    click_ajouter_note(browser)

                ecrire_message(browser, personalized_message)
                envoi_message(browser)
                insert_new_profile_in_db(cur, conn, first_name, last_name, profile_link, True, today, keyword_used, link_search_id)
                number_of_message_sent = retrieve_messages_sent(cur)+1
                update_messages_sent_in_db(cur, conn, number_of_message_sent)
                search_link = os.getenv("SEARCH_LINK") + f"&page={current_page}"
                browser.get(search_link)
        except:
            continue

        print(f"Message sent today : {int(messages_sent_today)+1}")
        time.sleep(random.randint(10, 20))
        
    # Update current page in db
    update_current_page_in_db(cur, conn, current_page+1)

cur.close()
conn.commit()
conn.close()
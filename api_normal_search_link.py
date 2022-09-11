from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By


def analyze_and_retrieve_all_profiles_li_tags(browser):
    soup = BeautifulSoup(browser.page_source, "html.parser")
    return soup.find_all('li', {'class': 'reusable-search__result-container'})

def retrieve_profile_link(li_tag):
    a = li_tag.find('a', {'class': 'app-aware-link'})
    return a.get('href').split('?')[0]

def retrieve_full_name(li_tag):
    return li_tag.find('span', {'aria-hidden': 'true'}).text

def get_button_name(li_tag):
    action_button = li_tag.find('button', {'class': 'artdeco-button'})
    return action_button.find('span', {'class': 'artdeco-button__text'}).text

def replace_first_name(message, first_name):
    return message.replace("{first_name}", first_name)

def click_connect_button(browser, li_tag):
    action_button = li_tag.find('button', {'class': 'artdeco-button'})
    id_button = action_button['id']
    browser.find_element(By.ID, id_button).click()

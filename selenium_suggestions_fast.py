import os
import time
from random import randint, choice

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import trio
import numpy as np
import scipy.interpolate as si
from selenium_stealth import stealth
import traceback
import sys

from utils.utils import sleep_func, init_stealth_browser, log_in, click_on_search_menu, read_csv_line_by_line, \
    is_profile, append_unique

"""
    Selenium with firefox, avoid detection test

    Source: https://www.zenrows.com/blog/selenium-avoid-bot-detection#ip-rotation-proxy

    Proxy: https://www.zenrows.com/pricing

    GET TO: https://www.instagram.com/api/v1/web/search/topsearch/?context=blended&include_reel=true&query=cooking women&rank_token=0.287621384898462&search_surface=web_top_search

"""


def get_suggested_accounts(wait_func):
    _all_buttons = wait_func.until(
        EC.presence_of_all_elements_located((By.XPATH, "//div[@role='button']//div//*[local-name()='svg']")))
    # There is suggested accounts button
    if len(_all_buttons) > 1:
        suggestion_btn = _all_buttons[-2]
        return suggestion_btn
    else:
        return None


def enter_search_text(wait_func, search_text):
    """
        Assumes search menu is already open.
        Enters @search_text to input field
    """
    input_field = wait_func.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Search']")))
    # Enter keyword
    input_field.send_keys(search_text)
    sleep_func(2, 3)


def search_suggested_accounts_fast(browser):
    # Screen size
    print(browser.get_window_size())
    s = browser.get_window_size()
    MAXX, MAXY = s['width'], s['height']
    # Browser actions
    ACTION = ActionChains(browser)
    wait = WebDriverWait(browser, 5)

    ###########################################################################
    # Log in and accept cookies

    log_in(a=ACTION, w=wait, usr_name=USERNAME, passw=PASSWORD, maxx=MAXX, maxy=MAXY)
    print('Log in succesful!')

    for idx, profile in enumerate(profiles_key_word):
        print(f'{100 * idx / len(profiles_key_word)}% - Searching profile: {profile}')
        # Open profile page
        browser.get(BASE_URL + "/" + profile)
        # Check if suggestions are open:
        suggested_closed = True
        try:
            suggestion_title = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div//div//span//div")))
            for title in suggestion_title:
                if title.text == "Suggested":
                    suggested_closed = False
                    break
        except:
            pass
        print(f'suggested_closed: {suggested_closed}')
        # Try to find suggested account button (if not found, skip account)
        btn = None
        try:
            if suggested_closed:
                print('SUGGESTED ACCOUNTS')
                btn = get_suggested_accounts(wait)
                # human_mouse_movement(start=mouse_loc, dest=btn.location)
                if type(btn) != WebElement:
                    raise ValueError(f'Suggestion button not found for: {profile}')
        except:
            print(f'Could not press suggested button for: {profile}. Continuing')
            append_unique(BASE_FOLDER + "/" + CHECKPOINT_FILE, [profile])
            print('Open search again')
            click_on_search_menu(wait, ACTION)
            continue
        # Try to press suggested account button (if can't press, try later)
        if suggested_closed:
            ACTION.move_to_element(btn)
            ACTION.click()
            ACTION.perform()
            sleep_func(2, 3)

        profiles_suggested = []
        result = None
        suggested_idx = 0
        while result is None:
            try:
                # get all link
                all_links = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//a[text() or *]")))
                tmp = []
                for link in all_links:
                    href = link.get_attribute('href')
                    if is_profile(href):
                        tmp.append(href.replace('https://www.instagram.com', '').replace('/', ''))

                profiles_suggested.extend(tmp)

                print('Clicking next: ')
                # click on right, get all links
                right_button = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//button[@aria-label='Next']")))[-1]  # Reels can also have this button..
                ACTION.move_to_element(right_button)
                ACTION.click()
                ACTION.perform()
                sleep_func(2, 3)  # longer wait for animation
                suggested_idx += 1
            except Exception as ex:
                print('Not found any more suggested profies')
                result = ex
                pass
        # Keep only unique
        profiles_suggested = list(set(profiles_suggested))
        print('profiles so far')
        print(profiles_suggested)
        # Save progress
        new_n = append_unique(BASE_FOLDER + "/" + SAVE_FILE, profiles_suggested)
        print(f'Result increased to: {profile} | {new_n}')
        # Save Checkpoint
        append_unique(BASE_FOLDER + "/" + CHECKPOINT_FILE, [profile])


# Parameters
BASE_URL = 'https://www.instagram.com'
CHECKPOINT_FILE = 'checkpoint_profiles_done.csv'
SAVE_FILE = 'suggested_profiles.csv'
MAX_TRIES = 100

profiles_key_word = []
profiles_suggested = []

if __name__ == '__main__':
    USERNAME = sys.argv[1]
    PASSWORD = sys.argv[2]
    BASE_FOLDER = sys.argv[3]
    KEY_WORD_SEARCH_FILE = sys.argv[4]

    driver = None
    for i in range(MAX_TRIES):
        print(f'TRY: {i}')
        try:
            ###########################################################################
            # Load profiles and checkpoint
            profiles_key_word = read_csv_line_by_line(BASE_FOLDER + "/" + KEY_WORD_SEARCH_FILE)

            print(f'Total number of profiles from keyword search: {len(profiles_key_word)}')

            # Continue from checkpoint
            lines = []

            if os.path.isfile(BASE_FOLDER + "/" + CHECKPOINT_FILE):
                lines = read_csv_line_by_line(BASE_FOLDER + "/" + CHECKPOINT_FILE)
            else:
                with open(BASE_FOLDER + "/" + CHECKPOINT_FILE, "w") as my_empty_csv:
                    pass

            profiles_key_word = [x for x in profiles_key_word if x not in lines]

            print(f'Profiles left: {len(profiles_key_word)}')
            ###########################################################################
            # INIT WEB BROWSER
            driver = init_stealth_browser()
            driver.get(BASE_URL)
            # Find suggested
            search_suggested_accounts_fast(driver)
        except:
            print('Fatal error, logging out')
            if driver is not None:
                driver.quit()
            traceback.print_exception(*sys.exc_info())
            time.sleep(5)
            pass
    driver.close()
    print("Saved search result")
    print(profiles_suggested)

"""
    Get information from profiles when logged out

    Useful: setTimeout(function(){debugger;},5000);
"""
import csv
import sys
import time
import traceback
from random import randint
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import numpy as np
from selenium_stealth import stealth

from utils.utils import sleep_func, init_stealth_browser, log_in, check_if_contained, append_unique


def has_numbers(inputString):
    return any(char.isdigit() for char in inputString)


def extract_one_profile(browser, usr_name):
    # Load profile page

    print('LOADING')
    print(BASE_URL + usr_name + "/")

    browser.get(BASE_URL + usr_name + "/")
    time.sleep(2)

    # Main profile info
    print('Searching main profile info')
    main_info = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//ul//li//span//span")))
    _pos = main_info[0].location

    n_posts = main_info[0].text
    n_followers = main_info[1].text
    n_following = main_info[2].text
    post_data = []
    # Is it a private profile ?
    # Get all links
    print('Searching all links')
    all_links = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//a[text() or *]")))
    post_links = []
    idx = 0
    for link in all_links:
        href = link.get_attribute('href')
        if "/p/" in href:
            idx += 1
            # Robot movement
            ACTION.move_to_element(link)
            ACTION.perform()
            time.sleep(2)
            # Extract post data
            main_info = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//ul//li//span//span")))
            like_text = main_info[-2].text
            comment_text = main_info[-1].text
            # likes
            if has_numbers(like_text):
                post_data.append(like_text)
            else:
                post_data.append('0')
            # comments
            if has_numbers(comment_text):
                post_data.append(comment_text)
            else:
                post_data.append('0')

            if idx >= 12:
                break
            # TODO if idx % 3 == 1, save prev pos, then in next round, idx% 3 == 2, move mouse, also in idx%3 == 0, move mouse
    print(f'Saving: {username} -> post_data: {post_data}')
    # Save profile info
    lines = []
    with open(BASE_FOLDER + "/" + RESULTS_FILE, 'r') as f:
        lines.extend([line.rstrip() for line in f])

    row = f'{username};{n_posts};{n_followers};{n_following}'
    for post in post_data:
        try:
            if 'K' in post:
                post = post.replace('K', '')
                post = str(float(post) * 1000)
            if 'M' in post:
                post = post.replace('M', '')
                post = str(float(post) * 1000000)
        except:
            pass
        row += f';{post}'

    lines.append(row)

    with open(BASE_FOLDER + "/" + RESULTS_FILE, mode='w', encoding="utf-8") as f:
        for line in lines:
            if line != "":
                f.write(f"{line}\n")


if __name__ == '__main__':
    USERNAME = sys.argv[1]
    PASSWORD = sys.argv[2]
    BASE_FOLDER = sys.argv[3]
    KEY_WORD_SEARCH_FILE = sys.argv[4]
    SUGGESTED_ACCOUNTS_FILE = 'suggested_profiles.csv'
    RESULTS_FILE = 'results.csv'
    BASE_URL = "https://www.instagram.com/"
    HEADER = "user_name;n_posts;n_followers;n_following;likes_1;comments_1;likes_2;comments_2;likes_3;comments_3;likes_4;comments_4;likes_5;comments_5;likes_6;comments_6;likes_7;comments_7;likes_8;comments_8;likes_9;comments_9;likes_10;comments_10;likes_11;comments_11;likes_12;comments_12"
    ###########################################################################
    # Read profile name information

    all_profiles = []

    # Keyword result
    with open(BASE_FOLDER + "/" + KEY_WORD_SEARCH_FILE, 'r') as file:
        all_profiles.extend([line.rstrip() for line in file])

    # Account suggestions

    with open(BASE_FOLDER + "/" + SUGGESTED_ACCOUNTS_FILE, 'r') as file:
        all_profiles.extend([line.rstrip() for line in file])

    all_profiles = list(set(all_profiles))

    print(f'Total profiles: {len(all_profiles)}')

    ###########################################################################
    MAX_TRIES = 100
    driver = None
    for i in range(MAX_TRIES):
        print(f'TRY: {i}')
        try:
            # INIT WEB BROWSER
            driver = init_stealth_browser()
            driver.get(BASE_URL)
            # Screen size
            print(driver.get_window_size())
            s = driver.get_window_size()
            MAXX, MAXY = s['width'], s['height']
            # Browser actions
            ACTION = ActionChains(driver)
            wait = WebDriverWait(driver, 5)

            ###########################################################################
            # Log in and accept cookies

            log_in(a=ACTION, w=wait, usr_name=USERNAME, passw=PASSWORD, maxx=MAXX, maxy=MAXY)
            print('Log in succesful!')
            time.sleep(2)
            for count, username in enumerate(all_profiles):
                print(f'{100 * count / len(all_profiles)}% - Searching profile: {username}')

                if check_if_contained(BASE_FOLDER + "/" + RESULTS_FILE, username, add_header=HEADER):
                    continue

                extract_one_profile(driver, username)
                time.sleep(1)
        except:
            print('Fatal error, logging out')
            if driver is not None:
                driver.quit()
            traceback.print_exception(*sys.exc_info())
            time.sleep(5)
            pass

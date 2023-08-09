import sys
from datetime import datetime
from bs4 import BeautifulSoup
from selenium.webdriver import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from utils.utils import enter_search_text, is_profile, sleep_func, init_stealth_browser, read_csv_line_by_line, \
    click_on_search_menu, log_in
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

if __name__ == '__main__':
    BASE_URL = 'https://www.instagram.com'
    USERNAME = sys.argv[1]
    PASSWORD = sys.argv[2]
    BASE_FOLDER = sys.argv[3]
    KEYWORD_FILE = sys.argv[4]
    # Search terms
    key_words = read_csv_line_by_line(BASE_FOLDER + "/" + KEYWORD_FILE)
    # Result
    profiles_key_word = []
    # Init browser
    browser = init_stealth_browser()
    browser.get(BASE_URL)
    # Screen size
    print(browser.get_window_size())
    s = browser.get_window_size()
    MAXX, MAXY = s['width'], s['height']
    # Browser actions
    ACTION = ActionChains(browser)
    wait = WebDriverWait(browser, 5)
    # Log in

    log_in(a=ACTION, w=wait, usr_name=USERNAME, passw=PASSWORD, maxx=MAXX, maxy=MAXY)

    click_on_search_menu(wait, ACTION)

    # Search for all keywords
    for search_key in key_words:
        # Locate search input
        enter_search_text(wait, search_key)

        # Save search result
        _ = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@role='none']")))   # Async wait for search result
        soup = BeautifulSoup(browser.page_source, "html.parser")

        tmp = []
        for link in soup.find_all('a', href=True):
            if is_profile(link['href']):
                tmp.append(link['href'].replace('/', ''))
        profiles_key_word = profiles_key_word + tmp
        print(f'Searching {search_key}. Found: {len(tmp)} profiles')
        print(profiles_key_word)
        sleep_func(2, 3)
        # Clear search
        clear_button = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@aria-label='Clear the search box']")))
        ACTION.move_to_element(clear_button)
        ACTION.click()
        ACTION.perform()
        sleep_func(2, 3)

    browser.close()

    # Save results
    sttime = datetime.now().strftime('%Y%m%d_%H_%M_%S')
    with open(f'{BASE_FOLDER}/key_word_search_{sttime}.csv', 'w') as f:
        for line in profiles_key_word:
            f.write(f"{line}\n")


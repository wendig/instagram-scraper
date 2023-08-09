import os
import time
from random import randint
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import numpy as np
from selenium_stealth import stealth


def sleep_func(a, b):
    time.sleep(randint(a, b))


def is_profile(str_link):
    """
        From all links on page, filter profile links

        Example profile:
            /cooking_womens/
        Not profiles:
            /?next=%2Fnike%2F
            #
            /explore/tags/cookingwomenofennis/
            https://about.meta.com/
            reels?next=%2Fnike%2F
    """
    # When absolute path, remove beginning
    if 'https://www.instagram.com' in str_link:
        str_link = str_link.replace('https://www.instagram.com', '')
    # Hashtag link
    non_profile_tags = [
        "/explore/", "https://", "reels?next", "?next=", "/p/", "/followers/",
        "/tagged/", "/similar_accounts/", "/following/", "/reels/", "/directoryprofiles/"
    ]

    for item in non_profile_tags:
        if item in str_link:
            return False

    # Profile link
    if str_link.startswith('/') and str_link.endswith('/'):
        return True
    # Default
    return False


def enter_search_text(wait_func, search_text):
    """
        Assumes search menu is already open.
        Enters @search_text to input field
    """
    input_field = wait_func.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Search']")))
    # Enter keyword
    input_field.send_keys(search_text)
    sleep_func(2, 3)


def log_in(a: ActionChains, w: WebDriverWait, usr_name, passw, min_wait=1, maxx=1600, maxy=1200):
    # Allow all cookies
    _pos = None
    try:
        print('> Locating: Allow cookies')
        allow_cookies = get_button_by_text(w, "Allow all cookies", "//button[@tabindex='0']")
        _pos = allow_cookies.location
        a.move_to_element(allow_cookies)
        a.click()
        a.perform()
        sleep_func(min_wait + 2, 3)
        # Navigate to log in page
    except:
        print('Allow cookies not found')
        pass
    # enter user name and pass
    enter_login(w, usr_name, passw)
    # press log in again
    print('> Locating: Login 2')
    log_in_button_2 = w.until(EC.presence_of_element_located((By.XPATH, "//button[@type='submit']")))
    if _pos is not None:
        human_mouse_movement(a, _pos, log_in_button_2.location, maxx, maxy)
    a.move_to_element(log_in_button_2)
    a.click()
    a.perform()
    sleep_func(min_wait, 1)
    # Dont ask for notifications
    # try:
    #    print('> Locating: Allow cookies')
    #    allow_cookies = get_button_by_text(w, "Allow all cookies", "//button[@tabindex='0']")
    #    _pos = allow_cookies.location
    #    a.move_to_element(allow_cookies)
    #    a.click()
    #    a.perform()
    #    sleep_func(min_wait + 2, 3)
    #    # Navigate to log in page
    # except:
    #    print('Did not ask for allow notification')
    #    pass

    return True


def random_control_points(start_point, end_point, size):
    """Generate random control points for the Bézier curve."""
    mid_point = (start_point + end_point) / 2
    control_point_1 = mid_point + np.random.randn(2) * size
    control_point_2 = mid_point + np.random.randn(2) * size
    return control_point_1, control_point_2


def generate_bezier_curve(start_point, end_point, control_point_1, control_point_2, num_points=10):
    """Generate Bézier curve points."""
    t = np.linspace(0, 1, num_points)
    x = (1 - t) ** 3 * start_point[0] + 3 * (1 - t) ** 2 * t * control_point_1[0] + 3 * (1 - t) * t ** 2 * \
        control_point_2[0] + t ** 3 * end_point[0]
    y = (1 - t) ** 3 * start_point[1] + 3 * (1 - t) ** 2 * t * control_point_1[1] + 3 * (1 - t) * t ** 2 * \
        control_point_2[1] + t ** 3 * end_point[1]
    return x, y


def human_mouse_movement(a: ActionChains, start, dest, max_x, max_y, steps=15):
    print('Moving mouse, please wait...')
    # Define the endpoints
    start_point = np.array([start['x'], start['y']])
    end_point = np.array([dest['x'], dest['y']])

    # Define the fixed size for control points
    size = 10

    # Generate random control points
    control_point_1, control_point_2 = random_control_points(start_point, end_point, size)

    # Generate Bézier curve points
    x_curve, y_curve = generate_bezier_curve(start_point, end_point, control_point_1, control_point_2, num_points=steps)

    pos_x, pos_y = start['x'], start['y']
    for x, y in zip(x_curve, y_curve):
        if (x != pos_x or y != pos_y) and x >= 0 and y >= 0 and x <= max_x and y <= max_y:
            a.move_by_offset(x - pos_x, y - pos_y)
            a.perform()
            pos_x, pos_y = x, y
    print('Moving mouse done.')


def enter_login(wait_func, usr, passw):
    username_field = wait_func.until(EC.presence_of_element_located((By.XPATH, "//input[@name='username']")))
    password_field = wait_func.until(EC.presence_of_element_located((By.XPATH, "//input[@name='password']")))
    # Enter keyword
    username_field.send_keys(usr)
    password_field.send_keys(passw)
    sleep_func(3, 5)

    return


def get_log_in(wait_func):
    _all_links = wait_func.until(EC.presence_of_all_elements_located((By.XPATH, "//a[text() or *]")))

    for _link in _all_links:
        _href = _link.get_attribute('href')
        if "accounts/login" in _href and "source=desktop_nav" in _href:
            return _link


def get_button_by_text(wait_func, button_text, x_path_expr):
    """
        Search all buttons for specific text
    """
    all_buttons = wait_func.until(EC.presence_of_all_elements_located((By.XPATH, x_path_expr)))
    for button in all_buttons:
        if button.text == button_text:
            # First, go to your start point or Element:
            return button
    raise Exception(f'Button: {button_text} with expression {x_path_expr} not found.')


def init_stealth_browser():
    options = webdriver.ChromeOptions()
    options.add_argument("start-maximized")
    # options.add_argument("--headless")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    driver = webdriver.Chrome(options=options, keep_alive=True)

    stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
            )
    return driver


def click_on_search_menu(wait_func, a: ActionChains, sleep_time=1):
    for count, item in enumerate(
            wait_func.until(EC.presence_of_all_elements_located((By.XPATH, "//span[@aria-describedby]")))):
        if count == 1:
            a.move_to_element(item)
            a.click()
            a.perform()
            time.sleep(sleep_time)


def read_csv_line_by_line(file_name):
    with open(file_name, 'r', encoding='utf8') as f:
        return [line.rstrip() for line in f]


def append_unique(file_path, list_in):
    lines = []

    # Read already saved usernames
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            lines.extend([line.rstrip() for line in file])

    lines = list(set(list_in + lines))

    # Save new usernames
    with open(file_path, 'w') as f:
        for line in lines:
            if line != "":
                f.write(f"{line}\n")

    return len(lines)


def check_if_contained(file_path, item, add_header=""):
    found = False

    if not os.path.exists(file_path):
        with open(file_path, 'w') as f:
            if add_header != "":
                f.write(f"{add_header}\n")
            pass
        return False

    with open(file_path, 'r') as f:
        lines = [line.rstrip() for line in f]
        for line in lines:
            if item in line:
                found = True
                break
    return found

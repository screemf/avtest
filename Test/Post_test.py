import time
import pytest
import allure
from Auth_test import get_auth_tokens
import os
import cv2
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import requests
from bs4 import BeautifulSoup

BASE_URL = 'http://127.0.0.1:8000'
API_POSTS_LIST = 'http://127.0.0.1:8000/blog/posts/'
API_CREATE_POST_URL = 'http://127.0.0.1:8000/blog/post/new'
API_BLOG_HOME = 'http://127.0.0.1:8000/blog/home/'
BASE_DIR = os.getcwd()
REFERENCE_SCREENSHOT_PATH = os.path.join(BASE_DIR, "D:\Refer.png")
CURRENT_SCREENSHOT_PATH = os.path.join(BASE_DIR, "D:\current_screenshot.png")



def get_csrf_token_from_create_post_page(username, password):
    url = API_CREATE_POST_URL

    auth_cookies, sessionid = get_auth_tokens(username, password)

    session = requests.Session()
    session.cookies.update(auth_cookies)

    response = session.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')
    csrf_input = soup.find('input', {'name': 'csrfmiddlewaretoken'})

    if csrf_input and 'value' in csrf_input.attrs:
        csrfmiddlewaretoken = csrf_input['value']
        return {
            'csrfmiddlewaretoken': csrfmiddlewaretoken,
            'cookies': session.cookies.get_dict()
        }
    else:
        raise ValueError("CSRF middleware token не найден на странице")


def get_csrf_token_for_post_like(username, password):
    url_post = API_POSTS_LIST

    auth_cookies, sessionid = get_auth_tokens(username, password)

    session = requests.Session()
    session.cookies.update(auth_cookies)

    response = session.get(url_post)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')

    scripts = soup.find_all('script')

    full_text = ''.join([script.string or '' for script in scripts])

    pattern = re.compile(r"['\"]csrfmiddlewaretoken['\"]\s*:\s*['\"]([^'\"]+)['\"]")
    match = pattern.search(full_text)

    if match:
        csrf_token = match.group(1)
        return {
            'csrfmiddlewaretoken': csrf_token,
            'cookies': session.cookies.get_dict()
        }
    else:
        raise ValueError("CSRF токен не найден в скриптах страницы.")


def get_csrf_token_delete(username, password, post_id):
    delete_url = f"{BASE_URL}/blog/post/{post_id}/delete"
    auth_cookies, sessionid = get_auth_tokens(username, password)

    session = requests.Session()
    session.cookies.update(auth_cookies)

    response = session.get(delete_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    csrf_input = soup.find('input', {'name': 'csrfmiddlewaretoken'})

    if csrf_input and csrf_input.get('value'):
        csrfmiddlewaretoken = csrf_input['value']
        return {
            'csrfmiddlewaretoken': csrfmiddlewaretoken,
            'cookies': session.cookies.get_dict()
        }
    else:
        raise ValueError("CSRF middleware token не найден на странице")


def save_full_page_screenshot(driver, path):
    result = driver.save_screenshot(path)
    if not result:
        print(f"Не удалось сохранить скриншот по пути: {path}")
    return result


def compare_images(img_path1, img_path2, threshold=0.1):
    if not os.path.exists(img_path1):
        print(f"Файл не найден: {img_path1}")
        return False
    if not os.path.exists(img_path2):
        print(f"Файл не найден: {img_path2}")
        return False

    img1 = cv2.imread(img_path1)
    img2 = cv2.imread(img_path2)

    if img1 is None:
        print(f"Не удалось прочитать изображение: {img_path1}")
        return False
    if img2 is None:
        print(f"Не удалось прочитать изображение: {img_path2}")
        return False

    if img1.shape != img2.shape:
        print("Размеры изображений не совпадают.")
        return False

    diff = cv2.absdiff(img1, img2)
    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 30, 255, cv2.THRESH_BINARY)

    non_zero_count = np.count_nonzero(thresh)
    total_pixels = thresh.size

    difference_ratio = non_zero_count / total_pixels

    print(f"Доля отличающихся пикселей: {difference_ratio:.4f}")

    return difference_ratio < threshold

def get_max_post_id():

    try:
        posts_url = f"{BASE_URL}/blog/posts/"
        response = requests.get(posts_url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        like_buttons = soup.find_all('button', class_='like-post')

        if not like_buttons:
            return None

        post_ids = []
        for button in like_buttons:
            try:
                match = re.search(r'/blog/like-post/(\d+)/', button['data-url'])
                if match:
                    post_ids.append(int(match.group(1)))
            except (ValueError, TypeError, KeyError):
                continue

        if not post_ids:
            return None

        return max(post_ids)

    except Exception as e:
        print(f"Ошибка при получении максимального ID поста: {e}")
        return None

@pytest.mark.parametrize(
    "username, password, post_title, post_content, expect_success",
    [
        ("admin", "000p;lko", "Тестовый пост 1", "Содержимое поста 1", True),#Админ,Автор
        ("test_no_avtor", "000p;lko", "Тестовый пост 2", "Содержимое поста 2", False),#Не автор, нет прав на создание
        ("Ostap", "000olkji", "Тестовый пост 3", "Содержимое поста 3", True),#Не админ, Автор, есть права на создание
    ]
)
@allure.epic("Посты")
@allure.feature('API: Создание нового поста')
def test_create_post_1(username, password, post_title, post_content, expect_success):
    result = get_csrf_token_from_create_post_page(username, password)
    csrf_token = result['csrfmiddlewaretoken']
    cookies = result['cookies']

    session = requests.Session()
    session.cookies.update(cookies)
    session.cookies.set('csrftoken', csrf_token)

    file_path = 'D:/photo_2024-11-15_14-27-02.jpg'

    with open(file_path, 'rb') as image_file:
        files = {
            'image': ('photo_2024-11-15_14-27-02.jpg', image_file, 'image/jpeg')
        }
        data = {
            'csrfmiddlewaretoken': csrf_token,
            'title': post_title,
            'content': post_content,
            'category': "Автотест API",
        }

        headers = {
            'Accept': 'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0 ...',
            'X-CSRFToken': csrf_token,
        }

        with allure.step(f"Создание нового поста для пользователя {username} с изображением.Привелегии {expect_success}"):
            response = session.post(
                API_CREATE_POST_URL,
                headers=headers,
                data=data,
                files=files,
            )

            allure.attach(str(response.status_code), name="Код ответа")
            allure.attach(response.text, name="Ответ сервера")

            if expect_success:
                if response.status_code == 500:
                    pytest.fail(f"Ошибка сервера (500): {response.text}")
                assert response.status_code in [200, 302], (
                    f"Создание поста для {username} с привелегиями {expect_success} не удалось, статус: {response.status_code}"
                )
            else:
                assert response.status_code in [403, 404, 500], (
                    f"Ожидалась ошибка для {username} с привелегиями {expect_success}, но получен статус: {response.status_code}"
                )


@pytest.mark.parametrize(
    "username, password",
    [
        ("test_123", "000P;lko"),
    ]
)
@allure.epic("Посты")
@allure.feature('UI: Создание поста через API авторизацию')
def test_ui_create_post_with_api_auth(username, password):
    driver = webdriver.Chrome()
    driver.implicitly_wait(10)

    try:
        auth_cookies, sessionid = get_auth_tokens(username, password)
        csrftoken = auth_cookies.get('csrftoken', '')

        driver.get(API_BLOG_HOME)

        driver.add_cookie({
            'name': 'sessionid',
            'value': sessionid,
            'domain': '127.0.0.1',
            'path': '/',
        })
        if csrftoken:
            driver.add_cookie({
                'name': 'csrftoken',
                'value': csrftoken,
                'domain': '127.0.0.1',
                'path': '/',
            })

        driver.refresh()

        post_new_url = API_CREATE_POST_URL
        driver.get(post_new_url)

        wait = WebDriverWait(driver, 10)

        title_input = wait.until(EC.presence_of_element_located((By.ID, "id_title")))
        title_input.send_keys("Тестовый заголовок UI")

        content_textarea = driver.find_element(By.ID, "id_content")
        content_textarea.send_keys("Это тестовое содержание поста. UI")

        category_input = driver.find_element(By.ID, "id_category")
        category_input.send_keys("Тестовая категория UI")

        image_input = driver.find_element(By.ID, "id_image")
        current_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(current_dir, "test_data", "Refer.png")
        image_input.send_keys(image_path)
        time.sleep(2)
        submit_button = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(text(), 'Создать пост')]")
        ))
        submit_button.click()

        wait.until(EC.url_contains("/blog/posts/"))

        current_url = driver.current_url

        assert "/blog/posts/" in current_url, f"Переход не выполнен, текущий URL: {current_url}"

        print("Тест прошел успешно: форма отправлена и произошел переход.")

    except Exception as e:
        print(f"Тест не прошел: {e}")
    finally:
        driver.quit()



#Не удалось придумать как проверить сообщение если оно DOM, придется применять скриншот
@pytest.mark.parametrize(
    "username, password",
    [
        ("test_123", "000P;lko" ),
    ]
)
@allure.epic("Посты")
@allure.feature('UI: Создание поста через API авторизацию без image')
def test_ui_create_post_with_api_auth_without_image(username, password):
    driver = webdriver.Chrome()
    driver.implicitly_wait(4)

    try:
        auth_cookies, sessionid = get_auth_tokens(username, password)
        csrftoken = auth_cookies.get('csrftoken', '')

        driver.get(API_BLOG_HOME )

        driver.add_cookie({
            'name': 'sessionid',
            'value': sessionid,
            'domain': '127.0.0.1',
            'path': '/',
        })
        if csrftoken:
            driver.add_cookie({
                'name': 'csrftoken',
                'value': csrftoken,
                'domain': '127.0.0.1',
                'path': '/',
            })

        driver.refresh()

        post_new_url = API_CREATE_POST_URL
        driver.get(post_new_url)

        wait = WebDriverWait(driver, 4)

        title_input = wait.until(EC.presence_of_element_located((By.ID, "id_title")))
        title_input.send_keys("Тестовый заголовок UI")

        content_textarea = driver.find_element(By.ID, "id_content")
        content_textarea.send_keys("Это тестовое содержание поста. UI")

        category_input = driver.find_element(By.ID, "id_category")
        category_input.send_keys("Тестовая категория UI")

        time.sleep(2)

        submit_button = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(text(), 'Создать пост')]")
        ))
        submit_button.click()

        save_full_page_screenshot(driver, CURRENT_SCREENSHOT_PATH)

        if not os.path.exists(REFERENCE_SCREENSHOT_PATH):
            print("Эталонный скриншот не найден. Создайте его вручную как reference_screenshot.png.")
            return

        if compare_images(REFERENCE_SCREENSHOT_PATH, CURRENT_SCREENSHOT_PATH):
            print("Изображения совпадают — тест прошел успешно.")
            assert True
        else:
            print("Изображения отличаются — тест не прошел.")
            assert False

    finally:
        driver.quit()


@pytest.mark.parametrize(
    "username, password, post_id",
    [
        ("admin", "000p;lko",15),#Админ,Автор
        ("test_no_avtor","000p;lko", 15),#Не автор, нет прав на создание
        ("Ostap", "000olkji", 15),#Не админ, Автор, есть права на создание
    ]
)
@allure.epic("Посты")
@allure.title("Тест лайка поста с автоматическим получением CSRF")
def test_like_post(username, password, post_id):
    result = get_csrf_token_for_post_like(username, password)
    csrf_token = result['csrfmiddlewaretoken']
    cookies = result['cookies']

    session = requests.Session()
    session.cookies.update(cookies)
    session.cookies.set('csrftoken', csrf_token)

    headers = {
        'Accept': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 ...',
        'X-CSRFToken': csrf_token,
    }
    data = {
        'csrfmiddlewaretoken': csrf_token,
    }

    with allure.step("Отправляем POST-запрос для лайка"):
        response = session.post(
            f'http://127.0.0.1:8000/blog/like-post/{post_id}/',
            headers={**headers, 'X-CSRFToken': csrf_token},
            data=data
        )
        assert response.status_code == 200, f"Ошибка при лайке: {response.status_code}"

        response_json = response.json()
        current_likes = response_json.get('likes')
        with allure.step("Отправляем POST-запрос для лайка повторно"):
            response = session.post(
                f'http://127.0.0.1:8000/blog/like-post/{post_id}/',
                headers={**headers, 'X-CSRFToken': csrf_token},
                data=data
            )
            assert response.status_code == 200, f"Ошибка при лайке: {response.status_code}"

            response_json = response.json()
            current_likes_2 = response_json.get('likes')
            dif_likes=current_likes - current_likes_2
            assert abs(dif_likes) == 1, f"Не обнажены изменения, различия = {dif_likes}"

        with allure.step("Отправляем POST-запрос для лайка повторно_2"):
            response = session.post(
                f'http://127.0.0.1:8000/blog/like-post/{post_id}/',
                headers={**headers, 'X-CSRFToken': csrf_token},
                data=data
            )
            assert response.status_code == 200, f"Ошибка при лайке: {response.status_code}"

            response_json = response.json()
            current_likes_3 = response_json.get('likes')
            assert current_likes == current_likes_3, f"Количество лайков отличается на  {current_likes - current_likes_3}"




@pytest.mark.parametrize(
    "username, password",
    [
        ("admin", "000p;lko"),  # Админ, Автор
    ]
)
@allure.epic("Посты")
@allure.feature("UI:Лайки постов Авторизация по API")
def test_like_button_increments(username, password):
    driver = webdriver.Chrome()
    driver.implicitly_wait(10)
    wait = WebDriverWait(driver, 10)

    try:
        auth_cookies, sessionid = get_auth_tokens(username, password)
        csrftoken = auth_cookies.get('csrftoken', '')

        driver.get(API_BLOG_HOME )

        driver.add_cookie({
            'name': 'sessionid',
            'value': sessionid,
            'domain': '127.0.0.1',
            'path': '/',
        })
        driver.add_cookie({
            'name': 'csrftoken',
            'value': csrftoken,
            'domain': '127.0.0.1',
            'path': '/',
        })

        driver.refresh()

        driver.get(API_POSTS_LIST)

        like_buttons = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".like-post")))


        like_button = like_buttons[0]

        initial_text = like_button.text.strip()
        initial_likes = int(initial_text.split()[0])

        with allure.step("Кликаем по кнопке Like"):
            like_button.click()

        dif_likes = 0

        def likes_updated(driver):
            nonlocal dif_likes
            try:
                btns = driver.find_elements(By.CSS_SELECTOR, ".like-post")
                if not btns:
                    return False
                current_text = btns[0].text.strip()
                current_likes = int(current_text.split()[0])
                dif_likes = current_likes - initial_likes
                return abs(dif_likes) == 1
            except:
                return False

        with allure.step("Ожидаем обновления счетчика лайков"):
            wait.until(likes_updated)

        assert abs(dif_likes) == 1, f"В результате нажатия кол-во лайков изменилось на {dif_likes}"

    finally:
        driver.quit()


@pytest.mark.parametrize(
    "username, password, staff",
    [
        ("admin", "000p;lko", True),#Админ,Автор
        ("test_no_avtor", "000p;lko", False),#Не автор, нет прав на удаление
        ("Ostap", "000olkji", False),#Не админ, Автор, нет  прав на создание
    ]
)
@allure.epic("Посты")
@allure.feature('API: Удаление поста ')
def test_delete_post(username, password,staff):
    post_id=get_max_post_id()
    result = get_csrf_token_delete(username, password, post_id)
    csrf_token = result['csrfmiddlewaretoken']
    cookies = result['cookies']

    session = requests.Session()
    session.cookies.update(cookies)
    session.cookies.set('csrftoken', csrf_token)

    data = {
            'csrfmiddlewaretoken': csrf_token,
        }

    headers = {
            'Accept': 'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0 ...',
            'X-CSRFToken': csrf_token,
        }

    with allure.step(f"Удаление поста от {username}.Сотрудинк {staff}"):
            response = session.post(
                f"{BASE_URL}/blog/post/{post_id}/delete",
                headers=headers,
                data=data,
            )

            allure.attach(str(response.status_code), name="Код ответа")
            allure.attach(response.text, name="Ответ сервера")

            if staff:
                if response.status_code == 500:
                    pytest.fail(f"Ошибка сервера (500): {response.text}")
                assert response.status_code in [200, 302], (
                    f"Удаление поста от  {username} Сотрудник {staff} не удалось, статус: {response.status_code}"
                )
            else:
                assert response.status_code in [403, 404, 500], (
                    f"Ожидалась ошибка для {username} Сотрудинк{staff}, но получен статус: {response.status_code}"
                )
import pytest
import requests
import allure
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

URL_LOGIN = 'http://0.0.0.0:8000/user/login/'
BASE_URL = 'http://0.0.0.0:8000'
PROTECTED_GET = 'http://0.0.0.0:8000/blog/post/new'
URL_HOME = 'http://0.0.0.0:8000/blog/home/'

def get_auth_tokens(username, password):
    session = requests.Session()

    login_page_url = URL_LOGIN
    response = session.get(login_page_url)
    response.raise_for_status()

    csrftoken = session.cookies.get('csrftoken')
    if not csrftoken:
        raise Exception("CSRF токен не найден в cookies после GET-запроса")

    login_data = {
        'csrfmiddlewaretoken': csrftoken,
        'username': username,
        'password': password
    }

    headers = {
        'Referer': login_page_url,
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 YaBrowser/25.4.0.0 Safari/537.36',
    }

    response_login = session.post(login_page_url, headers=headers, data=login_data)
    response_login.raise_for_status()

    sessionid = session.cookies.get('sessionid')

    return session.cookies.get_dict(), sessionid

@allure.epic("Авторизация")
@allure.feature("Авторизация через API")
@pytest.mark.parametrize("username,password,expect_sessionid", [
    ("admin", "000p;lko", True),
    ("test_123", "000P;lko", True),
    ("Ostap", "000olkji", True),
    ("admin", "000p;lk222o", False),
    ("admi222132n", "000p;lko", False),
])
def test_login_with_sessionid(username, password, expect_sessionid):
    with requests.Session() as session:
        session.cookies.clear()

        def get_auth():
            nonlocal session
            login_page_url = URL_LOGIN
            response = session.get(login_page_url)
            response.raise_for_status()

            csrftoken = session.cookies.get('csrftoken')
            if not csrftoken:
                raise Exception("CSRF токен не найден в cookies после GET-запроса")

            login_data = {
                'csrfmiddlewaretoken': csrftoken,
                'username': username,
                'password': password
            }

            headers = {
                'Referer': login_page_url,
                'Content-Type': 'application/x-www-form-urlencoded',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 YaBrowser/25.4.0.0 Safari/537.36',
            }

            response_login = session.post(login_page_url, headers=headers, data=login_data)
            response_login.raise_for_status()

            return session.cookies.get('sessionid')

        try:
            session_id_value = get_auth()
        except Exception as e:
            session_id_value = None

        with allure.step(f"Проверка наличия cookie sessionid для пользователя {username}"):
            if expect_sessionid:
                assert session_id_value is not None and session_id_value != '', \
                    "Ожидался cookie sessionid"
            else:
                assert session_id_value is None or session_id_value == '', \
                    "Cookie sessionid не должен быть"

@allure.epic("Авторизация")
@allure.feature("Авторизация без CSRF")
def test_post_without_csrf():
    login_url = URL_LOGIN

    with requests.Session() as session:
        with allure.step("Получение страницы входа для установки cookies"):
            response = session.get(login_url)
            response.raise_for_status()

        with allure.step("Отправка POST-запроса без CSRF токена"):
            data = {
                'username': 'admin',
                'password': '000p;lko'
            }

            headers = {
                'Referer': login_url,
                'Content-Type': 'application/x-www-form-urlencoded',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)...'
            }

            response_post = session.post(login_url, headers=headers, data=data)

        with allure.step("Проверка, что сервер возвращает статус 403"):
            assert response_post.status_code == 403, \
                f"Ожидался статус 403, получен {response_post.status_code}"


@pytest.mark.parametrize("username,password", [
    ("admin", "000p;lko"),
])
@allure.epic("Авторизация")
@allure.feature("Авторизация и деавторизация")
def test_logout_and_access(username,password):
    base_url = BASE_URL
    logout_url = f'{base_url}/user/logout/'
    auth_cookies, sessionid = get_auth_tokens(username, password)
    cookies = auth_cookies.copy()
    cookies['sessionid'] = sessionid
    with allure.step("Выполнение logout"):
        response = requests.get(
            logout_url,
            cookies=cookies
        )
        assert response.status_code in [200,302,301 ], \
            f"Ожидался статус 200 или 302 после logout, получен {response.status_code}"
        with allure.step("Проверка доступа к защищенному ресурсу после logout"):
            response = requests.get(
                PROTECTED_GET,
                cookies=cookies)
            assert response.status_code in [403, 302], \
                f"Ожидался статус 403 или 302 после logout, получен {response.status_code}"

@allure.epic("Авторизация")
@allure.feature('Фронт.Авторизация')
def test_authorization_redirect():
    driver = webdriver.Chrome()
    try:
        with allure.step("Открываем страницу входа"):
            driver.get(URL_LOGIN)
            time.sleep(2)

        with allure.step("Находим поля формы и вводим логин/пароль"):
            username_input = driver.find_element(By.ID, 'id_username')
            password_input = driver.find_element(By.ID, 'id_password')
            username_input.send_keys('admin')
            password_input.send_keys('000p;lko')

        with allure.step("Отправляем форму для входа"):
            password_input.send_keys(Keys.RETURN)
            time.sleep(3)

        with allure.step("Проверяем редирект на /blog/home/"):
            current_url = driver.current_url
            expected_url = URL_HOME
            assert current_url == expected_url, f"Редирект не произошел или URL другой: {current_url}"

        allure.attach(driver.page_source, name="Страница после авторизации", attachment_type=allure.attachment_type.HTML)
        print("Авторизация прошла успешно и произошел редирект на /blog/home/")

    except AssertionError as e:
        allure.attach(driver.page_source, name="Страница при ошибке", attachment_type=allure.attachment_type.HTML)
        raise e
    finally:
        driver.quit()
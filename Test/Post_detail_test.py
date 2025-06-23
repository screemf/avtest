
import pytest
import allure
from Auth_test import get_auth_tokens
import requests
from bs4 import BeautifulSoup
from allure import feature, story, severity, severity_level
import re
import allure
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = 'http://127.0.0.1:8000'
URL_POST_ID = 'http://127.0.0.1:8000/blog/post/15/'




def get_max_comment_id(post_id_del):
    try:
        post_url = f"{BASE_URL}/blog/post/{post_id_del}/"
        response = requests.get(post_url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        elements = soup.find_all(attrs={"data-id": True})

        if not elements:
            return None

        data_ids = []
        for el in elements:
            try:
                data_ids.append(int(el['data-id']))
            except (ValueError, TypeError):
                continue

        if not data_ids:
            return None

        return max(data_ids)

    except Exception as e:
        print(f"Ошибка при получении максимального ID: {e}")
        return None
def get_csrf_token_new_comm(username,password):
    url_post_id=URL_POST_ID
    auth_cookies, sessionid = get_auth_tokens(username, password)

    session = requests.Session()
    session.cookies.update(auth_cookies)
    response = session.get(url_post_id)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')

    csrf_input = soup.find('input', attrs={'name': 'csrfmiddlewaretoken'})

    if csrf_input and 'value' in csrf_input.attrs:
        csrfmiddlewaretoken = csrf_input['value']
        return {
            'csrfmiddlewaretoken': csrfmiddlewaretoken,
            'cookies': session.cookies.get_dict()
        }
    else:
        raise ValueError("CSRF middleware token не найден на странице")


def get_csrf_token_for_delete(username, password, data_id):
    url = URL_POST_ID  # ваш URL
    auth_cookies, sessionid = get_auth_tokens(username, password)

    session = requests.Session()
    session.cookies.update(auth_cookies)
    response = session.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')

    delete_button = soup.find('button', {'class': 'delete-comment', 'data-id': str(data_id)})
    if not delete_button:
        raise ValueError(f"Кнопка удаления с data-id={data_id} не найдена")

    comment_div = delete_button.find_parent('div', class_='comment')
    if not comment_div:
        raise ValueError(f"Родительский блок для комментария с data-id={data_id} не найден")

    search_areas = [comment_div] + comment_div.find_all('div', class_='comment')

    for area in search_areas:
        scripts = area.find_all('script')
        for script in scripts:
            if script.string and 'csrfmiddlewaretoken' in script.string:
                match = re.search(r"csrfmiddlewaretoken\s*:\s*['\"]([a-zA-Z0-9]+)['\"]", script.string)
                if match:
                    return {
                        'csrfmiddlewaretoken': match.group(1),
                        'cookies': session.cookies.get_dict()
                    }

    comment_form = soup.find('form', {'id': 'comment-form'})
    if comment_form:
        csrf_input = comment_form.find('input', {'name': 'csrfmiddlewaretoken'})
        if csrf_input and csrf_input.get('value'):
            return {
                'csrfmiddlewaretoken': csrf_input['value'],
                'cookies': session.cookies.get_dict()
            }

    raise ValueError(f"CSRF token для удаления не найден в комментарии с data-id={data_id}")
def get_csrf_token_for_element(username, password, data_id):
    url = URL_POST_ID
    auth_cookies, sessionid = get_auth_tokens(username, password)

    session = requests.Session()
    session.cookies.update(auth_cookies)
    response = session.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')

    like_button = soup.find('button', {'class': 'like-comment', 'data-id': str(data_id)})
    if not like_button:
        raise ValueError(f"Кнопка лайка с data-id={data_id} не найдена")

    comment_div = like_button.find_parent('div', class_='comment')
    if not comment_div:
        raise ValueError(f"Родительский блок для комментария с data-id={data_id} не найден")

    search_areas = [comment_div] + comment_div.find_all('div', class_='comment')

    for area in search_areas:
        scripts = area.find_all('script')
        for script in scripts:
            if script.string and 'csrfmiddlewaretoken' in script.string:
                match = re.search(r"csrfmiddlewaretoken\s*:\s*['\"]([a-zA-Z0-9]+)['\"]", script.string)
                if match:
                    return {
                        'csrfmiddlewaretoken': match.group(1),
                        'cookies': session.cookies.get_dict()
                    }

    comment_form = soup.find('form', {'id': 'comment-form'})
    if comment_form:
        csrf_input = comment_form.find('input', {'name': 'csrfmiddlewaretoken'})
        if csrf_input and csrf_input.get('value'):
            return {
                'csrfmiddlewaretoken': csrf_input['value'],
                'cookies': session.cookies.get_dict()
            }

    for script in soup.find_all('script'):
        if script.string and 'csrfmiddlewaretoken' in script.string:
            match = re.search(r"csrfmiddlewaretoken\s*:\s*['\"]([a-zA-Z0-9]+)['\"]", script.string)
            if match:
                return {
                    'csrfmiddlewaretoken': match.group(1),
                    'cookies': session.cookies.get_dict()
                }

    raise ValueError(f"CSRF token не найден ни в комментарии с data-id={data_id}, ни на странице")


@pytest.mark.parametrize(
    "username, password, id_comm, without_csrf_mid",
    [
        ("admin", "000p;lko", 66, False),  # Админ, Автор
        ("admin", "000p;lko", 66, True),

    ]
)
@allure.epic("Тестирования конкретного поста")
@allure.feature('Комментарии API')
def test_add_reply(username, password, id_comm,without_csrf_mid):
    result = get_csrf_token_new_comm(username, password)
    if without_csrf_mid:
        csrf_token = None
    else:
        csrf_token = result['csrfmiddlewaretoken']

    cookies = result['cookies']
    session = requests.Session()
    session.cookies.update(cookies)

    data = {
        'csrfmiddlewaretoken': csrf_token,
        'text': 'Автотестовое сообщение',
        'parent_id': id_comm
    }

    headers = {
        'Accept': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 ...',
        'X-CSRFToken': csrf_token,
    }

    with allure.step(f"Добавление комментария от пользователя {username} к комментарию {id_comm}"):
        response = session.post(
            URL_POST_ID,
            headers=headers,
            data=data,
        )
    if without_csrf_mid:
        assert response.status_code in [403, 404, 500], f"Коментарий был опубликован без CSRFmid..: {response.status_code}"
    else:
        assert response.status_code in [200, 302], f"Ошибка при добавлении комментария: {response.status_code}"



@pytest.mark.parametrize(
    "username, password, data_id",
    [
        ("admin", "000p;lko", 90),  # Админ, Автор
        ("test_no_avtor","000p;lko", 102),
        ("Ostap", "000olkji", 90)

    ]
)
@allure.epic("Тестирования конкретного поста")
@allure.feature('Лайк комментария API')
def test_like_comment(username, password, data_id):
    result = get_csrf_token_for_element(username, password, data_id)
    csrf_token = result['csrfmiddlewaretoken']
    cookies = result['cookies']
    session = requests.Session()
    session.cookies.update(cookies)
    data = {
        'csrfmiddlewaretoken': csrf_token,
    }
    headers = {
        'Accept': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 ...',
        'X-CSRFToken': csrf_token,
    }
    like_url = f'{BASE_URL}/blog/like-comment/{data_id}/'
    response = requests.post(
            like_url,
            headers=headers,
            cookies=cookies,
            data=data
    )
    assert response.status_code == 200
    response_json = response.json()
    current_likes = response_json.get('likes')
    with allure.step("Отправляем POST-запрос для лайка повторно"):
        response = requests.post(
            like_url,
            headers=headers,
            cookies=cookies,
            data=data
        )
        assert response.status_code == 200, f"Ошибка при лайке: {response.status_code}"

        response_json = response.json()
        current_likes_2 = response_json.get('likes')
        dif_likes = current_likes - current_likes_2
        assert abs(dif_likes) == 1, f"Не обнажены изменения, различия = {dif_likes}"

    with allure.step("Отправляем POST-запрос для лайка повторно_2"):
        response = requests.post(
            like_url,
            headers=headers,
            cookies=cookies,
            data=data
        )
        assert response.status_code == 200, f"Ошибка при лайке: {response.status_code}"

        response_json = response.json()
        current_likes_3 = response_json.get('likes')
        assert current_likes == current_likes_3, f"Количество лайков отличается на  {current_likes - current_likes_3}"


@pytest.mark.parametrize(
    "username, password, post_id_del, elses_comment",
    [
        ("Ostap", "000olkji", 15, True),  # Ожидаем НЕ найти кнопку
        ("admin", "000p;lko", 15, False),  # Ожидаем найти и удалить
    ]
)
@allure.epic("Тестирования конкретного поста")
@allure.feature('Удаление комментария')
def test_delete_comment(username, password, post_id_del, elses_comment):
    data_id = get_max_comment_id(post_id_del)
    if data_id is None:
        pytest.skip("Нет комментариев для удаления")

    try:
        result = get_csrf_token_for_delete(username, password, data_id)

        if elses_comment:
            pytest.fail(f"Кнопка удаления найдена (data-id={data_id}), хотя не должна была")

        csrf_token = result['csrfmiddlewaretoken']
        cookies = result['cookies']

        delete_url = f'{BASE_URL}/blog/delete-comment/{data_id}/'
        response = requests.post(
            delete_url,
            headers={
                'Accept': 'application/json',
                'X-CSRFToken': csrf_token,
                            },
            cookies=cookies,
            data={'csrfmiddlewaretoken': csrf_token}
        )

        assert response.status_code == 200, f"Ожидался статус 200, получен {response.status_code}"
        assert response.json().get('success') is True, "Удаление не было успешным"

    except ValueError as e:
        if "не найдена" in str(e):
            if elses_comment:
                with allure.step("Кнопка не найдена (ожидаемо)"):
                    return
            else:
                pytest.fail(f"Кнопка удаления не найдена (data-id={data_id}), хотя должна была")
        else:
            raise

#тут плавающая проблема иногда отправляется много запросов при нажатии на кнопку
@pytest.mark.parametrize(
    "username, password, post_id",
    [("Ostap", "000olkji", 16),
     ("Ostap", "000olkji", 16)
     ]
)
@allure.epic("Тестирования конкретного поста")
@allure.feature('UI тест лайка комментария с API авторизацией')
def test_like_comment_ui(username, password, post_id):
    driver = webdriver.Chrome()
    driver.implicitly_wait(5)

    try:
        with allure.step("1. Авторизация пользователя"):
            auth_cookies, sessionid = get_auth_tokens(username, password)
            csrftoken = auth_cookies.get('csrftoken', '')

            driver.get('http://127.0.0.1:8000/blog/home')

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

        with allure.step("Открытие страницы поста"):
            driver.get(f"{BASE_URL}/blog/post/{post_id}/")
            allure.attach(driver.get_screenshot_as_png(), name="Страница поста",
                          attachment_type=allure.attachment_type.PNG)

        with allure.step("Получение начального количества лайков"):
            like_button = driver.find_element(By.CSS_SELECTOR, ".like-comment")
            current_like = int(''.join(filter(str.isdigit, like_button.text or '0')))
            allure.attach(f"Текущее количество лайков: {current_like}",
                          name="Начальное значение",
                          attachment_type=allure.attachment_type.TEXT)

        with allure.step("Нажатие кнопки лайка"):
            like_button.click()
            time.sleep(3)
            allure.attach(driver.get_screenshot_as_png(), name="После нажатия",
                          attachment_type=allure.attachment_type.PNG)

        with allure.step("Проверка изменения счетчика"):
            final_like = int(''.join(filter(str.isdigit, like_button.text or '0')))
            allure.attach(f"Конечное количество лайков: {final_like}",
                          name="Конечное значение",
                          attachment_type=allure.attachment_type.TEXT)

            assert abs(final_like - current_like) == 1, (
                f"Счетчик должен измениться на 1. Было: {current_like}, стало: {final_like}"
            )
    finally:
        driver.quit()

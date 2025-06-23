import pytest
import allure
import requests
from Auth_test import get_auth_tokens
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains


@pytest.mark.parametrize(
    "username, password, url_suffix, elses_profile",
    [
        ("admin", "000p;lko", "1", False),
        ("test_123", "000P;lko", "24", False),
        ("Ostap", "000olkji", "2", False),
        ("admin", "000p;lko", "4", True),
        ("admin", "000p;lko", "999", True),
        ("admin", "000p;222lko", "22", True),

    ]
)
@allure.epic('Пользователи')
@allure.feature('API: Обновление профиля')
def test_update_profile(username, password, url_suffix,elses_profile):
    auth_cookies, sessionid = get_auth_tokens(username, password)

    update_url = f'http://127.0.0.1:8000/user/profile/update/{url_suffix}'

    headers = {
        'Accept': 'application/x-www-form-urlencoded',
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 YaBrowser/25.4.0.0 Safari/537.36',
    }

    data = {
        'csrfmiddlewaretoken': auth_cookies.get('csrftoken', ''),
        'about_me': 'Обновленный профиль через API',
        'hobbys': 'Тестовые хобби',
        'marital_status': 'Не важно',
        'email': 'test@example.com',
        'first_name': 'Обновлено',
        'last_name': 'Профиль'
    }

    cookies = auth_cookies.copy()
    cookies['sessionid'] = sessionid

    with allure.step(f"Обновление профиля для {username} с URL суффиксом {url_suffix}Чужой профиль{elses_profile}"):
        response = requests.post(
            update_url,
            headers=headers,
            data=data,
            cookies=cookies
        )

        allure.attach(str(response.status_code), name="Код ответа")
        allure.attach(response.text, name="Ответ сервера")

        if elses_profile:
            assert response.status_code in [401, 403, 404], (
                f"Ожидалась ошибка 403 или 404 для {username}, но получен статус {response.status_code}"
            )
        else:
            # Не ожидаем ошибок
            assert response.status_code in [200, 302], (
                f"Обновление профиля не удалось для {username}, статус {response.status_code}"
            )



@pytest.mark.parametrize(
    "username, password, url_suffix",
    [
        ("test_123", "000P;lko", "24"),
    ]
)
@allure.epic('Пользователи')
@allure.feature('UI: Обновление профиля через API авторизацию')
def test_ui_update_profile_with_api_auth(username, password, url_suffix):
    driver = webdriver.Chrome()
    driver.implicitly_wait(10)

    try:
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

        profile_url = f'http://127.0.0.1:8000/user/profile/update/{url_suffix}'
        driver.get(profile_url)

        with allure.step(f"Обновление профиля для {username} с URL суффиксом {url_suffix}"):
            about_me_input = driver.find_element(By.NAME, 'about_me')
            about_me_input.clear()
            about_me_input.send_keys('Обновленный профиль через UI')

            hobbys_input = driver.find_element(By.NAME, 'hobbys')
            hobbys_input.clear()
            hobbys_input.send_keys('Тестовые хобби')

            email_input = driver.find_element(By.NAME, 'email')
            email_input.clear()
            email_input.send_keys('test@example.com')

            first_name_input = driver.find_element(By.NAME, 'first_name')
            first_name_input.clear()
            first_name_input.send_keys('Обновлено222')

            last_name_input = driver.find_element(By.NAME, 'last_name')
            last_name_input.clear()
            last_name_input.send_keys('Профиль')

            wait = WebDriverWait(driver, 10)

            apply_button = wait.until(EC.element_to_be_clickable(
                (By.XPATH, '//button[text()="Применить"]')
            ))

            driver.execute_script("arguments[0].scrollIntoView(true);", apply_button)

            actions = ActionChains(driver)
            actions.move_to_element(apply_button).click().perform()

            wait = WebDriverWait(driver, 10)
            wait.until(EC.url_to_be('http://127.0.0.1:8000/user/users/'))

            assert driver.current_url == 'http://127.0.0.1:8000/user/users/', \
                f"Ожидался переход на http://127.0.0.1:8000/user/users/, но текущий URL: {driver.current_url}"
    finally:
        driver.quit()




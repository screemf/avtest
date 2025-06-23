import pytest
import allure
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import random
import string

URL_REGISTR = "http://127.0.0.1:8000/user/registr/"
URL_HOME = "http://127.0.0.1:8000/blog/home/"

@allure.feature("Регистрация пользователя - позитивный")
def test_registration():
    driver = webdriver.Chrome()
    try:
        with allure.step("Открыть страницу регистрации"):
            driver.get(URL_REGISTR)

        with allure.step("Заполнить имя пользователя"):
            username_input = driver.find_element(By.ID, "id_username")
            random_chars = ''.join(random.choices(string.ascii_letters + string.digits, k=4))
            username_input.send_keys("testuser"+ random_chars)

        with allure.step("Заполнить пароль"):
            password1_input = driver.find_element(By.ID, "id_password1")
            password1_input.send_keys("TestPassword123!")

        with allure.step("Подтвердить пароль"):
            password2_input = driver.find_element(By.ID, "id_password2")
            password2_input.send_keys("TestPassword123!")

        time.sleep(2)

        with allure.step("Отправить форму"):
            submit_button = driver.find_element(By.XPATH, "//button[@type='submit' and text()='Зарегистрироваться']")
            submit_button.click()

        time.sleep(2)

        with allure.step("Проверка успешной регистрации"):

            assert driver.current_url == URL_HOME
        allure.attach(driver.page_source, name="Страница после регистрации", attachment_type=allure.attachment_type.HTML)
    finally:
        driver.quit()


@allure.feature("Регистрация пользователя - негативный(неверный повтор пароля)")
def test_registration_negative_repear_pass():
    driver = webdriver.Chrome()
    try:
        with allure.step("Открыть страницу регистрации"):
            driver.get(URL_REGISTR)

        with allure.step("Заполнить имя пользователя"):
            username_input = driver.find_element(By.ID, "id_username")
            random_chars = ''.join(random.choices(string.ascii_letters + string.digits, k=4))
            username_input.send_keys("testuser"+ random_chars)

        with allure.step("Заполнить пароль"):
            password1_input = driver.find_element(By.ID, "id_password1")
            password1_input.send_keys("TestPassword123!")

        with allure.step("Парль не подтвержден"):
            password2_input = driver.find_element(By.ID, "id_password2")
            password2_input.send_keys("TestPassword234!")

        time.sleep(2)

        with allure.step("Отправить форму"):
            submit_button = driver.find_element(By.XPATH, "//button[@type='submit' and text()='Зарегистрироваться']")
            submit_button.click()

        time.sleep(2)

        with allure.step("Проверка валидации валидации повтроного пароля"):

            assert driver.current_url != URL_HOME
        allure.attach(driver.page_source, name="Страница после регистрации", attachment_type=allure.attachment_type.HTML)
    finally:
        driver.quit()

@allure.feature("Регистрация пользователя - негативный(Валидация пароля)")
def test_registration_no_valid_pass():
    driver = webdriver.Chrome()
    try:
        with allure.step("Открыть страницу регистрации"):
            driver.get(URL_REGISTR)

        with allure.step("Заполнить имя пользователя"):
            username_input = driver.find_element(By.ID, "id_username")
            random_chars = ''.join(random.choices(string.ascii_letters + string.digits, k=4))
            username_input.send_keys("testuser"+ random_chars)

        with allure.step("Заполнить пароль"):
            password1_input = driver.find_element(By.ID, "id_password1")
            password1_input.send_keys("password")

        with allure.step("Парль не подтвержден"):
            password2_input = driver.find_element(By.ID, "id_password2")
            password2_input.send_keys("password")

        time.sleep(2)

        with allure.step("Отправить форму"):
            submit_button = driver.find_element(By.XPATH, "//button[@type='submit' and text()='Зарегистрироваться']")
            submit_button.click()

        time.sleep(2)

        with allure.step("Проверка валидации валидации повтроного пароля"):

            assert driver.current_url != URL_HOME
        allure.attach(driver.page_source, name="Страница после регистрации", attachment_type=allure.attachment_type.HTML)
    finally:
        driver.quit()

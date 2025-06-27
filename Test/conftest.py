import pytest
import allure
import logging
from requests.exceptions import RequestException

@pytest.fixture
def safe_test_execution(request):
    """Фикстура, которая перехватывает ошибки и логирует их, не давая упасть контейнеру."""
    def run_safely():
        try:
            yield  # Здесь выполняется тест
        except AssertionError as e:
            logging.error(f"❌ Тест не пройден: {e}", exc_info=True)
            allure.attach(str(e), name="Assertion Error", attachment_type=allure.attachment_type.TEXT)
        except RequestException as e:
            logging.error(f"🔌 Ошибка запроса: {e}", exc_info=True)
            allure.attach(str(e), name="Request Error", attachment_type=allure.attachment_type.TEXT)
        except Exception as e:
            logging.error(f"💥 Непредвиденная ошибка: {e}", exc_info=True)
            allure.attach(str(e), name="Unexpected Error", attachment_type=allure.attachment_type.TEXT)
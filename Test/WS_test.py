import allure
import pytest
import websockets
import asyncio
from websockets.exceptions import ConnectionClosedError

WS_URL_POSTS = 'ws://localhost:8000/ws/posts/'
WS_URL_POST = 'ws://localhost:8000/ws/comments/15/'
@allure.feature('WebSocket создание поста')
async def test_websocket_notification():
    websocket_url =  WS_URL_POSTS
    timeout = 100  # seconds
    message_received = False

    with allure.step(f"Установка WebSocket соединения с {websocket_url}"):
        try:
            async with websockets.connect(websocket_url) as websocket:
                with allure.step(f"Ожидание сообщения в течение {timeout} секунд"):
                    try:
                        message = await asyncio.wait_for(websocket.recv(), timeout=timeout)
                        message_received = True
                        with allure.step("Сообщение получено"):
                            allure.attach(f"Полученное сообщение: {message}", name="WebSocket Message")
                    except asyncio.TimeoutError:
                        pytest.fail(f"Сообщение не получено в течение {timeout} секунд")
                    except ConnectionClosedError:
                        pytest.fail("Соединение было закрыто до получения сообщения")

        except Exception as e:
            pytest.fail(f"Ошибка соединения: {str(e)}")

    assert message_received, "Не удалось получить сообщение через WebSocket"

# Обертка для запуска асинхронного теста

@allure.feature('WebSocket создание комментария')
async def test_websocket_notification_post_id():
    websocket_url = WS_URL_POST
    timeout = 100  # seconds
    message_received = False

    with allure.step(f"Установка WebSocket соединения с {websocket_url}"):
        try:
            async with websockets.connect(websocket_url) as websocket:
                with allure.step(f"Ожидание сообщения в течение {timeout} секунд"):
                    try:
                        message = await asyncio.wait_for(websocket.recv(), timeout=timeout)
                        message_received = True
                        with allure.step("Сообщение получено"):
                            allure.attach(f"Полученное сообщение: {message}", name="WebSocket Message")
                    except asyncio.TimeoutError:
                        pytest.fail(f"Сообщение не получено в течение {timeout} секунд")
                    except ConnectionClosedError:
                        pytest.fail("Соединение было закрыто до получения сообщения")

        except Exception as e:
            pytest.fail(f"Ошибка соединения: {str(e)}")

    assert message_received, "Не удалось получить сообщение через WebSocket"

def test_websocket_wrapper():
   # """Обертка для запуска асинхронного теста"""
    asyncio.get_event_loop().run_until_complete(test_websocket_notification())
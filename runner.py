import os



def run_command(command, description):
    # Сохраняем текущую директорию
    original_dir = os.getcwd()

    try:
        # Переходим в директорию Test
        os.chdir('Test')

        # Запускаем команду pytest
        print(f"Запуск: {description}")
        print(f"Выполняется команда: {command}")
        # Здесь ваш код для выполнения команды

    finally:
        # Возвращаемся обратно в исходную директорию
        os.chdir(original_dir)


def main():
    # Первый набор тестов
    run_command(
        "pytest WS_test.py Post_test.py Post_detail_test.py -n 3 --alluredir=./allure-results",
        "Первый набор тестов (WS, Post, Post Detail)"
    )

    # Второй набор тестов
    run_command(
        "pytest Auth_test.py Users_test.py registr_test.py --alluredir=./allure-results",
        "Второй набор тестов (Auth, Users, Registration)"
    )

    # Запуск Allure (запустится в любом случае, даже если тесты упали)
    run_command(
        "allure serve ./allure-results",
        "Отображение результатов в Allure"
    )

    print("\n\033[1mВыполнение всех команд завершено\033[0m")


if __name__ == "__main__":
    main()
import subprocess
import sys


def run_command(command, description):
    print(f"\n\033[1mЗапуск: {description}\033[0m")
    print(f"\033[34mВыполняется команда: {command}\033[0m")
    result = subprocess.run(command, shell=True)
    if result.returncode == 0:
        print(f"\033[32mУспешно: {description}\033[0m")
    else:
        print(f"\033[33mЗавершено с ошибкой (код {result.returncode}): {description}\033[0m")
    return result.returncode


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
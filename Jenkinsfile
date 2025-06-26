pipeline {
    agent any

    environment {
        // Настройки тестового раннера
        TEST_IMAGE = "my-app"
        TEST_TAG = "${env.BUILD_NUMBER}"

        // URL тестируемого приложения (можно задавать через параметры)
        TEST_TARGET_URL = "http://127.0.0.1:8000/blog/home"

        // Время ожидания перед проверкой (в секундах)
        WAIT_TIME = "10" // 3 минуты = 180 секунд
    }

    stages {
        stage('Prepare Test Environment') {
            steps {
                script {
                    // Добавляем ожидание перед проверкой
                    echo "Ожидаем ${WAIT_TIME} секунд перед проверкой доступности приложения..."
                    sleep(time: WAIT_TIME.toInteger(), unit: 'SECONDS')

                    // Проверка доступности тестируемого приложения
                    sh """
                        if ! curl --output /dev/null --silent --head --fail "${TEST_TARGET_URL}"; then
                            echo "Тестируемое приложение не доступно по адресу ${TEST_TARGET_URL}"
                            exit 1
                        fi
                        echo "Приложение успешно доступно по адресу ${TEST_TARGET_URL}"
                    """
                }
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    try {
                        // Запускаем тестовый контейнер и передаем URL тестируемого приложения
                        sh """
                        docker run --rm \
                            -e TEST_TARGET_URL=${TEST_TARGET_URL} \
                            ${TEST_IMAGE}:${TEST_TAG} \
                            pytest -n 3 --alluredir=./allure-results
                        """
                    } finally {
                        // Сохраняем результаты тестов
                        archiveArtifacts artifacts: '**/allure-results/**', allowEmptyArchive: true
                    }
                }
            }
        }

        stage('Generate Report') {
            steps {
                script {
                    // Генерируем Allure отчет
                    allureCommandline = tool name: 'allure-commandline', type: 'io.qameta.allure.jenkins.tools.AllureCommandlineInstaller'
                    sh """
                    ${allureCommandline}/bin/allure generate allure-results -o allure-report
                    """
                }
            }
        }
    }

    post {
        always {
            allure includeProperties: false,
                   jdk: '',
                   results: [[path: 'allure-results']]
        }
    }
}
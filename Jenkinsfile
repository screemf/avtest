pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "my-app"
        DOCKER_TAG = "${env.BUILD_NUMBER}"
        CONTAINER_NAME = "my-app"
        APP_PORT = "5000" // Укажите нужный порт вашего приложения
    }

    stages {
        stage('Build Docker Image') {
            steps {
                script {
                    // Собираем Docker-образ
                    docker.build("${DOCKER_IMAGE}:${DOCKER_TAG}")
                }
            }
        }

        stage('Run Application') {
            steps {
                script {
                    // Останавливаем и удаляем предыдущий контейнер, если есть
                    sh "docker stop ${CONTAINER_NAME} || true"
                    sh "docker rm ${CONTAINER_NAME} || true"

                    // Запускаем новый контейнер
                    sh """
                    docker run -d \
                        --name ${CONTAINER_NAME} \
                        -p ${APP_PORT}:${APP_PORT} \
                        ${DOCKER_IMAGE}:${DOCKER_TAG}
                    """

                    // Ждем запуска приложения
                    sleep(time: 5, unit: 'SECONDS')

                    // Проверяем, что контейнер запущен
                    sh "docker ps | grep ${CONTAINER_NAME}"
                }
            }
        }
    }

    post {
        success {
            echo "Приложение успешно запущено и доступно по адресу:"
            echo "http://localhost:${APP_PORT}"
            echo "Или используйте: docker logs ${CONTAINER_NAME}"
        }
        failure {
            echo "Ошибка при запуске приложения"
            sh "docker logs ${CONTAINER_NAME} || true"
        }
    }

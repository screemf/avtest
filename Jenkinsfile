pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "my-app"
        DOCKER_TAG = "${env.BUILD_NUMBER}"
        CONTAINER_NAME = "my-app"
        APP_PORT = "5000"
        ALLURE_RESULTS = "./allure-results"
    }

    stages {
        stage('Build Docker Image') {
            steps {
                script {
                    docker.build("${DOCKER_IMAGE}:${DOCKER_TAG}")
                }
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE') {
                        sh """
                        pytest WS_test.py Post_test.py Post_detail_test.py \
                            -n 3 \
                            --alluredir=${ALLURE_RESULTS}
                        """
                    }
                    catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE') {
                        sh """
                        pytest Auth_test.py Users_test.py registr_test.py \
                            --alluredir=${ALLURE_RESULTS}
                        """
                    }
                }
            }
        }

        stage('Generate Allure Report') {
            steps {
                script {
                    sh "allure serve ${ALLURE_RESULTS} || true"
                }
            }
        }

        stage('Run Application') {
            steps {
                script {
                    sh "docker stop ${CONTAINER_NAME} || true"
                    sh "docker rm ${CONTAINER_NAME} || true"
                    sh """
                    docker run -d \
                        --name ${CONTAINER_NAME} \
                        -p ${APP_PORT}:${APP_PORT} \
                        ${DOCKER_IMAGE}:${DOCKER_TAG}
                    """
                    sleep(time: 5, unit: 'SECONDS')
                    sh "docker ps | grep ${CONTAINER_NAME}"
                }
            }
        }
    }

    post {
        always {
            echo "Allure отчёт был доступен во время выполнения"
            echo "Приложение запущено на порту: ${APP_PORT}"
            echo "Для просмотра логов: docker logs ${CONTAINER_NAME}"
        }
        success {
            echo "Pipeline завершён успешно (приложение запущено)"
        }
        unstable {
            echo "Некоторые тесты не прошли, но приложение запущено"
        }
        failure {
            echo "Ошибка в процессе выполнения pipeline"
        }
    }
}
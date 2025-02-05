pipeline {
    agent {
        label 'eu-node'  
    }

    environment {
        DOCKER_IMAGE = 'flask-wallet-app'
        DOCKER_TAG = 'latest'
        DOCKER_REGISTRY = 'local' // Replace with your Docker registry
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/followeran2024/Wallet.git' // Replace with your repo URL
            }
        }

        stage('Prepare Environment') {
            steps {
                script {
                    withCredentials([
                        string(credentialsId: 'wallet_db_username', variable: 'DB_USERNAME'),
                        string(credentialsId: 'wallet_db_password', variable: 'DB_PASSWORD'),
                        string(credentialsId: 'wallet_db_host', variable: 'DB_HOST'),
                        string(credentialsId: 'VALIDATE_TOKEN_URL', variable: 'VALIDATE_TOKEN_URL')
                    ]) {
                       sh """
                                    echo "DB_USERNAME=$DB_USERNAME" > .env
                                    echo "DB_PASSWORD=$DB_PASSWORD" >> .env
                                    echo "DB_HOST=$DB_HOST" >> .env
                                    echo "DB_HOST=$VALIDATE_TOKEN_URL" >> .env
                                    
                                """
                    }
                }

                sh 'cat .env'  // Debugging (remove in production)
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    docker.build("${DOCKER_IMAGE}:${DOCKER_TAG}", ".")
                }
            }
        }

       /*stage('Run Tests') {
            steps {
                script {
                    sh "docker run --rm ${DOCKER_IMAGE}:${DOCKER_TAG} sh -c 'pip install pytest && pytest tests/ -v'"
                }
            }
        }
*/
        stage('Deploy to Production') {
            steps {
                script {
                    sh "docker compose down || true" // Ensure it doesn't fail if not running
                    sh "docker compose up -d"
                }
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
}

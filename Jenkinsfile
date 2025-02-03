pipeline {
    agent {
        label 'eu-node'  
    }

    environment {
        DOCKER_IMAGE = 'flask-wallet-app'
        DOCKER_TAG = 'latest'
        DOCKER_REGISTRY = 'local' // Replace with your Docker registry
        ENV_WALLET_DBUSERNAME=credentials('wallet_db_username') 
        ENV_WALLET_DBPASSWORD=credentials('wallet_db_password') 
        ENV_WALLET_DBHOST=credentials('wallet_db_host') 
    }


 

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/followeran2024/Wallet.git' // Replace with your repo URL
            }
        }

 stages {
        stage('Prepare Environment') {
            steps {
                script {
                    def envFileContent = """
                    FLASK_ENV=production
                    DB_HOST=${ENV_WALLET_DBHOST}
                    DB_USER=${ENV_WALLET_DBUSERNAME}
                    DB_PASSWORD=${ENV_WALLET_DBPASSWORD}
                    
                    """

                    writeFile file: '.env', text: envFileContent
                }

                sh 'cat .env'  // For debugging (remove in production)
            }
        }

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
                    docker.image("${DOCKER_IMAGE}:${DOCKER_TAG}").inside {
                        sh 'pip install pytest'
                        sh 'pytest test.py -v'
                    }
                }
            }
        }



        stage('Deploy to Production') {
            steps {
                script {
                    sh "docker compose down"
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
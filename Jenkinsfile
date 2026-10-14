pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                echo '=================================================='
                echo 'Stage 1: Building Docker Image (waste-collection-ci)'
                echo '=================================================='
                sh 'docker build -t waste-collection-ci .'
            }
        }

        stage('Test') {
            steps {
                echo '=================================================='
                echo 'Stage 2: Running Automated Pytest in Container'
                echo '=================================================='
                sh 'docker run --rm waste-collection-ci python -m pytest test_app.py'
            }
        }

        stage('Deploy with Ansible') {
            steps {
                echo '=================================================='
                echo 'Stage 3: Executing Ansible Playbook via Container'
                echo '=================================================='
                sh '''
                docker exec ansible-docker-lab \
                ansible-playbook \
                -i /inventory.ini \
                /waste-deploy.yml
                '''
            }
        }
    }

    post {
        success {
            echo '=================================================='
            echo 'SUCCESS: Waste Collection CI/CD Pipeline Completed Successfully!'
            echo '=================================================='
        }
        failure {
            echo '=================================================='
            echo 'FAILURE: Waste Collection CI/CD Pipeline Failed!'
            echo '=================================================='
        }
    }
}

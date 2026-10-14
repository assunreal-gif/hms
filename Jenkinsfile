node {
    try {
        stage('Checkout') {
            echo '=================================================='
            echo 'Stage 0: Checking out source code on server...'
            echo '=================================================='
            checkout scm
        }

        stage('Build') {
            echo '=================================================='
            echo 'Stage 1: Building Docker Image (waste-collection-ci)'
            echo '=================================================='
            if (isUnix()) {
                sh 'docker build -t waste-collection-ci .'
            } else {
                bat 'docker build -t waste-collection-ci .'
            }
        }

        stage('Test') {
            echo '=================================================='
            echo 'Stage 2: Running Automated Pytest in Container'
            echo '=================================================='
            if (isUnix()) {
                sh 'docker run --rm waste-collection-ci python -m pytest test_app.py'
            } else {
                bat 'docker run --rm waste-collection-ci python -m pytest test_app.py'
            }
        }

        stage('Deploy with Ansible') {
            echo '=================================================='
            echo 'Stage 3: Executing Ansible Playbook via Container'
            echo '=================================================='
            if (isUnix()) {
                sh '''
                docker exec ansible-docker-lab \
                ansible-playbook \
                -i /inventory.ini \
                /waste-deploy.yml
                '''
            } else {
                bat 'docker exec ansible-docker-lab ansible-playbook -i /inventory.ini /waste-deploy.yml'
            }
        }

        echo '=================================================='
        echo 'SUCCESS: Waste Collection CI/CD Pipeline Completed Successfully!'
        echo '=================================================='
    } catch (Exception e) {
        echo '=================================================='
        echo 'FAILURE: Waste Collection CI/CD Pipeline Failed!'
        echo "Error: ${e.message}"
        echo '=================================================='
        currentBuild.result = 'FAILURE'
        throw e
    }
}

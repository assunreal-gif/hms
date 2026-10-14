node {
    try {
        stage('Checkout') {
            echo '=================================================='
            echo 'Stage 0: Checking out source code into workspace...'
            echo '=================================================='
            try {
                checkout scm
            } catch (Exception scmErr) {
                echo 'SCM not configured; copying source code from project directory...'
                if (isUnix()) {
                    sh 'cp -r "/c/Users/Assun/Downloads/hostel management/." .'
                } else {
                    bat 'xcopy /E /I /Y "C:\\Users\\Assun\\Downloads\\hostel management" .'
                }
            }
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
            echo 'Stage 3: Executing Deployment'
            echo '=================================================='
            if (isUnix()) {
                sh '''
                docker exec ansible-docker-lab ansible-playbook -i /inventory.ini /waste-deploy.yml || (
                    echo "Deploying container directly with persistent volume..."
                    docker rm -f waste-collection-ansible || true
                    docker run -d --name waste-collection-ansible -p 5002:5000 -v waste_collection_data:/app/data --restart unless-stopped waste-collection-ci
                )
                '''
            } else {
                bat '''
                docker exec ansible-docker-lab ansible-playbook -i /inventory.ini /waste-deploy.yml || (
                    echo Deploying container directly with persistent volume...
                    docker rm -f waste-collection-ansible 2>nul || exit 0
                    docker run -d --name waste-collection-ansible -p 5002:5000 -v waste_collection_data:/app/data --restart unless-stopped waste-collection-ci
                )
                '''
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

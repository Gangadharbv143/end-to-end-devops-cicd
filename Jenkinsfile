pipeline {
    agent any

    environment {
        KUBECONFIG = '/var/lib/jenkins/.kube/config'
        K8S_NAMESPACE = 'devops-cicd'
        APP_NAME = 'end-to-end-devops-cicd'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Python Tests') {
            steps {
                sh '''
                    set -e
                    python3 -m venv .venv
                    . .venv/bin/activate
                    pip install -r requirements.txt
                    pytest -q
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                    set -e
                    IMAGE="${APP_NAME}:build-${BUILD_NUMBER}"
                    docker build -t "$IMAGE" .
                    echo "Built image: $IMAGE"
                '''
            }
        }

        stage('Transfer Image to Minikube') {
            steps {
                sh '''
                    set -e
                    IMAGE="${APP_NAME}:build-${BUILD_NUMBER}"

                    docker save "$IMAGE" | \
                        docker exec -i minikube docker load

                    docker exec minikube docker images "$IMAGE"
                '''
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                sh '''
                    set -e

                    kubectl apply -f k8s/ -n "$K8S_NAMESPACE"

                    kubectl set image \
                        deployment/"$APP_NAME" \
                        devops-app="${APP_NAME}:build-${BUILD_NUMBER}" \
                        -n "$K8S_NAMESPACE"

                    kubectl rollout status \
                        deployment/"$APP_NAME" \
                        -n "$K8S_NAMESPACE" \
                        --timeout=120s
                '''
            }
        }

        stage('Verify Deployment') {
            steps {
                sh '''
                    set -e
                    kubectl get pods -n "$K8S_NAMESPACE"
                    kubectl get services -n "$K8S_NAMESPACE"
                '''
            }
        }
    }
}

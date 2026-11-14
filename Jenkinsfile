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
                    python -m pytest -q
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

        stage('Post-Deployment Smoke Tests') {
            steps {
                sh '''
                    set -eu

                    PORT=18086
                    LOG_FILE="$WORKSPACE/port-forward.log"

                    kubectl port-forward \
                        -n "$K8S_NAMESPACE" \
                        --address 127.0.0.1 \
                        service/"$APP_NAME"-service \
                        "$PORT":80 > "$LOG_FILE" 2>&1 &

                    PF_PID=$!

                    cleanup() {
                        kill "$PF_PID" 2>/dev/null || true
                        wait "$PF_PID" 2>/dev/null || true
                    }

                    trap cleanup EXIT

                    echo "Waiting for application..."

                    READY=0
                    for attempt in $(seq 1 30); do
                        if curl --silent --fail \
                            "http://127.0.0.1:$PORT/health" >/dev/null; then
                            READY=1
                            break
                        fi
                        sleep 2
                    done

                    if [ "$READY" -ne 1 ]; then
                        echo "Application did not become ready."
                        cat "$LOG_FILE"
                        exit 1
                    fi

                    for endpoint in / /health /ready; do
                        echo "Checking $endpoint"

                        STATUS=$(curl --silent --output /dev/null \
                            --write-out "%{http_code}" \
                            "http://127.0.0.1:$PORT$endpoint")

                        echo "HTTP status: $STATUS"

                        if [ "$STATUS" != "200" ]; then
                            echo "Smoke test failed: $endpoint"
                            exit 1
                        fi
                    done

                    echo "All smoke tests passed."
                '''
            }
        }
    }
}
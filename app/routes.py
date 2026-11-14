from flask import jsonify

def register_routes(app):

    @app.route("/")
    def home():
        return jsonify({
            "application": "End-to-End DevOps CI/CD Pipeline",
            "status": "running",
            "version": "1.0.0"
        })

    @app.route("/health")
    def health():
        return jsonify({
            "status": "healthy"
        }), 200

    @app.route("/ready")
    def ready():
        return jsonify({
            "status": "ready"
        }), 200

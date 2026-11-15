from flask import Flask
from app.routes import register_routes
from app.metrics import configure_metrics

app = Flask(__name__)

register_routes(app)
configure_metrics(app)

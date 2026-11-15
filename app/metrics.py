import os
import time

from flask import Response, g, request

from prometheus_client import (
    CONTENT_TYPE_LATEST,
    CollectorRegistry,
    Counter,
    Histogram,
    REGISTRY,
    generate_latest,
    multiprocess,
)

HTTP_REQUESTS = Counter(
    "flask_http_requests",
    "Total number of HTTP requests",
    ["method", "endpoint", "status"]
)

HTTP_REQUEST_DURATION = Histogram(
    "flask_http_request_duration_seconds",
    "HTTP request response time in seconds",
    ["method", "endpoint"]
)


def configure_metrics(app):

    @app.before_request
    def start_request_timer():
        g.prometheus_start_time = time.perf_counter()

    @app.after_request
    def record_request_metrics(response):

        if request.endpoint != "prometheus_metrics":
            endpoint = request.endpoint or "unknown"

            HTTP_REQUESTS.labels(
                request.method,
                endpoint,
                str(response.status_code)
            ).inc()

            start_time = getattr(g, "prometheus_start_time", None)

            if start_time is not None:
                duration = time.perf_counter() - start_time

                HTTP_REQUEST_DURATION.labels(
                    request.method,
                    endpoint
                ).observe(duration)

        return response

    @app.route("/metrics", methods=["GET"], endpoint="prometheus_metrics")
    def prometheus_metrics():

        if os.environ.get("PROMETHEUS_MULTIPROC_DIR"):
            registry = CollectorRegistry()
            multiprocess.MultiProcessCollector(registry)
        else:
            registry = REGISTRY

        return Response(
            generate_latest(registry),
            mimetype=CONTENT_TYPE_LATEST
        )

from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix


class PrefixMiddleware:
    def __init__(self, app, prefix: str):
        self.app = app
        self.prefix = prefix.rstrip("/")

    def __call__(self, environ, start_response):
        if self.prefix:
            environ["SCRIPT_NAME"] = self.prefix
        return self.app(environ, start_response)


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object("experiment.config.Config")
    app.config["APPLICATION_ROOT"] = app.config["URL_PREFIX"] or "/"

    from .routes import bp

    app.register_blueprint(bp)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    app.wsgi_app = PrefixMiddleware(app.wsgi_app, app.config["URL_PREFIX"])
    return app

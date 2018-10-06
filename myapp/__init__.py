import importlib

import flask

import config


def _initialize_errorhandlers(app):
    from myapp.errors import errors
    app.register_blueprint(errors)


def _initialize_blueprints(app):
    from myapp import main
    app.register_blueprint(main.bp)


def create_app(config_class=config.ConfigProd):
    app = flask.Flask(__name__)
    app.config.from_object(config_class)

    _initialize_errorhandlers(app)
    _initialize_blueprints(app)

    app.target_backends = {}
    for name, backend in app.config['TARGET_BACKENDS'].items():
        *m, c = backend['class'].split('.')
        # Oh boy !
        module = importlib.import_module('.'.join(m))
        instance = getattr(module, c)(**backend['arguments'])
        app.target_backends[name] = instance
    return app

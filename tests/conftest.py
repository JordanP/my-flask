import hashlib
import hmac

import flask.json
import pytest

import config
from myapp import create_app


@pytest.fixture()
def test_app():
    app = create_app(config_class=config.ConfigTest)
    yield app


@pytest.fixture()
def test_client(test_app):
    yield test_app.test_client()


@pytest.fixture()
def test_config(test_app):
    yield test_app.config


@pytest.fixture()
def compute_sig(test_config):
    def _(obj):
        # This really needs to reuse the same JSON encoder (i.e the flask one) that the one used by test_client.post
        hasher = hmac.new(test_config["SQREEN_WEBHOOK_SECRET_KEY"], flask.json.dumps(obj).encode(), hashlib.sha256)
        return hasher.hexdigest()

    return _

import hashlib
import hmac
import json

import flask
import flask.json
import werkzeug.local

from myapp import errors, models

bp = flask.Blueprint("main", __name__)
log = werkzeug.local.LocalProxy(lambda: flask.current_app.logger)


def check_signature(secret_key, request_signature, request_body):
    hasher = hmac.new(secret_key, request_body, hashlib.sha256)
    dig = hasher.hexdigest()
    return hmac.compare_digest(dig, request_signature)


@bp.route('/', methods=['GET', 'POST'])
def index():
    req_body = flask.request.get_data() or b"{}"
    req_sig = flask.request.headers.get("X-Sqreen-Integrity", default="")

    if not check_signature(flask.current_app.config["SQREEN_WEBHOOK_SECRET_KEY"], req_sig, req_body):
        raise errors.BadRequest("Invalid X-Sqreen-Integrity signature")

    try:
        payloads = json.loads(req_body, object_hook=models.object_decoder)
    except ValueError as e:
        # Signature is valid (comes from Sqreen) but payload is weird, this warrants logging at warning level
        log.warning("unable to decode Sqreen IO Payload: %s", req_body)
        raise errors.BadRequest(str(e))

    if payloads:
        for target_backend in flask.current_app.target_backends.values():
            target_backend.send(payloads)

    return '', 204

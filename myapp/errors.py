import flask

errors = flask.Blueprint('errors', __name__)


class BadRequest(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        super().__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


@errors.app_errorhandler(BadRequest)
def handle_bad_request(error):
    response = flask.json.jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

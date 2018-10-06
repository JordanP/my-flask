import abc
import logging
import urllib.parse

import flask
import requests
import werkzeug.local

log = werkzeug.local.LocalProxy(lambda: flask.current_app.logger)


class TargetBackend(abc.ABC):
    @abc.abstractmethod
    def send(self, sqreen_payload):
        pass


class BaseSqreenIOPayload:
    """This class acts as a container for common payload attributes"""
    application_id = ""
    application_name = ""
    date_occurred = ""
    environment = ""
    event_category = ""
    event_kind = ""
    humanized_description = ""
    id = ""
    risk = ""
    sqreen_payload_type = ""
    url = ""

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class SecurityEventPayload(BaseSqreenIOPayload):
    application_account_account_id = ""
    application_account_account_keys = ""
    application_account_url = ""


class TestPayload(BaseSqreenIOPayload):
    pass


def object_decoder(obj):
    if 'sqreen_payload_type' in obj:
        if obj['sqreen_payload_type'] == 'security_event':
            return SecurityEventPayload(**obj)
        if obj['sqreen_payload_type'] == "test":
            return TestPayload(**obj)

        raise ValueError("Unable to decode Sqreen IO Payload")


class LogTargetBackend(TargetBackend):
    def __init__(self, log_filename):
        self.logger = logging.getLogger("LogTargetBackend")
        handler = logging.FileHandler(log_filename)
        self.logger.addHandler(handler)

    def send(self, payloads):
        for payload in payloads:
            self.logger.warning(
                "Got a security event at {p.date_occurred}: {p.humanized_description}".format(p=payload))


class HTTPTargetBackend(TargetBackend):
    def __init__(self, remote_url):
        url_parts = urllib.parse.urlparse(remote_url)
        if url_parts.scheme not in ['http', 'https']:  # Validate that some more
            raise ValueError("remote_url argument must start by http:// or https://")

        self.remote_url = url_parts.geturl()

    def send(self, payloads):
        for payload in payloads:
            try:
                resp = requests.post(self.remote_url, json=payload.__dict__)
            except requests.exceptions.RequestException as e:
                log.info("Exception while sending payload to %s: %s", self.remote_url, e)
                continue
            if not 200 <= resp.status_code < 300:
                log.info(
                    "Unexpected status code while sending payload to %s: '%d'", self.remote_url, resp.status_code)

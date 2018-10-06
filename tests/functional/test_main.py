from unittest import mock
from unittest.mock import patch

import requests

from myapp import models

test_payloads = {
    "security_event": [{"sqreen_payload_type": "security_event", "date_occurred": "2018-10-10T08:32:25.169232+00:00"}],
    "unknown": [{"sqreen_payload_type": "unknown"}]
}


def test_check_signature(test_client, compute_sig):
    test_tables = [
        {"name": "No X-Sqreen-Integrity header", "value": None, "expected": 400},
        {"name": "Empty X-Sqreen-Integrity header", "value": "", "expected": 400},
        {"name": "Invalid X-Sqreen-Integrity header", "value": "foobar", "expected": 400},
        {"name": "Valid X-Sqreen-Integrity header", "value": compute_sig(test_payloads["security_event"]),
         "expected": 204},
    ]

    for test in test_tables:
        headers = {}
        if test["value"] is not None:
            headers = {"X-Sqreen-Integrity": test["value"]}

        resp = test_client.post("/", json=test_payloads["security_event"], headers=headers)
        assert resp.status_code == test["expected"], test["name"]

        if test["expected"] == 400:
            resp_json = resp.get_json()
            assert resp_json["message"] == "Invalid X-Sqreen-Integrity signature"


def test_decode_sqreen_payload(test_client, compute_sig):
    headers = {"X-Sqreen-Integrity": compute_sig(test_payloads["unknown"])}

    resp = test_client.post("/", json=test_payloads["unknown"], headers=headers)
    assert resp.status_code == 400
    assert resp.get_json()["message"] == "Unable to decode Sqreen IO Payload"


def test_log_target_backend(test_client, test_app, compute_sig):
    test_app.target_backends = {
        "log": models.LogTargetBackend("./sqreenio.logs.test")
    }
    headers = {"X-Sqreen-Integrity": compute_sig(test_payloads["security_event"])}

    with patch.object(test_app.target_backends['log'].logger, 'warning') as m:
        test_client.post("/", json=test_payloads["security_event"], headers=headers)

    m.assert_called_once()
    log_message, = m.call_args[0]
    assert "2018-10-10" in log_message  # A bit weak but at least not brittle


def test_http_target_backend(test_client, test_app, compute_sig):
    remote_url = "http://mocked"
    test_app.target_backends = {
        "http": models.HTTPTargetBackend(remote_url)
    }
    headers = {"X-Sqreen-Integrity": compute_sig(test_payloads["security_event"])}

    mock_response = mock.Mock(spec=requests.post)
    mock_response.status_code = 200
    with patch('requests.post', return_value=mock_response) as m:
        resp = test_client.post("/", json=test_payloads["security_event"], headers=headers)
        assert resp.status_code == 204
    m.assert_called_once_with(remote_url, json=mock.ANY)

    with patch('requests.post', autospec=True, side_effect=requests.exceptions.RequestException) as m:
        test_client.post("/", json=test_payloads["security_event"], headers=headers)
        assert resp.status_code == 204
    m.assert_called_once()

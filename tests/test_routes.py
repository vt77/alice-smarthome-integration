import sys
import json

sys.path.append(".")

import unittest
from unittest.mock import patch
import uuid
from wsgi import app, tokens
from collections import namedtuple
from drivers import DeviceDriver, register_driver

import logging

logging.basicConfig(
    format="%(asctime)-15s %(process)d %(levelname)s %(name)s %(message)s",
    stream=sys.stdout,
    level=logging.DEBUG,
)
logger = logging.getLogger()

app.testing = True


(token, refresh, expired) = tokens.create_token_pair(100)

logger.debug("Using token %s", token)

mock_user = namedtuple("IOTUser", ["user_id", "nickname"])(*[200, "testuser"])

class MockDriver(DeviceDriver):
    name = 'mock'
    params = None

    def with_params(self,params):
        self.params = params

register_driver(MockDriver())


@patch("wsgi.auth.backend")
class TestYandexEndpoints(unittest.TestCase):
    headers = {"X-Request-Id": "1", "Authorization": f"Bearer {token}"}

    def no_test_ping(self, backend):
        client = app.test_client()
        rv = client.get("/ping")
        self.assertNotEqual(rv.data, None)

    def no_test_v1_ping_no_auth(self, backend):
        """Base path just ping"""
        client = app.test_client()
        rv = client.head("/v1.0/")
        self.assertEqual(rv.status_code, 403)

    def no_test_v1_ping(self, backend):
        """Base path just ping"""
        client = app.test_client()
        rv = client.head("/v1.0/", headers=self.headers)
        self.assertEqual(rv.status_code, 200)

    @patch("wsgi.backend")
    def no_test_v1_user_unlink(self, backend, auth_backend):
        client = app.test_client()
        self.headers["X-Request-Id"] = str(uuid.uuid1())
        auth_backend.load_user.return_value = mock_user
        rv = client.get("/v1.0/user/unlink", headers=self.headers)
        backend.user_unlink.assert_called_once_with(200)
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(rv.json["request_id"], self.headers["X-Request-Id"])

    @patch("wsgi.backend")
    def test_v1_devices(self, backend, auth_backend):
        client = app.test_client()
        self.headers["X-Request-Id"] = str(uuid.uuid1())
        auth_backend.load_user.return_value = mock_user
        backend.load_yandex_devices.return_value = [
            {
                "device_id": 213123,
                "name": "Lamp1",
                "description": "Main lamp1",
                "room": "Living room",
                "device_type": "light",
                "driver": "mock",
                "params": {
                    "action": "rfsend",
                    "params": {"freq": 315, "payload": "10965763,24"},
                },
                "device_info": None,
                "properties" : {'temperature':{}},
                "capabilities" : {'range':{}}
            }
        ]
        rv = client.get("/v1.0/user/devices", headers=self.headers)
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(rv.json["request_id"], self.headers["X-Request-Id"])
        self.assertIsNotNone(rv.json.get("payload"), self.headers["X-Request-Id"])
        self.assertEqual(rv.json["payload"]['user_id'], 'testuser')
        self.assertEqual(rv.json["payload"]['devices'][0]['name'], 'Lamp1')
        self.assertEqual(rv.json["payload"]['devices'][0]['type'], 'devices.types.light')


    @patch("wsgi.backend")
    def no_test_v1_devices_query(self, backend, auth_backend):
        client = app.test_client()
        self.headers["X-Request-Id"] = str(uuid.uuid1())
        auth_backend.load_user.return_value = mock_user
        backend.load_yandex_devices.return_value =         backend.load_yandex_devices.return_value = [
            {
                "device_id": "213123",
                "name": "Lamp1",
                "description": "Main lamp1",
                "room": "Living room",
                "device_type": "light",
                "driver": "mqtt",
                "params": {
                    "action": "rfsend",
                    "params": {"freq": 315, "payload": "10965763,24"},
                },
                "device_info": None,
                "properties" : [],
                "capabilities" : []
            }
        ]
        rv = client.post("/v1.0/user/devices/query", data=json.dumps({
            'devices' : [
                {"id": "abc-123","custom_data": {}},
                {"id": "213123","custom_data": {}}
            ]
        }),content_type='application/json', headers=self.headers)
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(rv.json["request_id"], self.headers["X-Request-Id"])

    def no_test_ping_v1_ping(self):
        """Base path just ping"""
        with app.test_request_context():
            (token, refresh, expires) = tokens.create_token_pair(100)
            self.assertNotEqual(token, None)
            self.assertNotEqual(refresh, None)
            self.assertNotEqual(expires, None)

            valid_token = tokens.validate_token(token)
            self.assertEqual(valid_token.user_id, 100)
            valid_token = tokens.validate_token(refresh, "refresh.alice.iothome.vt77")
            self.assertEqual(valid_token.user_id, 100)

    def no_test_auth_endpoint(self):
        """Auth endpoint test"""
        client = app.test_client()
        rv = client.get(
            "/auth?scope=alice.iothome.vt77&state=https%3A%2F%2Fsocial.yandex.ru%2Fbroker2%2Fauthz_in_web%2F174bca75472e49c1b5d4059312683e33%2Fcallback&redirect_uri=https%3A%2F%2Fsocial.yandex.net%2Fbroker%2Fredirect&response_type=code&client_id=iothome"
        )
        self.assertNotEqual(rv.data, None)
        rv = client.get(
            "/auth?scope=alice.iothome.vt77&state=https%3A%2F%2Fsocial.yandex.ru%2Fbroker2%2Fauthz_in_web%2F174bca75472e49c1b5d4059312683e33%2Fcallback&redirect_uri=https%3A%2F%2Fsocial.yandex.net%2Fbroker%2Fredirect&response_type=token&client_id=iothome"
        )
        self.assertEqual(rv.status_code, 302)

        from urllib import parse

        result = parse.urlsplit(rv.location)

        self.assertEqual(result.scheme, "https")
        self.assertEqual(result.netloc, "social.yandex.net")

        qs = parse.parse_qs(result.query)

        self.assertEqual(
            qs["state"][0],
            "https://social.yandex.ru/broker2/authz_in_web/174bca75472e49c1b5d4059312683e33/callback",
        )
        self.assertEqual(qs["token_type"][0], "bearer")

        code = qs["code"][0]

        """ 
            Token endpoint test 
            Should be execued with code from /auth endpoint
        """
        client = app.test_client()
        rv = client.get("/token?client_id=iothome&code=%s" % code)
        self.assertNotEqual(rv.data, None)
        token = rv.json["access_token"]
        refresh = rv.json["refresh_token"]
        headers = {"Authorization": "Bearer {}".format(token)}
        rv = client.get("/ping", headers=headers)
        self.assertEqual(rv.data.decode(), "PONG")

        # Try access protected endpoint with wrong aud
        headers = {"Authorization": "Bearer {}".format(refresh)}
        rv = client.get("/ping", headers=headers)
        self.assertEqual(rv.status_code, 403)

        """ Refresh token """
        rv = client.get("/refresh", headers=headers)
        self.assertEqual(rv.status_code, 200)
        token = rv.json["access_token"]
        headers = {"Authorization": "Bearer {}".format(token)}
        rv = client.get("/ping", headers=headers)
        self.assertEqual(rv.data.decode(), "PONG")


if __name__ == "__main__":
    unittest.main()

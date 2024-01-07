import os
import sys
import logging

from flask import (
    Flask,
    request,
    render_template,
    jsonify,
    abort,
    make_response,
)

import settings

sys.path.append(settings.LIB_DIR)
sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))

from lib.auth import VT77APIAuth, ApiAuthError, TokenAgentOAuth
from lib.backend import alice as backend

from integrations.yandex import YandexDevice, YandexDeviceBuilder, YandexError, YandexRequest, YandexResponse 
from drivers import DriverFactory
import drivers

import mysql.connector


config = {
    "user": settings.DB_USER,
    "password": settings.DB_PASS,
    "host": "localhost",
    "database": settings.DB_NAME,
    "raise_on_warnings": True,
}

backend.connection = mysql.connector.connect(**config)

drivers.settings = {
    'MQTT_HOST' : settings.MQTT_HOST,
    'MQTT_PREFIX' :settings.MQTT_PREFIX,
    'BACKEND' : backend
}



aud = "iot.vt77.com"
logging.basicConfig(
    format="%(asctime)-15s %(process)d %(levelname)s %(name)s %(message)s",
    stream=sys.stdout,
    level=logging.DEBUG,
)
logger = logging.getLogger()

app = Flask("alice-backend")

tokens = TokenAgentOAuth(aud)
auth = VT77APIAuth(backend, tokens)

@app.route("/")
def main():
    return "<h1>Yandex Alice integration</h1>"


@app.route("/dashboard")


@app.route("/ping")
@auth.token_auth(aud)
def _ping():
    try:
        user = auth.get_auth_user()
        return "PONG"
    except ApiAuthError:
        abort(403)

@app.route("/devices", methods=["GET"])
@auth.token_auth(aud)
def devices_ui():
    return render_template("devices.html", devices=["234234", "sdsdfgdfsg"])


@app.route("/v1.0/", methods=["HEAD"])
@auth.token_auth(aud)
def devices_ping():
    try:
        user = auth.get_auth_user()
        logger.debug("[ROUTE]Ping %s", user.user_id)
        return make_response("OK", 200)
    except ApiAuthError:
        logger.error("User not authorized")
        abort(403)


@app.route("/v1.0/user/unlink", methods=["GET"])
@auth.token_auth(aud)
def devices_unlink():
    """Called by yandex IoT framework on account unlink"""
    try:
        user = auth.get_auth_user()
        request_id = request.headers.get("X-Request-Id")
        logger.debug("[ROUTE]Unlink %s", user.user_id)
        backend.user_unlink(user.user_id)
        return jsonify({"request_id": request_id})
    except ApiAuthError:
        logger.error("User not authorized")
        abort(403)


@app.route("/v1.0/user/devices", methods=["GET"])
@auth.token_auth(aud)
def devices_list():
    """Called by yandex IoT framework to list devices
    See : https://yandex.ru/dev/dialogs/smart-home/doc/reference/get-devices.html
    """

    def build_device(
        device_id, name, description, room, device_type, driver, properties, capabilities, params, device_info
    ):
        """Build yandex device object"""

        driver = DriverFactory().get(driver)
        builder = (
            YandexDeviceBuilder(device_id, device_type)
            .with_name(name)
            .with_room(room)
            .with_custom_data({'driver':driver.name,'params':params})
            .with_description(description)
            .with_properties(properties)
            .with_capabilities(capabilities)
            .with_device_info(device_info)
        )
        return builder.build()

    try:
        user = auth.get_auth_user()
        devices = [build_device(**d) for d in backend.load_yandex_devices(user.user_id)]
        request_id = request.headers.get("X-Request-Id")
        return jsonify(dict(YandexResponse(request_id, devices,user.nickname)))
    except ApiAuthError:
        logger.error("User not authorized")
        abort(403)


@app.route("/v1.0/user/devices/query", methods=["POST"])
@auth.token_auth(aud)
def devices_status():
    """Called by yandex IoT framework to get devices status
    See : https://yandex.ru/dev/dialogs/smart-home/doc/reference/post-devices-query.html
    """
    try:
        user = auth.get_auth_user()
        request_id = request.headers.get("X-Request-Id")
        data = request.json
        devices = {d['device_id']:d for d in backend.load_yandex_devices(user.user_id)}
        ret = []
        for dev in YandexRequest(data).devices:
            if dev['id'] in devices:
                device = devices[dev['id']]
                builder = (
                    YandexDeviceBuilder(device.id)
                    .with_properties(YandexRequest.build_query_request(device.properties))
                    .with_capabilities(YandexRequest.build_query_request(device.capabilities))
                )
                device = builder.build()
                device.resolve()
                ret.append(device)
            else:
                dev.update(dict(YandexError("DEVICE_NOT_FOUND","Device not found")))
                ret.append(dev)

        return jsonify(dict(YandexResponse(request_id, ret)))
    except ApiAuthError:
        logger.error("User not authorized")
        abort(403)


@app.route("/v1.0/user/devices/action", methods=["POST"])
@auth.token_auth(aud)
def devices_action():
    """Called by yandex IoT framework to get devices status
    See : https://yandex.ru/dev/dialogs/smart-home/doc/reference/post-action.html
    """

    try:
        user = auth.get_auth_user()
        request_id = request.headers.get("X-Request-Id")
        data = request.json
        devices = {d['device_id']:YandexDevice(**d) for d in backend.load_yandex_devices(user.user_id)}
        ret = []

        for dev in YandexRequest(data).devices:
            if dev['id'] in devices:
                device = devices[dev['id']]
                builder = (
                    YandexDeviceBuilder(device.id)
                    .with_capabilities(YandexRequest.build_action_request(device.capabilities,dev['capabilities']))
                )
                # var device : YandexDevice
                device = builder.build()
                device.resolve(params={'user':user})
                ret.append( device )
            else:
                dev['action_result'] = dict(YandexError("DEVICE_NOT_FOUND","Device not found"))
                ret.append(device)
        return jsonify(dict(YandexResponse(request_id, ret)))
    except ApiAuthError:
        logger.error("User not authorized")
        abort(403)

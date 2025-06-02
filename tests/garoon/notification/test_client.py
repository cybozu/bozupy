import responses
from pytest_mock import MockFixture
from responses.registries import OrderedRegistry

from bozupy.garoon.notification import GaroonNotification
from ...testtool import set_mock_response, load, DUMMY_ACCESS_DATA, AuthMode

from bozupy.garoon.notification import client as sut


@responses.activate
def test_get_notifications(mocker: MockFixture) -> None:
    mocker.patch(
        "bozupy.garoon.notification.dxo.to_garoon_notification",
        return_value=None
    )
    res_json: dict = load("notification.json")
    set_mock_response("GET", "/g/api/v1/notification/items", 200, res_json, req_params={"limit": 100}, strict=True, auth=AuthMode.PASSWORD)

    actual: list[GaroonNotification] = [gn for gn in sut.get_notifications(DUMMY_ACCESS_DATA)]

    assert len(actual) == len(res_json["items"])


@responses.activate(registry=OrderedRegistry)
def test_get_notifications_offset(mocker: MockFixture) -> None:
    mocker.patch(
        "bozupy.garoon.notification.dxo.to_garoon_notification",
        return_value=None
    )
    res_json: dict = load("notification.json")
    res_json["hasNext"] = True
    set_mock_response("GET", "/g/api/v1/notification/items", 200, res_json, req_params={"limit": 100}, strict=True, auth=AuthMode.PASSWORD)
    res_json2: dict = load("notification.json")
    set_mock_response("GET", "/g/api/v1/notification/items", 200, res_json2, req_params={"limit": 100, "offset": 1}, auth=AuthMode.PASSWORD)

    actual: list[GaroonNotification] = [gn for gn in sut.get_notifications(DUMMY_ACCESS_DATA)]

    assert len(actual) == len(res_json["items"] + res_json2["items"])

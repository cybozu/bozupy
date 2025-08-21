import responses
from pytest_mock import MockFixture
from responses.registries import OrderedRegistry

from bozupy.kintone.app import client as sut
from bozupy.kintone.constant import AppFieldTypes
from ...testtool import set_mock_response, DUMMY_ACCESS_DATA, AuthMode


@responses.activate
def test_get_app_setting(mocker: MockFixture) -> None:
    mocker.patch(
        "bozupy.kintone.app.dxo.to_app_setting",
        return_value=None
    )
    set_mock_response("GET", "/k/v1/app/settings.json", 200, {}, req_params={"app": 1}, auth=AuthMode.API_TOKEN)
    sut.get_app_setting(1, DUMMY_ACCESS_DATA)


@responses.activate
def test_get_app_fields(mocker: MockFixture) -> None:
    mocker.patch(
        "bozupy.kintone.app.dxo.to_app_field",
        return_value=None
    )
    set_mock_response("GET", "/k/v1/app/form/fields.json", 200, {"properties": {}}, req_params={"app": 1}, auth=AuthMode.API_TOKEN)
    assert len(sut.get_app_fields(1, False, DUMMY_ACCESS_DATA)) == 0


@responses.activate
def test_get_app_fields_preview(mocker: MockFixture) -> None:
    mocker.patch(
        "bozupy.kintone.app.dxo.to_app_field",
        return_value=None
    )
    set_mock_response("GET", "/k/v1/app/form/fields.json", 403, {"properties": {}}, req_params={"app": 1}, auth=AuthMode.API_TOKEN)
    set_mock_response("GET", "/k/v1/preview/app/form/fields.json", 200, {"properties": {}}, req_params={"app": 1}, auth=AuthMode.API_TOKEN)
    assert len(sut.get_app_fields(1, True, DUMMY_ACCESS_DATA)) == 0


@responses.activate
def test_get_app_views() -> None:
    set_mock_response("GET", "/k/v1/app/views.json", 200, {}, req_params={"app": 1}, auth=AuthMode.API_TOKEN)
    sut.get_app_views(1, DUMMY_ACCESS_DATA)


@responses.activate
def test_get_app_process_conf() -> None:
    set_mock_response("GET", "/k/v1/app/status.json", 200, {}, req_params={"app": 1}, auth=AuthMode.API_TOKEN)
    sut.get_app_process_conf(1, DUMMY_ACCESS_DATA)


@responses.activate
def test_create_preview_app() -> None:
    set_mock_response("POST", "/k/v1/preview/app.json", 200, {"app": 1}, auth=AuthMode.PASSWORD)
    assert sut.create_preview_app("name", DUMMY_ACCESS_DATA) == 1


@responses.activate
def test_deploy_app() -> None:
    set_mock_response("POST", "/k/v1/preview/app/deploy.json", 200, {"app": 1}, auth=AuthMode.API_TOKEN)
    sut.deploy_app(1, DUMMY_ACCESS_DATA)


@responses.activate(registry=OrderedRegistry)
def test_update_app_name() -> None:
    set_mock_response("PUT", "/k/v1/preview/app/settings.json", 200, {}, auth=AuthMode.API_TOKEN)
    set_mock_response("POST", "/k/v1/preview/app/deploy.json", 200, {"app": 1}, auth=AuthMode.API_TOKEN)
    sut.update_app_name(1, "name", DUMMY_ACCESS_DATA)


@responses.activate
def test_add_field_to_preview_app() -> None:
    set_mock_response("POST", "/k/v1/preview/app/form/fields.json", 200, {"app": 1}, auth=AuthMode.API_TOKEN)
    sut.add_field_to_preview_app(1, AppFieldTypes.SINGLE_LINE_TEXT, "code", "label",  DUMMY_ACCESS_DATA, {"1", "2"})


@responses.activate
def test_get_app(mocker: MockFixture) -> None:
    mocker.patch(
        "bozupy.kintone.app.dxo.to_app",
        return_value=None
    )
    set_mock_response("GET", "/k/v1/app.json", 200, {}, req_params={"id": 1}, auth=AuthMode.API_TOKEN)
    sut.get_app(1, DUMMY_ACCESS_DATA)


@responses.activate
def test_get_apps(mocker: MockFixture) -> None:
    mocker.patch(
        "bozupy.kintone.app.dxo.to_app",
        return_value=None
    )
    set_mock_response("GET", "/k/v1/apps.json", 200, {"apps": [{}]}, auth=AuthMode.PASSWORD)
    assert len([_ for _ in sut.get_apps(DUMMY_ACCESS_DATA)]) == 1


@responses.activate(registry=OrderedRegistry)
def test_get_apps_offset(mocker: MockFixture) -> None:
    mocker.patch(
        "bozupy.kintone.app.dxo.to_app",
        return_value=None
    )
    set_mock_response("GET", "/k/v1/apps.json", 200, {"apps": [{} for _ in range(100)]}, req_params={"limit": 100, "offset": 0}, auth=AuthMode.PASSWORD)
    set_mock_response("GET", "/k/v1/apps.json", 200, {"apps": [{}]}, req_params={"limit": 100, "offset": 100}, auth=AuthMode.PASSWORD)
    assert len([_ for _ in sut.get_apps(DUMMY_ACCESS_DATA, limit=100)]) == 101


@responses.activate
def test_get_app_acl() -> None:
    set_mock_response("GET", "/k/v1/app/acl.json", 200, {"rights": {}}, req_params={"app": 1}, auth=AuthMode.API_TOKEN)
    sut.get_app_acl(1, DUMMY_ACCESS_DATA)


@responses.activate
def test_get_app_acl_403() -> None:
    set_mock_response("GET", "/k/v1/app/acl.json", 403, {"message": "権限がありません"}, req_params={"app": 1}, auth=AuthMode.API_TOKEN)
    assert len(sut.get_app_acl(1, DUMMY_ACCESS_DATA)) == 0


@responses.activate
def test_get_app_acl_520() -> None:
    set_mock_response("GET", "/k/v1/app/acl.json", 520, {"message": "ゲストスペース"}, req_params={"app": 1}, auth=AuthMode.API_TOKEN)
    assert len(sut.get_app_acl(1, DUMMY_ACCESS_DATA)) == 0

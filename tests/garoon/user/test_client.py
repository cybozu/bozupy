import responses
from responses.registries import OrderedRegistry

from ...testtool import set_mock_response, DUMMY_ACCESS_DATA, AuthMode

from bozupy.garoon.user import client as sut


@responses.activate
def test_get_user_code_and_garoon_ids() -> None:
    set_mock_response("GET", "/g/api/v1/base/users", 200, {"users": [{"code": "code", "id": 1}]}, req_params={"size": 100, "offset": 0}, auth=AuthMode.COOKIE)
    assert list(sut.get_user_code_and_garoon_ids(DUMMY_ACCESS_DATA)) == [("code", 1)]


@responses.activate(registry=OrderedRegistry)
def test_get_user_code_and_garoon_ids_offset() -> None:
    set_mock_response("GET", "/g/api/v1/base/users", 200, {"users": [{"code": f"code{i}", "id": i} for i in range(100)]}, req_params={"size": 100, "offset": 0}, auth=AuthMode.COOKIE)
    set_mock_response("GET", "/g/api/v1/base/users", 200, {"users": [{"code": "code101", "id": 101}]}, req_params={"size": 100, "offset": 100}, auth=AuthMode.COOKIE)
    assert len(list(sut.get_user_code_and_garoon_ids(DUMMY_ACCESS_DATA))) == 101


@responses.activate
def test_get_code_garoon_id_map() -> None:
    set_mock_response("GET", "/g/api/v1/base/users", 200, {"users": [{"code": "code", "id": 1}]}, req_params={"size": 100, "offset": 0}, auth=AuthMode.COOKIE)
    expected: dict[str, int] = {"code": 1}
    actual: dict[str, int] = sut.get_code_garoon_id_map(DUMMY_ACCESS_DATA)
    assert actual == expected


@responses.activate
def test_get_garoon_id_by_code() -> None:
    set_mock_response("GET", "/g/api/v1/base/users", 200, {"users": [{"code": "code", "id": 1}]}, req_params={"size": 100, "offset": 0}, auth=AuthMode.COOKIE)
    assert sut.get_garoon_id_by_code("code", DUMMY_ACCESS_DATA) == 1


@responses.activate
def test_get_garoon_id_by_code_not_found() -> None:
    set_mock_response("GET", "/g/api/v1/base/users", 200, {"users": [{"code": "code", "id": 1}]}, req_params={"size": 100, "offset": 0}, auth=AuthMode.COOKIE)
    assert sut.get_garoon_id_by_code("hoge", DUMMY_ACCESS_DATA) is None

import responses
from pytest_mock import MockFixture

from bozupy.kintone.space import client as sut
from ...testtool import set_mock_response, DUMMY_ACCESS_DATA, AuthMode


@responses.activate
def test_get_space(mocker: MockFixture) -> None:
    mocker.patch(
        "bozupy.kintone.space.dxo.to_space",
        return_value=None
    )
    set_mock_response(
        "GET",
        "/k/v1/space.json",
        200,
        res_json={},
        req_params={"id": 1},
        auth=AuthMode.PASSWORD)
    sut.get_space(1, DUMMY_ACCESS_DATA)


@responses.activate
def test_update_space_body() -> None:
    set_mock_response(
        "PUT",
        "/k/v1/space/body.json",
        200,
        res_json={},
        req_json={"id": 1, "body": "body"},
        auth=AuthMode.PASSWORD
    )
    sut.update_space_body(1, "body", DUMMY_ACCESS_DATA)


@responses.activate
def test_update_space_members() -> None:
    set_mock_response(
        "PUT",
        "/k/v1/space/members.json",
        200,
        res_json={},
        req_json={
            "id": 1,
            "members": [
                {
                    "entity": {
                        "type": "USER",
                        "code": "1"
                    },
                    "isAdmin": True
                },
                {
                    "entity": {
                        "type": "USER",
                        "code": "2"
                    },
                    "isAdmin": False
                },
                {
                    "entity": {
                        "type": "GROUP",
                        "code": "3"
                    }
                },
                {
                    "entity": {
                        "type": "ORGANIZATION",
                        "code": "4"
                    }
                }
            ]
        },
        auth=AuthMode.PASSWORD
    )
    sut.update_space_members(1, {"1"}, {"2"}, {"3"}, {"4"}, DUMMY_ACCESS_DATA)


@responses.activate
def test_create_thread() -> None:
    set_mock_response(
        "POST",
        "/k/v1/space/thread.json",
        200,
        res_json={"id": 1},
        req_json={"space": 1, "name": "name"},
        auth=AuthMode.PASSWORD
    )
    assert sut.create_thread(1, "name", DUMMY_ACCESS_DATA) == 1


@responses.activate
def test_update_thread() -> None:
    set_mock_response(
        "PUT",
        "/k/v1/space/thread.json",
        200,
        res_json={},
        req_json={"id": 1, "name": "name", "body": "body"},
        auth=AuthMode.PASSWORD
    )
    sut.update_thread(1, "name", "body", DUMMY_ACCESS_DATA)

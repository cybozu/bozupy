from typing import Pattern

import pytest
import responses

from bozupy.kintone import util as sut
from ..testtool import set_mock_response, DUMMY_ACCESS_DATA


@pytest.mark.parametrize(["app_id", "auth_header"], [
    [1, "X-Cybozu-API-Token"],
    [None, "X-Cybozu-Authorization"]
])
@responses.activate
def test_get(app_id: int | None, auth_header: str) -> None:
    set_mock_response("GET", "/k/v1/path.json", 200, {"hoge": "fuga"}, req_headers={auth_header})
    assert sut.get("path", None, app_id, access_data=DUMMY_ACCESS_DATA) == {"hoge": "fuga"}


@pytest.mark.parametrize(["app_id", "additional_app_ids", "auth_headers"], [
    [1, None, {"X-Cybozu-API-Token": "1"}],
    [1, {2}, {"X-Cybozu-API-Token": "1,2"}],
    [None, None, {"X-Cybozu-Authorization"}]
])
@responses.activate
def test_post(app_id: int, additional_app_ids: set[int] | None, auth_headers: dict[str, str | Pattern] | set[str] | None) -> None:
    set_mock_response("POST", "/k/v1/path.json", 200, {"hoge": "fuga"}, req_headers=auth_headers)
    assert sut.post("path", {"hoge": "fuga"}, app_id, access_data=DUMMY_ACCESS_DATA, additional_app_ids=additional_app_ids) == {"hoge": "fuga"}


@pytest.mark.parametrize(["app_id", "additional_app_ids", "auth_headers"], [
    [1, None, {"X-Cybozu-API-Token": "1"}],
    [1, {2}, {"X-Cybozu-API-Token": "1,2"}],
    [None, None, {"X-Cybozu-Authorization"}]
])
@responses.activate
def test_put(app_id: int, additional_app_ids: set[int] | None, auth_headers: dict[str, str | Pattern] | set[str] | None) -> None:
    set_mock_response("PUT", "/k/v1/path.json", 200, {"hoge": "fuga"}, req_headers=auth_headers)
    assert sut.put("path", {"hoge": "fuga"}, app_id, access_data=DUMMY_ACCESS_DATA, additional_app_ids=additional_app_ids) == {"hoge": "fuga"}


@pytest.mark.parametrize(["app_id", "auth_header"], [
    [1, "X-Cybozu-API-Token"],
    [None, "X-Cybozu-Authorization"]
])
@responses.activate
def test_delete(app_id: int | None, auth_header: str) -> None:
    set_mock_response("DELETE", "/k/v1/path.json", 200, {"hoge": "fuga"}, req_headers={auth_header})
    assert sut.delete("path", None, app_id, access_data=DUMMY_ACCESS_DATA) == {"hoge": "fuga"}

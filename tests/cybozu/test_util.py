from typing import Type

import pytest
import requests

from bozupy import AccessData
from bozupy.cybozu import util as sut
from bozupy.exception import AccessForbidden, LoginRequired, RateLimitExceeded, RequestNotSuccess, APIError, \
    NoJsonResponse


@pytest.mark.parametrize(["has_body", "app_ids", "tokens", "expected_headers"], [
    [False, None, None, {"X-Cybozu-Authorization"}],
    [True, None, None, {"Content-Type", "X-Cybozu-Authorization"}],
    [False, 1, {1: "hoge"}, {"X-Cybozu-API-Token"}],
    [False, {1}, {1: "hoge"}, {"X-Cybozu-API-Token"}],
    [False, {1, 2}, {1: "hoge"}, {"X-Cybozu-Authorization"}],
    [True, {1}, {1: "hoge"}, {"Content-Type", "X-Cybozu-API-Token"}],
    [False, set([]), {}, {"X-Cybozu-Authorization"}],
    [False, {1, 2}, {1: "hoge", 2: "fuga"}, {"X-Cybozu-API-Token"}]
])
def test_get_headers(has_body: bool, app_ids: set[int] | int | None, tokens: dict[int, str] | None, expected_headers: set[str]):
    # 必ず付与される必要のあるもの
    expected_headers.add("Host")
    expected_headers.add("User-Agent")
    actual: dict[str, str] = sut.get_headers(access_data=AccessData(
        subdomain="test", username="user", password="pass", app_tokens=tokens if tokens is not None else {}
    ), has_body=has_body, app_ids=app_ids)
    assert set(actual.keys()) == expected_headers
    if tokens is not None and len(tokens) >= 2:
        assert set(actual["X-Cybozu-API-Token"].split(",")) == set(tokens.values())


@pytest.mark.parametrize(["status_code", "location", "text", "is_plain", "expected_exception"], [
    [200, "", "{}", False, None],
    [200, "", "{\"success\": true}", False, None],
    [200, "", "{\"success\": false}", False, RequestNotSuccess],
    [401, "", "{}", False, LoginRequired],
    [302, "/login", "{}", False, LoginRequired],
    [403, "", "{}", False, AccessForbidden],
    [429, "", "{}", False, RateLimitExceeded],
    [502, "", "一時的な過負荷かメンテナンス", False, RateLimitExceeded],
    [502, "", "{}", False, requests.HTTPError],
    [520, "", "{}", False, APIError],
    [200, "", "hoge", False, NoJsonResponse],
    [200, "", "hoge", True, None]
])
def test_check_response(status_code: int, location: str, text: str, is_plain: bool, expected_exception: Type[Exception] | None) -> None:
    input_response: requests.Response = requests.Response()
    input_response.status_code = status_code
    input_response.headers["Location"] = location
    input_response.headers["Content-Type"] = "application/json; charset=utf-8"
    input_response._content = text.encode()
    if expected_exception is not None:
        with pytest.raises(expected_exception):
            sut.check_response(input_response, is_plain)
    else:
        sut.check_response(input_response, is_plain)

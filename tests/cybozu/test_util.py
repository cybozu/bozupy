import logging
from typing import Type
from unittest.mock import MagicMock

import pytest
import requests
from pytest_mock import MockerFixture

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
    [False, {1, 2}, {1: "hoge", 2: "fuga"}, {"X-Cybozu-API-Token"}],
    # 複数アプリに同一のトークンが設定されていてもAPIトークン認証を使う
    [False, {1, 2}, {1: "hoge", 2: "hoge"}, {"X-Cybozu-API-Token"}]
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


def _no_auth_access_data(app_tokens: dict[int, str] | None = None) -> AccessData:
    return AccessData(subdomain="test", username="", password="", app_tokens=app_tokens or {})


def _patch_secret_manager(mocker: MockerFixture, prefix: str = "op") -> MagicMock:
    mocker.patch("bozupy.cybozu.util.DEFAULT_SECRET_MANAGER_PREFIX", prefix)
    mocker.patch("bozupy.cybozu.util.DEFAULT_1PASSWORD_VAULT", "Employee")
    mocker.patch("bozupy.cybozu.util.DEFAULT_1PASSWORD_FIELD", "credential")
    return mocker.patch(
        "bozupy.cybozu.util.resolve_app_token",
        side_effect=lambda app_id, **kwargs: f"token{app_id}"
    )


def test_get_headers_シークレットストアからAPIトークンを取得する(mocker: MockerFixture) -> None:
    resolve_app_token: MagicMock = _patch_secret_manager(mocker)
    access_data: AccessData = _no_auth_access_data()
    actual: dict[str, str] = sut.get_headers(access_data=access_data, app_ids={1, 2})
    assert actual["X-Cybozu-API-Token"] == "token1,token2"
    resolve_app_token.assert_any_call(
        app_id=1,
        secret_manager_prefix="op",
        onepassword_vault="Employee",
        onepassword_field="credential"
    )
    assert resolve_app_token.call_count == 2
    # 取得したトークンはAccessDataに保持される
    assert access_data.app_tokens == {1: "token1", 2: "token2"}


def test_get_headers_取得済みのトークンはシークレットストアを見ない(mocker: MockerFixture) -> None:
    resolve_app_token: MagicMock = _patch_secret_manager(mocker)
    actual: dict[str, str] = sut.get_headers(access_data=_no_auth_access_data({1: "hoge"}), app_ids={1, 2})
    assert set(actual["X-Cybozu-API-Token"].split(",")) == {"hoge", "token2"}
    assert resolve_app_token.call_count == 1


def test_get_headers_シークレットストアにトークンがない場合(mocker: MockerFixture) -> None:
    _patch_secret_manager(mocker)
    mocker.patch("bozupy.cybozu.util.resolve_app_token", return_value="")
    with pytest.raises(ValueError, match="API Token not found in Secret Manager for app_id 1"):
        sut.get_headers(access_data=_no_auth_access_data(), app_ids={1})


def test_get_headers_パスワード認証ができる場合はシークレットストアを見ない(mocker: MockerFixture) -> None:
    resolve_app_token: MagicMock = _patch_secret_manager(mocker)
    actual: dict[str, str] = sut.get_headers(
        access_data=AccessData(subdomain="test", username="user", password="pass", app_tokens={}),
        app_ids={1}
    )
    assert "X-Cybozu-Authorization" in actual
    resolve_app_token.assert_not_called()


def test_get_headers_SECRET_MANAGER_PREFIXが未設定の場合(mocker: MockerFixture) -> None:
    resolve_app_token: MagicMock = _patch_secret_manager(mocker, prefix="")
    with pytest.raises(ValueError, match="No Auth Data"):
        sut.get_headers(access_data=_no_auth_access_data(), app_ids={1})
    resolve_app_token.assert_not_called()


@pytest.mark.parametrize(["app_ids"], [
    [None],
    [set([])]
])
def test_get_headers_app_idsがない場合はシークレットストアを見ない(
    app_ids: set[int] | None,
    mocker: MockerFixture,
    caplog: pytest.LogCaptureFixture
) -> None:
    resolve_app_token: MagicMock = _patch_secret_manager(mocker)
    with caplog.at_level(logging.INFO):
        with pytest.raises(ValueError, match="No Auth Data"):
            sut.get_headers(access_data=_no_auth_access_data(), app_ids=app_ids)
    resolve_app_token.assert_not_called()
    assert "Secret Manager" not in caplog.text

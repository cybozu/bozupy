import base64
import logging
from typing import Iterator

import requests

from .dto import AccessData
from ..exception import LoginRequired, AccessForbidden, RateLimitExceeded, RequestNotSuccess, APIError, NoJsonResponse
from ..setting import USER_AGENT, DEFAULT_SECRET_MANAGER_PREFIX, DEFAULT_1PASSWORD_VAULT, DEFAULT_1PASSWORD_FIELD
from ..util import debug_response_print, resolve_app_token


def get_headers(access_data: AccessData | None, has_body: bool = False, app_ids: set[int] | int | None = None) -> dict[str, str]:
    if access_data is None:
        access_data = AccessData()
    headers: dict[str, str] = {
        "Host": f"{access_data.host}:443",
        "User-Agent": USER_AGENT
    }
    if has_body:
        headers["Content-Type"] = "application/json"
    if app_ids is None:
        app_ids = set([])
    elif isinstance(app_ids, int) or isinstance(app_ids, float):
        app_ids = {int(app_ids)}
    api_token_header: str | None = _to_api_token_header(access_data, app_ids)
    if api_token_header is None and not access_data.has_auth:
        _fetch_app_tokens_from_secret_manager(access_data, app_ids)
        api_token_header = _to_api_token_header(access_data, app_ids)
    if api_token_header is not None:
        headers["X-Cybozu-API-Token"] = api_token_header
        logging.info("Use API Token")
    elif access_data.has_auth:
        headers["X-Cybozu-Authorization"] = base64.b64encode(
            f"{access_data.username}:{access_data.password}".encode()).decode()
        logging.info("Use Password")
    else:
        raise ValueError("No Auth Data")
    return headers


def _to_api_token_header(access_data: AccessData, app_ids: set[int]) -> str | None:
    if not app_ids or not app_ids.issubset(access_data.app_tokens):
        return None
    return ",".join(sorted({access_data.app_tokens[app_id] for app_id in app_ids}))


def _fetch_app_tokens_from_secret_manager(access_data: AccessData, app_ids: set[int]) -> None:
    missing_app_ids: set[int] = {app_id for app_id in app_ids if app_id not in access_data.app_tokens}
    if not DEFAULT_SECRET_MANAGER_PREFIX or not missing_app_ids:
        return
    logging.info(f"Get Auth Data from Secret Manager: {DEFAULT_SECRET_MANAGER_PREFIX}")
    for app_id in missing_app_ids:
        token_value: str = resolve_app_token(
            app_id=app_id,
            secret_manager_prefix=DEFAULT_SECRET_MANAGER_PREFIX,
            onepassword_vault=DEFAULT_1PASSWORD_VAULT,
            onepassword_field=DEFAULT_1PASSWORD_FIELD
        )
        if not token_value:
            raise ValueError(f"API Token not found in Secret Manager for app_id {app_id}")
        access_data.app_tokens[app_id] = token_value
        logging.info(f"Get API Token from Secret Manager for app_id {app_id}")


def check_response(res: requests.Response, is_plain: bool = False, no_debug_print: bool = False) -> None:
    if not no_debug_print:
        debug_response_print(res)
    # エラーを出し分けたいのでres.raise_for_status()は使わない
    if res.status_code <= 299:
        if is_plain:
            return
        elif "application/json" not in res.headers.get("Content-Type", ""):
            raise NoJsonResponse(res)
        try:
            res_json: dict | list = res.json()
        except ValueError:
            raise NoJsonResponse(res)
        if not isinstance(res_json, dict) or "success" not in res_json or res_json["success"]:
            return
        else:
            raise RequestNotSuccess(res)
    elif res.status_code == 401:
        raise LoginRequired(res)
    elif res.status_code == 302 and "/login" in res.headers.get("Location", ""):
        raise LoginRequired(res)
    elif res.status_code == 403:
        raise AccessForbidden(res)
    elif res.status_code == 429:
        raise RateLimitExceeded(res)
    elif res.status_code == 502 and "一時的な過負荷かメンテナンス" in res.text:
        raise RateLimitExceeded(res)
    elif res.status_code == 520:
        raise APIError(res)
    raise requests.HTTPError(response=res)


def get_offset_request(url: str, headers: dict, params: dict, key: str, limit: int) -> Iterator[dict]:
    offset: int = 0
    params["size"] = limit
    while True:
        ps: dict = params.copy()
        ps["offset"] = offset
        res: requests.Response = requests.get(url, headers=headers, params=ps)
        check_response(res)
        result: list[dict] = res.json()[key]
        yield from result
        if len(result) < limit:
            break
        offset += len(result)

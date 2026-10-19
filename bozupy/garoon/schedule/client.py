import logging
from datetime import datetime, date

import requests

# 何故かこの０ファイルだけfrom .dxo import to_eventだとテストでモックできなくなるので回避策
from . import dxo
from .dto import GaroonEvent, Facility, GaroonEventBase, GaroonEventComment
from ...cybozu.dto import AccessData
from ...cybozu.util import get_headers, check_response
from ...util import datetime_to_garoon_jst_str, date_to_garoon_jst_str, garoon_str_to_datetime

_DEFAULT_LIMIT: int = 100
_MAX_COMMENT_LIMIT: int = 1000


def get_event(event_id: int, access_data: AccessData | None = None) -> GaroonEventBase:
    logging.info(f"Get Event: {event_id}")
    if access_data is None:
        access_data = AccessData()
    # https://cybozu.dev/ja/garoon/docs/rest-api/schedule/get-schedule-event/
    res: requests.Response = requests.get(
        f"https://{access_data.host}/g/api/v1/schedule/events/{int(event_id)}",
        headers=get_headers(access_data=access_data)
    )
    check_response(res)
    return dxo.to_event(res.json())


def get_event_comments(event_id: int, access_data: AccessData | None = None) -> list[GaroonEventComment]:
    logging.info(f"Get Event Comments: {event_id}")
    if access_data is None:
        access_data = AccessData()
    # https://cybozu.dev/ja/garoon/docs/rest-api/schedule/get-schedule-comments/
    comments: list[dict] = []
    while True:
        res: requests.Response = requests.get(
            f"https://{access_data.host}/g/api/v1/schedule/events/{int(event_id)}/comments",
            headers=get_headers(access_data=access_data),
            params={"limit": str(_MAX_COMMENT_LIMIT), "offset": str(len(comments))}
        )
        check_response(res)
        json_: dict = res.json()
        result: list[dict] = json_.get("comments", [])
        comments.extend(result)
        if not json_.get("hasNext") or not result:
            break
    # 書き込み日時の降順で返ってくる
    return [dxo.to_event_comment(comment, int(event_id), access_data.subdomain, access_data.is_dev) for comment in comments]


def add_event(start: datetime, end: datetime, title: str, attendees: set[str], access_data: AccessData | None = None) -> int:
    logging.info(f"Add Event: {title}")
    if access_data is None:
        access_data = AccessData()
    res: requests.Response = requests.post(
        f"https://{access_data.host}/g/api/v1/schedule/events",
        headers=get_headers(access_data=access_data, has_body=True),
        json={
            "eventType": "REGULAR",
            "subject": title,
            "start": {
                "dateTime": datetime_to_garoon_jst_str(start),
                "timeZone": "Asia/Tokyo"
            },
            "end": {
                "dateTime": datetime_to_garoon_jst_str(end),
                "timeZone": "Asia/Tokyo"
            },
            "attendees": [
                {
                    "type": "USER",
                    "code": attendee
                } for attendee in attendees
            ]
        }
    )
    check_response(res)
    return int(res.json()["id"])


def update_event(event_id: int, start: datetime | None, end: datetime, title: str, attendees: set[str], access_data: AccessData | None = None) -> None:
    logging.info(f"Update Event: {event_id}: {title}")
    if access_data is None:
        access_data = AccessData()
    res: requests.Response = requests.patch(
        f"https://{access_data.host}/g/api/v1/schedule/events/{int(event_id)}",
        headers=get_headers(access_data=access_data, has_body=True),
        json={
            "eventType": "REGULAR",
            "subject": title,
            "start": {
                "dateTime": datetime_to_garoon_jst_str(start) if start else None,
                "timeZone": "Asia/Tokyo"
            },
            "end": {
                "dateTime": datetime_to_garoon_jst_str(end),
                "timeZone": "Asia/Tokyo"
            },
            "attendees": [
                {
                    "type": "USER",
                    "code": attendee
                } for attendee in attendees
            ]
        }
    )
    check_response(res)
    return None


def search_events(access_data: AccessData | None = None, query: str | None = None, user_id: int | None = None, start: date | None = None, end: date | None = None, facility_id: int | None = None) -> list[GaroonEvent]:
    logging.info("Search Events")
    if access_data is None:
        access_data = AccessData()
    if user_id and facility_id:
        raise ValueError("user_id and facility_id cannot be specified at the same time")
    # https://cybozu.dev/ja/garoon/docs/rest-api/schedule/get-schedule-events/
    params: dict = {
        "limit": str(_DEFAULT_LIMIT),
    }
    events: list[dict] = []
    while True:
        params["offset"] = len(events)
        if query:
            params["keyword"] = query
        if start:
            params["rangeStart"] = date_to_garoon_jst_str(start)
        if end:
            params["rangeEnd"] = date_to_garoon_jst_str(end)
        if user_id:
            params["targetType"] = "user"
            params["target"] = str(int(user_id))
        elif facility_id:
            params["targetType"] = "facility"
            params["target"] = str(int(facility_id))
        res: requests.Response = requests.get(
            f"https://{access_data.host}/g/api/v1/schedule/events",
            headers=get_headers(access_data=access_data),
            params=params
        )
        check_response(res)
        json_: dict = res.json()
        result: list[dict] = json_.get("events", [])
        events.extend(result)
        # limitより少ない件数で返ることがあるのでhasNextで判定する。hasNextがない場合は件数で判定する
        has_next: bool | None = json_.get("hasNext")
        if not result or not (len(result) >= _DEFAULT_LIMIT if has_next is None else has_next):
            break
    return [dxo.to_normal_event(event) for event in events]


def get_available_times(user_codes: list[str], time_interval: int, start: datetime, end: datetime, access_data: AccessData | None = None) -> list[tuple[datetime, datetime]]:
    logging.info("Get Available Times")
    if access_data is None:
        access_data = AccessData()
    params: dict = {
        "timeRanges": {
            "start": datetime_to_garoon_jst_str(start),
            "end": datetime_to_garoon_jst_str(end)
        },
        "timeInterval": time_interval,
        "attendees": [
            {"type": "USER", "code": user_code} for user_code in user_codes
        ]
    }
    res: requests.Response = requests.post(
        f"https://{access_data.host}/g/api/v1/schedule/searchAvailableTimes",
        headers=get_headers(access_data=access_data, has_body=True),
        json=params
    )
    check_response(res)
    times_list: list[dict] = res.json().get("availableTimes", [])
    return [(garoon_str_to_datetime(json_["start"]), garoon_str_to_datetime(json_["end"])) for json_ in times_list]


def get_event_data_store(access_data: AccessData, event_id: int, name: str) -> dict:
    logging.info(f"Get Event Data Store: {event_id}: {name}")
    res: requests.Response = requests.get(
        f"https://{access_data.host}/g/api/v1/schedule/events/{int(event_id)}/datastore/{name}",
        headers=get_headers(access_data=access_data)
    )
    check_response(res)
    return res.json()["value"]


def add_event_data_store(access_data: AccessData, event_id: int, name: str, data: dict[str, str | int | dict | list]) -> None:
    logging.info(f"Add Event Data Store: {event_id}: {name}")
    res: requests.Response = requests.post(
        f"https://{access_data.host}/g/api/v1/schedule/events/{int(event_id)}/datastore/{name}",
        headers=get_headers(access_data=access_data, has_body=True),
        json={"value": data}
    )
    check_response(res)


def update_event_data_store(access_data: AccessData, event_id: int, name: str, data: dict[str, str | int | dict | list]) -> None:
    logging.info(f"Update Event Data Store: {event_id}: {name}")
    res: requests.Response = requests.put(
        f"https://{access_data.host}/g/api/v1/schedule/events/{int(event_id)}/datastore/{name}",
        headers=get_headers(access_data=access_data, has_body=True),
        json={"value": data}
    )
    check_response(res)


def get_facilities(access_data: AccessData) -> list[Facility]:
    logging.info("Get Facilities")
    facilities: list[dict] = []
    params: dict = {
        "limit": str(_DEFAULT_LIMIT),
    }
    while True:
        params["offset"] = len(facilities)
        res: requests.Response = requests.get(
            f"https://{access_data.host}/g/api/v1/schedule/facilities",
            headers=get_headers(access_data=access_data),
            params=params
        )
        check_response(res)
        result: list[dict] = res.json().get("facilities", [])
        facilities.extend(result)
        if len(result) < _DEFAULT_LIMIT:
            break
    return [dxo.to_facility(facility) for facility in facilities]

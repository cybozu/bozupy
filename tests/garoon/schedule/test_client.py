from datetime import datetime

import pytest
import responses
from pytest_mock import MockerFixture
from responses.registries import OrderedRegistry

from bozupy.garoon.schedule import client as sut
from bozupy.garoon.schedule.dto import GaroonEventComment
from ...testtool import set_mock_response, DUMMY_ACCESS_DATA, not_raises, AuthMode


@responses.activate
def test_get_event(mocker: MockerFixture) -> None:
    set_mock_response("GET", "/g/api/v1/schedule/events/1", 200, {}, auth=AuthMode.PASSWORD)
    mocker.patch(
        "bozupy.garoon.schedule.dxo.to_event",
        return_value=None
    )
    with not_raises():
        sut.get_event(1, DUMMY_ACCESS_DATA)


def _comment(comment_id: int) -> dict:
    return {
        "id": str(comment_id),
        "body": f"comment{comment_id}",
        "createdAt": "2024-04-19T04:46:25Z",
        "creator": {"id": "1", "code": "user1", "name": "ユーザー1"},
        "mentions": []
    }


@responses.activate(registry=OrderedRegistry)
def test_get_event_comments() -> None:
    set_mock_response(
        "GET",
        "/g/api/v1/schedule/events/1/comments",
        200,
        {"comments": [_comment(3), _comment(2)], "hasNext": True},
        req_params={"limit": "1000", "offset": "0"},
        strict=True,
        auth=AuthMode.PASSWORD
    )
    set_mock_response(
        "GET",
        "/g/api/v1/schedule/events/1/comments",
        200,
        {"comments": [_comment(1)], "hasNext": False},
        req_params={"limit": "1000", "offset": "2"},
        strict=True,
        auth=AuthMode.PASSWORD
    )
    actual: list[GaroonEventComment] = sut.get_event_comments(1, DUMMY_ACCESS_DATA)
    assert [comment.id for comment in actual] == [3, 2, 1]
    assert [comment.event_id for comment in actual] == [1, 1, 1]


@responses.activate
def test_get_event_comments_コメントがない場合() -> None:
    set_mock_response("GET", "/g/api/v1/schedule/events/1/comments", 200, {"comments": [], "hasNext": False}, auth=AuthMode.PASSWORD)
    assert sut.get_event_comments(1, DUMMY_ACCESS_DATA) == []


@responses.activate
def test_add_event() -> None:
    set_mock_response("POST", "/g/api/v1/schedule/events", 200, {"id": "1"}, auth=AuthMode.PASSWORD)
    with not_raises():
        sut.add_event(datetime.now(), datetime.now(), "title", set([]), DUMMY_ACCESS_DATA)


@responses.activate
def test_update_event() -> None:
    set_mock_response("PATCH", "/g/api/v1/schedule/events/1", 200, {}, auth=AuthMode.PASSWORD)
    with not_raises():
        sut.update_event(1, datetime.now(), datetime.now(), "title", set([]), DUMMY_ACCESS_DATA)


@responses.activate
def test_search_events() -> None:
    set_mock_response("GET", "/g/api/v1/schedule/events", 200, {}, auth=AuthMode.PASSWORD)
    with not_raises():
        sut.search_events(DUMMY_ACCESS_DATA)


@responses.activate(registry=OrderedRegistry)
def test_search_events_offset(mocker: MockerFixture) -> None:
    mocker.patch(
        "bozupy.garoon.schedule.dxo.to_normal_event",
        return_value=None
    )
    set_mock_response("GET", "/g/api/v1/schedule/events", 200, {"events": [_ for _ in range(100)]}, req_params={"limit": 100, "offset": 0}, auth=AuthMode.PASSWORD)
    set_mock_response("GET", "/g/api/v1/schedule/events", 200, {"events": [_ for _ in range(1)]}, req_params={"limit": 100, "offset": 100}, auth=AuthMode.PASSWORD)
    with not_raises():
        assert len(sut.search_events(DUMMY_ACCESS_DATA)) == 101


@responses.activate(registry=OrderedRegistry)
def test_search_events_hasNextがある場合は件数が少なくても次を取得する(mocker: MockerFixture) -> None:
    mocker.patch(
        "bozupy.garoon.schedule.dxo.to_normal_event",
        return_value=None
    )
    set_mock_response("GET", "/g/api/v1/schedule/events", 200, {"events": [_ for _ in range(10)], "hasNext": True}, req_params={"limit": 100, "offset": 0}, auth=AuthMode.PASSWORD)
    set_mock_response("GET", "/g/api/v1/schedule/events", 200, {"events": [_ for _ in range(1)], "hasNext": False}, req_params={"limit": 100, "offset": 10}, auth=AuthMode.PASSWORD)
    assert len(sut.search_events(DUMMY_ACCESS_DATA)) == 11


@responses.activate
def test_search_events_施設を指定した場合(mocker: MockerFixture) -> None:
    mocker.patch(
        "bozupy.garoon.schedule.dxo.to_normal_event",
        return_value=None
    )
    set_mock_response(
        "GET",
        "/g/api/v1/schedule/events",
        200,
        {"events": [1], "hasNext": False},
        req_params={"limit": 100, "offset": 0, "targetType": "facility", "target": 5},
        strict=True,
        auth=AuthMode.PASSWORD
    )
    assert len(sut.search_events(DUMMY_ACCESS_DATA, facility_id=5)) == 1


def test_search_events_ユーザーと施設を同時に指定した場合() -> None:
    with pytest.raises(ValueError):
        sut.search_events(DUMMY_ACCESS_DATA, user_id=1, facility_id=5)


@responses.activate
def test_get_available_times() -> None:
    set_mock_response("POST", "/g/api/v1/schedule/searchAvailableTimes", 200, {}, auth=AuthMode.PASSWORD)
    with not_raises():
        sut.get_available_times([], 1, datetime.now(), datetime.now(), DUMMY_ACCESS_DATA)


@responses.activate
def test_get_event_data_store():
    set_mock_response("GET", "/g/api/v1/schedule/events/1/datastore/hoge", 200, {"value": {}}, auth=AuthMode.PASSWORD)
    with not_raises():
        sut.get_event_data_store(DUMMY_ACCESS_DATA, 1, "hoge")


@responses.activate
def test_add_event_data_store() -> None:
    set_mock_response("POST", "/g/api/v1/schedule/events/1/datastore/hoge", 200, {}, auth=AuthMode.PASSWORD)
    with not_raises():
        sut.add_event_data_store(DUMMY_ACCESS_DATA, 1, "hoge", {})


@responses.activate
def test_update_event_data_store() -> None:
    set_mock_response("PUT", "/g/api/v1/schedule/events/1/datastore/hoge", 200, {}, auth=AuthMode.PASSWORD)
    with not_raises():
        sut.update_event_data_store(DUMMY_ACCESS_DATA, 1, "hoge", {})


@responses.activate
def test_get_facilities() -> None:
    set_mock_response("GET", "/g/api/v1/schedule/facilities", 200, {}, auth=AuthMode.PASSWORD)
    with not_raises():
        sut.get_facilities(DUMMY_ACCESS_DATA)


@responses.activate(registry=OrderedRegistry)
def test_get_facilities_offset(mocker: MockerFixture) -> None:
    mocker.patch(
        "bozupy.garoon.schedule.dxo.to_facility",
        return_value=None
    )
    set_mock_response("GET", "/g/api/v1/schedule/facilities", 200, {"facilities": [_ for _ in range(100)]}, req_params={"limit": 100, "offset": 0}, auth=AuthMode.PASSWORD)
    set_mock_response("GET", "/g/api/v1/schedule/facilities", 200, {"facilities": [_ for _ in range(1)]}, req_params={"limit": 100, "offset": 100}, auth=AuthMode.PASSWORD)
    with not_raises():
        assert len(sut.get_facilities(DUMMY_ACCESS_DATA)) == 101

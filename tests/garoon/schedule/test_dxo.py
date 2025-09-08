from datetime import datetime

import pytest

from bozupy.garoon.schedule import dxo as sut, GaroonEvent
from ...testtool import load


@pytest.mark.parametrize(["filename", "has_start", "has_repeat_info"], [
    ["event.json", True, False],
    ["event_no_watchers.json", True, False],
    ["event-repeating.json", False, True]
])
def test_to_event(filename: str, has_start: bool, has_repeat_info: bool):
    event_json: dict = load(filename)
    actual: GaroonEvent = sut.to_event(event_json)
    assert actual.id
    assert actual.subject
    assert actual.creator_code
    assert actual.event_type
    if has_start:
        assert actual.start
        assert isinstance(actual.start, datetime)
    else:
        assert actual.start is None
    if has_repeat_info:
        assert actual.repeat_info
        assert actual.repeat_info.period_start
        assert actual.repeat_info.period_end
    else:
        assert actual.repeat_info is None
    assert actual.created_at


@pytest.mark.parametrize(["filename"], [
    ["facilities.json"]
])
def test_to_facility(filename: str):
    facility_json: dict = load(filename)["facilities"][0]
    actual = sut.to_facility(facility_json)
    assert actual.code
    assert actual.id
    assert actual.name

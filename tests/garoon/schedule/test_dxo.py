from datetime import datetime

import pytest

from bozupy.garoon.schedule import dxo as sut, GaroonEvent
from ...testtool import load


@pytest.mark.parametrize(["filename"], [
    ["event.json"],
    ["event_no_watchers.json"]
])
def test_to_event(filename: str):
    event_json: dict = load(filename)
    actual: GaroonEvent = sut.to_event(event_json)
    assert actual.id
    assert actual.subject
    assert actual.creator_code
    assert actual.event_type
    assert actual.start
    assert actual.created_at
    assert isinstance(actual.start, datetime)


@pytest.mark.parametrize(["filename"], [
    ["facilities.json"]
])
def test_to_facility(filename: str):
    facility_json: dict = load(filename)["facilities"][0]
    actual = sut.to_facility(facility_json)
    assert actual.code
    assert actual.id
    assert actual.name

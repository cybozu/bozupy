from typing import Type

import pytest

from bozupy.garoon.schedule import dxo as sut, GaroonEvent
from bozupy.garoon.schedule.dto import GaroonEventBase, GaroonRepeatEvent
from ...testtool import load


@pytest.mark.parametrize(["filename", "expected_class"], [
    ["event.json", GaroonEvent],
    ["event_no_watchers.json", GaroonEvent],
    ["event-repeating.json", GaroonRepeatEvent]
])
def test_to_event(filename: str, expected_class: Type[GaroonEventBase]):
    event_json: dict = load(filename)
    actual: GaroonEventBase = sut.to_event(event_json)
    assert isinstance(actual, expected_class)
    assert actual.id
    assert actual.subject
    assert actual.creator_code
    assert actual.event_type
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

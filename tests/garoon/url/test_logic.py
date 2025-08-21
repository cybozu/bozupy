import pytest
from bozupy.garoon.url.dto import GaroonUrl, GaroonEventUrl

from bozupy.garoon.url import logic as sut


@pytest.mark.parametrize(["input_"], [
    ["https://test.cybozu.com/g/schedule/view.csp?event=1"],
    ["https://test.cybozu.com/g/schedule/view.csp?hoge=1&event=1"],
])
def test_parse_garoon_url_schedule(input_: str):
    actual: GaroonUrl | None = sut.parse_garoon_url(input_)
    assert actual is not None
    assert isinstance(actual, GaroonEventUrl)
    assert actual.event_id == 1
    assert actual.url() == "https://test.cybozu.com/g/schedule/view.csp?event=1"


@pytest.mark.parametrize(["input_", "expected"], [
    ["https://test.s.cybozu.com/g/schedule/view.csp?event=1", "https://test.cybozu.com/g/schedule/view.csp?event=1"],

])
def test_parse_garoon_url_secure(input_: str, expected: str):
    actual: GaroonUrl | None = sut.parse_garoon_url(input_)
    assert actual is not None
    assert actual.url() == expected


@pytest.mark.parametrize(["input_"], [
    [""],
    ["http://google.com"],
    ["hoge-hoge"],
    ["https://test.cybozu.com/g/schedule/view.csp?event=a"]
])
def test_parse_garoon_url_error(input_: str):
    assert sut.parse_garoon_url(input_) is None

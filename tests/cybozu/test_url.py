from pytest_mock import MockerFixture

from bozupy.cybozu import url as sut
from ..testtool import not_raises


def test_parse_url_kintone(mocker: MockerFixture) -> None:
    mocker.patch("bozupy.kintone.url.logic.parse_kintone_url", return_value=True)
    mocker.patch("bozupy.garoon.url.logic.parse_garoon_url", side_effect=AssertionError())
    with not_raises():
        assert sut.parse_url("https://example.cybozu.com/k/1") is not None


def test_parse_url_garoon(mocker: MockerFixture) -> None:
    mocker.patch("bozupy.kintone.url.logic.parse_kintone_url", side_effect=AssertionError())
    mocker.patch("bozupy.garoon.url.logic.parse_garoon_url", return_value=True)
    with not_raises():
        assert sut.parse_url("https://example.cybozu.com/g/1") is not None


def test_parse_url_none(mocker: MockerFixture) -> None:
    mocker.patch("bozupy.kintone.url.logic.parse_kintone_url", side_effect=AssertionError())
    mocker.patch("bozupy.garoon.url.logic.parse_garoon_url", side_effect=AssertionError())
    with not_raises():
        assert sut.parse_url("https://example.cybozu.com/") is None

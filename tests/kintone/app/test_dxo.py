import pytest

from ...testtool import load

from bozupy.kintone.app import dxo as sut, KintoneApp, KintoneAppField


@pytest.mark.parametrize(["filename"], [
    ["app.json"]
])
def test_to_app(filename: str):
    actual: KintoneApp = sut.to_app(load(filename))
    assert actual.id
    assert actual.name


@pytest.mark.parametrize(["filename"], [
    ["setting.json"]
])
def test_to_app_setting(filename: str):
    actual = sut.to_app_setting(load(filename))
    assert actual.name
    assert actual.revision


@pytest.mark.parametrize(["filename"], [
    ["fields.json"]
])
def test_to_app_field(filename: str):
    for field_json in load(filename)["properties"].values():
        actual: KintoneAppField = sut.to_app_field(field_json)
        assert actual.label
        assert actual.type
        assert actual.code

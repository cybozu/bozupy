import pytest

from bozupy.kintone.space.dto import Space

from bozupy.kintone.space import dxo as sut
from ...testtool import load


@pytest.mark.parametrize(["filename"], [
    ["space.json"]
])
def test_to_space(filename: str) -> None:
    actual: Space = sut.to_space(load(filename))
    assert actual is not None
    assert isinstance(actual, Space)
    assert actual.id is not None
    assert actual.default_thread_id is not None
    assert actual.creator_code is not None
    assert actual.modifier_code is not None
    assert actual.created_at is not None
    assert actual.modified_at is not None
    assert actual.body is not None
    assert actual.name is not None


@pytest.mark.parametrize(["filename"], [
    ["space2.json"]
])
def test_to_space_info_user_not_exist(filename: str) -> None:
    actual: Space = sut.to_space(load(filename))
    assert actual is not None
    assert isinstance(actual, Space)
    assert actual.id is not None
    assert actual.default_thread_id is not None
    assert actual.creator_code is None
    assert actual.modifier_code is None
    assert actual.created_at is not None
    assert actual.modified_at is not None
    assert actual.body is not None
    assert actual.name is not None

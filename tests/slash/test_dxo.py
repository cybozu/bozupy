import pytest

from bozupy.slash import dxo as sut
from bozupy.slash.dto import User, Group
from ..testtool import load, not_raises


@pytest.mark.parametrize(["filename"], [
    ["user1.json"],
    ["user2.json"]
])
def test_to_user(filename: str):
    data: dict = load(filename, "user")
    with not_raises():
        result: User = sut.to_user(data)
    assert result.code
    assert result.id
    assert result.created_at
    assert result.updated_at
    assert result.is_valid is not None
    assert result.name
    assert result.locale
    assert result.timezone


@pytest.mark.parametrize(["filename"], [
    ["group1.json"],
    ["group2.json"]
])
def test_to_group(filename: str):
    data: dict = load(filename, "group")
    with not_raises():
        result: Group = sut.to_group(data)
    assert result.code
    assert result.id
    assert result.name


@pytest.mark.parametrize(["filename"], [
    ["org1.json"],
    ["org2.json"]
])
def test_to_org(filename: str):
    data: dict = load(filename, "org")
    with not_raises():
        result = sut.to_org(data)
    assert result.code
    assert result.id
    assert result.name
    assert result.parent_code is not None
    assert result.description is not None

import responses
import pytest
from pytest_mock import MockFixture

from ..testtool import load, set_mock_response, DUMMY_ACCESS_DATA, AuthMode

from bozupy.slash import client as sut, Org, Group


@pytest.mark.parametrize(["filename"], [
    ["users1.json"]
])
@responses.activate
def test_get_users(filename: str, mocker: MockFixture) -> None:
    # https://cybozu.dev/ja/common/docs/user-api/users/get-users/
    mocker.patch(
        "bozupy.slash.dxo.to_user",
        return_value=None
    )
    set_mock_response("GET", "/v1/users.json", res_json=load(filename, "users"), auth=AuthMode.PASSWORD)
    results: list = [u for u in sut.get_users(DUMMY_ACCESS_DATA)]
    assert len(results) == 2


@responses.activate
def test_get_users_有効なユーザーのみ(mocker: MockFixture) -> None:
    mocker.patch(
        "bozupy.slash.dxo.to_user",
        return_value=None
    )
    set_mock_response("GET", "/v1/users.json", res_json=load("invalid.json", "users"), auth=AuthMode.PASSWORD)
    results: list = [u for u in sut.get_users(DUMMY_ACCESS_DATA, is_valid_only=True)]
    assert len(results) == 0


@pytest.mark.parametrize(["filename"], [
    ["groups1.json"]
])
@responses.activate
def test_get_groups(filename: str, mocker: MockFixture) -> None:
    mocker.patch(
        "bozupy.slash.dxo.to_group",
        return_value=None
    )
    set_mock_response("GET", "/v1/groups.json", res_json=load(filename, "groups"), auth=AuthMode.PASSWORD)
    results: list = [u for u in sut.get_groups(DUMMY_ACCESS_DATA)]
    assert len(results) == 2


@pytest.mark.parametrize(["filename"], [
    ["orgs1.json"]
])
@responses.activate
def test_get_orgs(filename: str, mocker: MockFixture) -> None:
    mocker.patch(
        "bozupy.slash.dxo.to_org",
        return_value=None
    )
    set_mock_response("GET", "/v1/organizations.json", res_json=load(filename, "orgs"), auth=AuthMode.PASSWORD)
    results: list = [u for u in sut.get_orgs(DUMMY_ACCESS_DATA)]
    assert len(results) == 2


@pytest.mark.parametrize(["filename"], [
    ["orgUsers1.json"]
])
@responses.activate
def test_get_user_codes_by_org_code(filename: str) -> None:
    set_mock_response("GET", "/v1/organization/users.json", res_json=load(filename, "orgUsers"), auth=AuthMode.PASSWORD)
    results: list = [u for u in sut.get_user_codes_by_org_code("org1", DUMMY_ACCESS_DATA)]
    assert len(results) == 1


@pytest.mark.parametrize(["filename"], [
    ["groupUsers1.json"]
])
@responses.activate
def test_get_user_codes_by_group_code(filename: str) -> None:
    set_mock_response("GET", "/v1/group/users.json", res_json=load(filename, "groupUsers"), auth=AuthMode.PASSWORD)
    results: list = [u for u in sut.get_user_codes_by_group_code("group1", DUMMY_ACCESS_DATA)]
    assert len(results) == 1


@pytest.mark.parametrize(["filename"], [
    ["orgsByUserCode1.json"]
])
@responses.activate
def test_get_orgs_by_user_code(filename: str) -> None:
    set_mock_response("GET", "/v1/user/organizations.json", res_json=load(filename, "users"), auth=AuthMode.PASSWORD)
    actual: list[Org] = sut.get_orgs_by_user_code("user_code", DUMMY_ACCESS_DATA)
    assert len(actual) == 1


@pytest.mark.parametrize(["filename"], [
    ["groupsByUserCode1.json"]
])
@responses.activate
def test_get_groups_by_user_code(filename: str) -> None:
    set_mock_response("GET", "/v1/user/groups.json", res_json=load(filename, "users"), auth=AuthMode.PASSWORD)
    actual: list[Group] = sut.get_groups_by_user_code("user_code", DUMMY_ACCESS_DATA)
    assert len(actual) == 2

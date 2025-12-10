from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
import responses
from pytest_mock import MockFixture
from responses.registries import OrderedRegistry

from bozupy.kintone.record.dto import KintoneRecord
from ...testtool import set_mock_response, DUMMY_ACCESS_DATA, AuthMode

from bozupy.kintone.record import client as sut, KintoneRecordSingleLineTextField


@responses.activate
def test_get_records_by_offset() -> None:
    set_mock_response("GET", "/k/v1/records.json", 200, {"records": []}, req_params={"app": 1}, auth=AuthMode.API_TOKEN)
    assert len(list(sut.get_records_by_offset(1, None, DUMMY_ACCESS_DATA))) == 0


@responses.activate(registry=OrderedRegistry)
def test_get_records(mocker: MockFixture) -> None:
    set_mock_response("POST", "/k/v1/records/cursor.json", 200, {"id": "dummy"}, req_json={"app": 1, "size": 500}, auth=AuthMode.API_TOKEN)
    set_mock_response("GET", "/k/v1/records/cursor.json", 200, {"records": [], "next": False}, req_params={"id": "dummy"}, auth=AuthMode.API_TOKEN)
    set_mock_response("DELETE", "/k/v1/records/cursor.json", 200, {}, req_params={"id": "dummy"}, auth=AuthMode.API_TOKEN)
    mocker.patch("bozupy.kintone.record.dxo.to_record", return_value=None)
    assert len(list(sut.get_records(1, None, DUMMY_ACCESS_DATA))) == 0


@responses.activate
def test_add_record() -> None:
    set_mock_response("POST", "/k/v1/record.json", 200, {"id": "1"}, req_json={"app": 1, "record": {}}, auth=AuthMode.API_TOKEN)
    assert sut.add_record(KintoneRecord(app_id=1), DUMMY_ACCESS_DATA) == 1


def test_add_record_cannot_set_record_id() -> None:
    with pytest.raises(ValueError):
        sut.add_record(KintoneRecord(app_id=1, id=1), DUMMY_ACCESS_DATA)


@responses.activate
def test_add_record_raw() -> None:
    set_mock_response("POST", "/k/v1/record.json", 200, {"id": "1"}, req_json={"app": 1, "record": {}}, auth=AuthMode.API_TOKEN)
    assert sut.add_record_raw(1, {}, DUMMY_ACCESS_DATA) == 1


@responses.activate
def test_add_records() -> None:
    set_mock_response("POST", "/k/v1/records.json", 200, {"ids": ["1"]}, req_json={"app": 1, "records": [{}]}, auth=AuthMode.API_TOKEN)
    assert sut.add_records([KintoneRecord(app_id=1)], DUMMY_ACCESS_DATA) == [1]


def test_add_records_cannot_set_record_id() -> None:
    with pytest.raises(ValueError):
        sut.add_records([KintoneRecord(app_id=1), KintoneRecord(app_id=1, id=1)], DUMMY_ACCESS_DATA)


def test_add_records_app_id_must_be_same() -> None:
    with pytest.raises(ValueError):
        sut.add_records([KintoneRecord(app_id=1), KintoneRecord(app_id=2)], DUMMY_ACCESS_DATA)


@responses.activate
def test_add_records_raw() -> None:
    set_mock_response("POST", "/k/v1/records.json", 200, {"ids": ["1"]}, req_json={"app": 1, "records": [{}]}, auth=AuthMode.API_TOKEN)
    assert sut.add_records_raw(1, [{}], DUMMY_ACCESS_DATA) == [1]


@responses.activate(registry=OrderedRegistry)
def test_add_records_raw_offset() -> None:
    set_mock_response("POST", "/k/v1/records.json", 200, {"ids": [str(i) for i in range(100)]}, req_json={"app": 1, "records": [{} for _ in range(100)]}, auth=AuthMode.API_TOKEN)
    set_mock_response("POST", "/k/v1/records.json", 200, {"ids": ["100"]}, req_json={"app": 1, "records": [{}]}, auth=AuthMode.API_TOKEN)
    assert sut.add_records_raw(1, [{} for _ in range(101)], DUMMY_ACCESS_DATA) == list(range(101))


@responses.activate
def test_update_record() -> None:
    set_mock_response("PUT", "/k/v1/record.json", 200, {}, req_json={"app": 1, "id": 1, "record": {}}, auth=AuthMode.API_TOKEN)
    sut.update_record(KintoneRecord(app_id=1, id=1), DUMMY_ACCESS_DATA)


def test_update_record_record_id_is_required() -> None:
    with pytest.raises(ValueError):
        sut.update_record(KintoneRecord(app_id=1), DUMMY_ACCESS_DATA)


@responses.activate
def test_update_record_raw() -> None:
    set_mock_response("PUT", "/k/v1/record.json", 200, {}, req_json={"app": 1, "id": 1, "record": {}}, auth=AuthMode.API_TOKEN)
    sut.update_record_raw(1, 1, {}, DUMMY_ACCESS_DATA)


@responses.activate
def test_update_records() -> None:
    set_mock_response("PUT", "/k/v1/records.json", 200, {}, req_json={"app": 1, "records": [{"id": 1, "record": {}}]}, auth=AuthMode.API_TOKEN)
    sut.update_records([KintoneRecord(app_id=1, id=1)], DUMMY_ACCESS_DATA)


def test_update_records_record_id_is_required() -> None:
    with pytest.raises(ValueError):
        sut.update_records([KintoneRecord(app_id=1, id=1), KintoneRecord(app_id=1)], DUMMY_ACCESS_DATA)


def test_update_records_app_id_must_be_same() -> None:
    with pytest.raises(ValueError):
        sut.update_records([KintoneRecord(app_id=1, id=1), KintoneRecord(app_id=2, id=2)], DUMMY_ACCESS_DATA)


def test_update_records_record_id_is_not_duplicate() -> None:
    with pytest.raises(ValueError):
        sut.update_records([KintoneRecord(app_id=1, id=1), KintoneRecord(app_id=1, id=1)], DUMMY_ACCESS_DATA)


@responses.activate
def test_update_records_raw() -> None:
    set_mock_response("PUT", "/k/v1/records.json", 200, {}, req_json={"app": 1, "records": [{"id": 1, "record": {}}]}, auth=AuthMode.API_TOKEN)
    sut.update_records_raw(1, [(1, {})], DUMMY_ACCESS_DATA)


@responses.activate(registry=OrderedRegistry)
def test_update_records_raw_offset() -> None:
    set_mock_response("PUT", "/k/v1/records.json", 200, {}, req_json={"app": 1, "records": [{"id": i, "record": {}} for i in range(100)]}, auth=AuthMode.API_TOKEN)
    set_mock_response("PUT", "/k/v1/records.json", 200, {}, req_json={"app": 1, "records": [{"id": 100, "record": {}}]}, auth=AuthMode.API_TOKEN)
    sut.update_records_raw(1, [(i, {}) for i in range(101)], DUMMY_ACCESS_DATA)


def test_upsert_record_add(mocker: MockFixture) -> None:
    mocker.patch("bozupy.kintone.record.client.get_records_by_offset", return_value=[])
    mocker.patch("bozupy.kintone.record.client.add_record", return_value=1)
    mocker.patch("bozupy.kintone.record.client.update_record", side_effect=Exception)
    assert sut.upsert_record(KintoneRecord(app_id=1), "key", "value", DUMMY_ACCESS_DATA) == 1


def test_upsert_record_update(mocker: MockFixture) -> None:
    mocker.patch("bozupy.kintone.record.client.get_records_by_offset", return_value=[KintoneRecord(1, id=1)])
    mocker.patch("bozupy.kintone.record.client.add_record", side_effect=Exception)
    mocker.patch("bozupy.kintone.record.client.update_record", return_value=1)
    assert sut.upsert_record(KintoneRecord(app_id=1), "key", "value", DUMMY_ACCESS_DATA) == 1


@responses.activate
def test_upsert_records() -> None:
    set_mock_response("PUT", "/k/v1/records.json", 200, {}, req_json={"app": 1, "upsert": True, "records": [{"updateKey": "hoge", "record": {"hoge": {"value": "huga"}}}]}, auth=AuthMode.API_TOKEN)
    record: KintoneRecord = KintoneRecord(app_id=1)
    record.set_field(KintoneRecordSingleLineTextField("hoge", "huga"))
    sut.upsert_records([record], "hoge", DUMMY_ACCESS_DATA)


def test_upsert_records_update_key_field_is_required() -> None:
    record: KintoneRecord = KintoneRecord(app_id=1)
    record.set_field(KintoneRecordSingleLineTextField("hoge", "huga"))
    with pytest.raises(ValueError):
        sut.upsert_records([KintoneRecord(app_id=1, id=1)], "aaa", DUMMY_ACCESS_DATA)


def test_upsert_record_cannot_set_record_id() -> None:
    with pytest.raises(ValueError):
        sut.upsert_record(KintoneRecord(app_id=1, id=1), "key", "value", DUMMY_ACCESS_DATA)


def test_upsert_record_update_error(mocker: MockFixture) -> None:
    mocker.patch("bozupy.kintone.record.client.get_records_by_offset", return_value=[{}, {}])
    mocker.patch("bozupy.kintone.record.client.add_record", side_effect=Exception)
    mocker.patch("bozupy.kintone.record.client.update_record", return_value=1)
    with pytest.raises(RuntimeError):
        sut.upsert_record(KintoneRecord(app_id=1), "key", "value", DUMMY_ACCESS_DATA)


@responses.activate
def test_delete_records() -> None:
    set_mock_response("DELETE", "/k/v1/records.json", 200, {}, req_json={"app": 1, "ids": [1]}, auth=AuthMode.API_TOKEN)
    sut.delete_records(1, {1}, DUMMY_ACCESS_DATA)


@responses.activate(registry=OrderedRegistry)
def test_delete_records_offset() -> None:
    set_mock_response("DELETE", "/k/v1/records.json", 200, {}, req_json={"app": 1, "ids": list(range(100))}, auth=AuthMode.API_TOKEN)
    set_mock_response("DELETE", "/k/v1/records.json", 200, {}, req_json={"app": 1, "ids": [100]}, auth=AuthMode.API_TOKEN)
    sut.delete_records(1, set(range(101)), DUMMY_ACCESS_DATA)


@responses.activate
def test_upload_file() -> None:
    set_mock_response("POST", "/k/v1/file.json", 200, {"fileKey": "dummy"}, auth=AuthMode.API_TOKEN)
    with TemporaryDirectory() as td:
        temp_file: Path = Path(td) / "test.txt"
        temp_file.touch()
        assert sut.upload_file(1, "dummy", temp_file, "dummy", DUMMY_ACCESS_DATA) == "dummy"


@responses.activate
def test_download_file() -> None:
    set_mock_response("GET", "/k/v1/file.json", 200, res_body="", auth=AuthMode.API_TOKEN)
    with TemporaryDirectory() as td:
        temp_file: Path = Path(td) / "test.txt"
        sut.download_file("dummy", temp_file, 1, DUMMY_ACCESS_DATA)


@responses.activate
def test_update_record_assignees() -> None:
    set_mock_response(
        "PUT",
        "/k/v1/record/assignees.json",
        200,
        {"revision": 2},
        req_json={"app": 1, "id": 1, "assignees": ["hoge"]},
        auth=AuthMode.API_TOKEN)
    sut.update_record_assignees(1, 1, {"hoge"}, DUMMY_ACCESS_DATA)


@responses.activate
def test_update_record_status() -> None:
    set_mock_response(
        "PUT",
        "/k/v1/record/status.json",
        200,
        {"revision": 2},
        req_json={"app": 1, "id": 1, "assignee": "hoge", "action": "action"},
        auth=AuthMode.API_TOKEN)
    sut.update_record_status(1, 1, "action", "hoge", DUMMY_ACCESS_DATA)


@responses.activate
def test_update_record_status_no_assignee() -> None:
    set_mock_response(
        "PUT",
        "/k/v1/record/status.json",
        200,
        {"revision": 2},
        req_json={"app": 1, "id": 1, "action": "action"},
        auth=AuthMode.API_TOKEN)
    sut.update_record_status(1, 1, "action", access_data=DUMMY_ACCESS_DATA)

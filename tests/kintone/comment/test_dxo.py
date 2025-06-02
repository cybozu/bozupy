import pytest

from bozupy.kintone.comment.dto import KintoneRecordComment

from ...testtool import load, DUMMY_ACCESS_DATA

from bozupy.kintone.comment import dxo as sut


@pytest.mark.parametrize(["filename"], [
    ["record-comment.json"],
])
def test_to_record_comment(filename: str) -> None:
    actual: KintoneRecordComment = sut.to_record_comment(load(filename), 1, 1, DUMMY_ACCESS_DATA.subdomain, DUMMY_ACCESS_DATA.is_dev)
    assert actual is not None
    assert actual.id is not None
    assert actual.app_id == 1
    assert actual.record_id == 1
    assert actual.like_count == 0
    assert actual.like_codes == set([])

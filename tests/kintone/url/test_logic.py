from typing import Type

import pytest

from bozupy.kintone.url.dto import KintoneUrl, KintoneSpaceUrl, KintoneThreadUrl, KintonePeopleUrl, KintoneMessageUrl, \
    KintoneThreadCommentUrl, KintoneThreadChildCommentUrl, KintonePeopleChildCommentUrl, KintonePeopleCommentUrl, \
    KintoneMessageCommentUrl, KintoneAppUrl, KintoneRecordUrl, KintoneRecordCommentUrl

from bozupy.kintone.url import logic as sut


@pytest.mark.parametrize(["input_", "expected_class"], [
    ["https://test.cybozu.com/k/#/space/1", KintoneSpaceUrl],
    ["https://test.cybozu.com/k/#/space/1/thread/2", KintoneThreadUrl],
    ["https://test.cybozu.com/k/#/people/user/test", KintonePeopleUrl],
    ["https://test.cybozu.com/k/#/message/1;2", KintoneMessageUrl],
    ["https://test.cybozu.com/k/#/space/1/thread/2/3", KintoneThreadCommentUrl],
    ["https://test.cybozu.com/k/#/space/1/thread/2/3/4", KintoneThreadChildCommentUrl],
    ["https://test.cybozu.com/k/#/people/user/test/1", KintonePeopleCommentUrl],
    ["https://test.cybozu.com/k/#/people/user/test/1/2", KintonePeopleChildCommentUrl],
    ["https://test.cybozu.com/k/#/message/1;2/3", KintoneMessageCommentUrl],
    ["https://test.cybozu.com/k/1/", KintoneAppUrl],
    ["https://test.cybozu.com/k/1/show#record=2", KintoneRecordUrl],
    ["https://test.cybozu.com/k/1/show#record=2&comment=3", KintoneRecordCommentUrl]
])
def test_parse_kintone_url(input_: str, expected_class: Type[KintoneUrl]) -> None:
    actual: KintoneUrl | None = sut.parse_kintone_url(input_)
    assert actual is not None
    assert isinstance(actual, expected_class)
    assert actual.url() == input_

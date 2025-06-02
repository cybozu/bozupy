from dataclasses import dataclass
from datetime import datetime

import responses
from pytest_mock import MockFixture

from bozupy import CybozuDotComUrl
from bozupy.kintone.comment import client as sut
from bozupy.kintone.comment.dto import KintoneRecordComment, KintoneComment
from ...testtool import set_mock_response, DUMMY_ACCESS_DATA, AuthMode


@responses.activate
def test_get_record_comments(mocker: MockFixture) -> None:
    mocker.patch(
        "bozupy.kintone.comment.dxo.to_record_comment",
        return_value=_create_dummy_comment(1)
    )
    set_mock_response("GET", "/k/v1/record/comments.json", 200, {
        "comments": [{}]
    }, req_params={
        "app": 1,
        "record": 1,
        "limit": 10,
        "offset": 0
    }, auth=AuthMode.API_TOKEN)
    actual: list[KintoneRecordComment] = sut.get_record_comments(1, 1, DUMMY_ACCESS_DATA)
    assert len(actual) == 1
    assert actual[0].id == 1


@responses.activate
def test_post_record_comment() -> None:
    set_mock_response("POST", "/k/v1/record/comment.json", 200, {"id": 1}, auth=AuthMode.API_TOKEN)
    assert sut.post_record_comment(1, 1, "", {"test"}, DUMMY_ACCESS_DATA) == 1


@responses.activate
def test_post_thread_comment() -> None:
    set_mock_response(
        "POST",
        "/k/v1/space/thread/comment.json",
        200,
        res_json={"id": 3},
        req_json={
            "space": 1,
            "thread": 2,
            "comment": {
                "text": "comment",
                "mentions": [
                    {"code": "user", "type": "USER"},
                    {"code": "group", "type": "GROUP"},
                    {"code": "org", "type": "ORGANIZATION"},
                ]
            },
            "files": [
                {"fileKey": "file_key"}
            ]
        },
        auth=AuthMode.PASSWORD
    )
    assert sut.post_thread_comment(
        space_id=1,
        thread_id=2,
        comment="comment",
        mention_codes={"user"},
        mention_group_codes={"group"},
        mention_org_codes={"org"},
        file_keys={"file_key"},
        access_data=DUMMY_ACCESS_DATA) == 3


@dataclass
class _DummyComment(KintoneComment):
    @property
    def url(self) -> CybozuDotComUrl:
        raise NotImplementedError()


def _create_dummy_comment(id_: int) -> _DummyComment:
    return _DummyComment(
        id=id_,
        text="test",
        commented_at=datetime.now(),
        like_count=1,
        like_codes=set([]),
        creator_code="test",
        mention_codes=set([]),
        mention_org_codes=set([]),
        mention_group_codes=set([]),
        subdomain="test",
        is_dev=False
    )

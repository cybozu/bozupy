from datetime import datetime
from typing import Type

import pytest

from bozupy.kintone.search import dxo as sut
from bozupy.kintone.search.constant import KintoneSearchTypes, KintoneSearchOperators, KintoneSearchScopes, \
    KintoneSearchSortKeys, KintoneSearchSortOrders
from bozupy.kintone.search.dto import KintoneSearchCondition, KintoneSearchScope, KintoneSearchResult, \
    KintoneAttachmentSearchResult, KintoneSpaceSearchResult, KintoneSpaceAttachmentSearchResult, \
    KintoneThreadSearchResult, KintoneThreadAttachmentSearchResult, KintoneThreadCommentSearchResult, \
    KintoneThreadCommentAttachmentSearchResult, KintoneRecordSearchResult, KintoneRecordAttachmentSearchResult, \
    KintoneRecordCommentSearchResult, KintonePeopleCommentSearchResult, \
    KintonePeopleCommentAttachmentSearchResult

from ...testtool import load, DUMMY_ACCESS_DATA


@pytest.mark.parametrize(["filename", "expected_type"], [
    ["record.json", KintoneRecordSearchResult],
    ["record-attachment.json", KintoneRecordAttachmentSearchResult],
    ["record-comment.json", KintoneRecordCommentSearchResult],
    ["space.json", KintoneSpaceSearchResult],
    ["space-attachment.json", KintoneSpaceAttachmentSearchResult],
    ["thread.json", KintoneThreadSearchResult],
    ["thread-attachment.json", KintoneThreadAttachmentSearchResult],
    ["thread-comment.json", KintoneThreadCommentSearchResult],
    ["thread-comment-reply.json", KintoneThreadCommentSearchResult],
    ["thread-comment-attachment.json", KintoneThreadCommentAttachmentSearchResult],
    ["people-comment.json", KintonePeopleCommentSearchResult],
    ["people-comment-reply.json", KintonePeopleCommentSearchResult],
    ["people-comment-attachment.json", KintonePeopleCommentAttachmentSearchResult],
])
def test_to_search_result(filename: str, expected_type: Type[KintoneSearchResult]) -> None:
    hit: dict = load(filename)
    actual: KintoneSearchResult | None = sut.to_search_result(hit, DUMMY_ACCESS_DATA.subdomain, DUMMY_ACCESS_DATA.is_dev)
    assert actual is not None
    assert type(actual) is expected_type
    assert actual.raw_url == hit["url"]
    assert actual.snippets == hit["snippets"]
    assert actual.text == "\n".join(hit["snippets"])
    assert actual.creator_code
    assert actual.creator_name
    assert actual.is_attachment == isinstance(actual, KintoneAttachmentSearchResult)
    assert actual.is_attachment == (hit["type"] == KintoneSearchTypes.ATTACHMENT.value)
    # 組み立てたURLはレスポンスのURLと一致する
    assert str(actual.url) == hit["url"]


def test_to_search_result_record() -> None:
    actual: KintoneSearchResult | None = sut.to_search_result(load("record.json"), DUMMY_ACCESS_DATA.subdomain, DUMMY_ACCESS_DATA.is_dev)
    assert isinstance(actual, KintoneRecordSearchResult)
    assert actual.app_id == 760
    assert actual.app_name == "活動報告"
    assert actual.record_id == 12787
    assert actual.record_title == "顧客対応の効率化に向けて"
    assert actual.space_id == 18
    assert actual.space_name == "営業本部"
    assert actual.creator_code == "user1"
    assert actual.creator_name == "ユーザー1"
    # UTCで返ってくるのでJSTに変換される
    assert actual.created_at == datetime(2024, 3, 28, 18, 13, 0)
    assert len(actual.matched_fields) == 1
    assert actual.matched_fields[0].code == "summary"
    assert actual.matched_fields[0].label == "概要"


def test_to_search_result_record_attachment() -> None:
    actual: KintoneSearchResult | None = sut.to_search_result(load("record-attachment.json"), DUMMY_ACCESS_DATA.subdomain, DUMMY_ACCESS_DATA.is_dev)
    assert isinstance(actual, KintoneRecordAttachmentSearchResult)
    assert actual.record_id == 12787
    assert actual.matched_fields == []
    assert actual.file_key == "20250804065242B76047BB21494FE5BD4FA54590A50984300"
    assert actual.file_name == "予算管理表_2025年度.xlsx"
    assert actual.file_created_at == datetime(2025, 8, 4, 15, 53, 0)
    assert actual.file_creator_code == "user2"
    assert actual.file_creator_name == "ユーザー2"
    # 添付ファイル自身のURLはわからないので添付先のURLになる
    assert str(actual.url) == "https://test.cybozu.com/k/760/show#record=12787"


@pytest.mark.parametrize(["filename", "expected_type"], [
    ["record-no-permission.json", KintoneRecordSearchResult],
    ["record-attachment-no-permission.json", KintoneRecordAttachmentSearchResult],
])
def test_to_search_result_作成日時と作成者の閲覧権限がない場合(filename: str, expected_type: Type[KintoneRecordSearchResult]) -> None:
    hit: dict = load(filename)
    actual: KintoneSearchResult | None = sut.to_search_result(hit, DUMMY_ACCESS_DATA.subdomain, DUMMY_ACCESS_DATA.is_dev)
    assert type(actual) is expected_type
    assert isinstance(actual, KintoneRecordSearchResult)
    assert actual.record_id == 12787
    assert actual.created_at is None
    assert actual.creator_code is None
    assert actual.creator_name is None
    if isinstance(actual, KintoneRecordAttachmentSearchResult):
        assert actual.file_key == "20250804065242B76047BB21494FE5BD4FA54590A50984300"
        assert actual.file_created_at is None
        assert actual.file_creator_code is None
        assert actual.file_creator_name is None
    assert str(actual.url) == hit["url"]


def test_to_search_result_record_comment_without_space() -> None:
    actual: KintoneSearchResult | None = sut.to_search_result(load("record-comment.json"), DUMMY_ACCESS_DATA.subdomain, DUMMY_ACCESS_DATA.is_dev)
    assert isinstance(actual, KintoneRecordCommentSearchResult)
    assert actual.comment_id == 5
    assert actual.space_id is None
    assert actual.space_name is None


@pytest.mark.parametrize(["filename", "expected_reply_id"], [
    ["thread-comment.json", None],
    ["thread-comment-reply.json", 5678],
])
def test_to_search_result_thread_comment(filename: str, expected_reply_id: int | None) -> None:
    actual: KintoneSearchResult | None = sut.to_search_result(load(filename), DUMMY_ACCESS_DATA.subdomain, DUMMY_ACCESS_DATA.is_dev)
    assert isinstance(actual, KintoneThreadCommentSearchResult)
    assert actual.space_id == 18
    assert actual.space_name == "営業本部"
    assert actual.thread_id == 34
    assert actual.thread_name == "提案資料の整備"
    assert actual.comment_id == 1234
    assert actual.reply_id == expected_reply_id


@pytest.mark.parametrize(["filename", "expected_reply_id"], [
    ["people-comment.json", None],
    ["people-comment-reply.json", 182425],
])
def test_to_search_result_people_comment(filename: str, expected_reply_id: int | None) -> None:
    actual: KintoneSearchResult | None = sut.to_search_result(load(filename), DUMMY_ACCESS_DATA.subdomain, DUMMY_ACCESS_DATA.is_dev)
    assert isinstance(actual, KintonePeopleCommentSearchResult)
    assert actual.owner_code == "user3"
    assert actual.owner_name == "ユーザー3"
    assert actual.comment_id == 347030
    assert actual.reply_id == expected_reply_id
    assert actual.creator_code == "user4"


@pytest.mark.parametrize(["filename"], [
    ["message-comment.json"],
    ["message-comment-attachment.json"],
])
def test_to_search_result_message_comment_is_skipped(filename: str) -> None:
    # メッセージはアクセス権の扱いが他と異なるため未対応
    assert sut.to_search_result(load(filename), DUMMY_ACCESS_DATA.subdomain, DUMMY_ACCESS_DATA.is_dev) is None


def test_to_search_result_snippets_are_plain_text() -> None:
    hit: dict = load("record.json")
    hit["snippets"] = ["\n  営業支援を目的として、<strong>提案資料</strong>のテンプレート ", "<em>abc</em>&amp;<em>def</em>"]
    actual: KintoneSearchResult | None = sut.to_search_result(hit, DUMMY_ACCESS_DATA.subdomain, DUMMY_ACCESS_DATA.is_dev)
    assert actual is not None
    assert actual.snippets == ["営業支援を目的として、提案資料のテンプレート", "abc&def"]
    assert actual.text == "営業支援を目的として、提案資料のテンプレート\nabc&def"


def test_to_search_result_unknown_type() -> None:
    assert sut.to_search_result(load("unknown.json"), DUMMY_ACCESS_DATA.subdomain, DUMMY_ACCESS_DATA.is_dev) is None


def test_to_request_body_minimum() -> None:
    assert sut.to_request_body([KintoneSearchCondition(KintoneSearchOperators.AND, ["abc", "def"])]) == {
        "query": [
            {"operator": "AND", "keywords": ["abc", "def"]}
        ],
        "sort": {"by": "RELEVANCE", "order": "DESC"}
    }


def test_to_request_body_full() -> None:
    assert sut.to_request_body(
        conditions=[
            KintoneSearchCondition(KintoneSearchOperators.AND, ["abc"]),
            KintoneSearchCondition(KintoneSearchOperators.NOT, ["def"])
        ],
        types={KintoneSearchTypes.RECORD, KintoneSearchTypes.ATTACHMENT},
        scopes=[KintoneSearchScope(KintoneSearchScopes.APP, ids={2, 1})],
        exclude_scopes=[KintoneSearchScope(KintoneSearchScopes.PEOPLE, codes={"user9"})],
        created_after=datetime(2026, 5, 1),
        created_before=datetime(2026, 5, 31, 23, 59, 59),
        creators={"user2", "user1"},
        sort_by=KintoneSearchSortKeys.CREATED_AT,
        sort_order=KintoneSearchSortOrders.ASC,
        include_synonyms=True,
        limit=10,
        page_token="token"
    ) == {
        "query": [
            {"operator": "AND", "keywords": ["abc"]},
            {"operator": "NOT", "keywords": ["def"]}
        ],
        "types": ["ATTACHMENT", "RECORD"],
        "scopes": [{"scope": "APP", "ids": [1, 2]}],
        "excludeScopes": [{"scope": "PEOPLE", "codes": ["user9"]}],
        "createdAfter": "2026-05-01T00:00:00+09:00",
        "createdBefore": "2026-05-31T23:59:59+09:00",
        "creators": ["user1", "user2"],
        "includeSynonyms": True,
        "sort": {"by": "CREATED_AT", "order": "ASC"},
        "limit": 10,
        "pageToken": "token"
    }

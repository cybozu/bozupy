from datetime import datetime

import pytest
import responses

from bozupy.kintone.search import client as sut
from bozupy.kintone.search.constant import KintoneSearchOperators, KintoneSearchSortKeys, KintoneSearchSortOrders, \
    KintoneSearchTypes
from bozupy.kintone.search.dto import KintoneSearchCondition, KintoneSearchResult, KintoneRecordSearchResult

from ...testtool import set_mock_response, DUMMY_ACCESS_DATA, AuthMode

_PATH: str = "/k/v1/search.json"


def _record_hit(record_id: int) -> dict:
    return {
        "type": "RECORD",
        "url": f"https://test.cybozu.com/k/1/show#record={record_id}",
        "snippets": ["snippet"],
        "record": {
            "appId": "1",
            "appName": "app",
            "recordId": str(record_id),
            "recordTitle": "title",
            "createdAt": "2024-03-28T09:13:00.000Z",
            "creator": {"code": "user1", "name": "ユーザー1"},
            "matchedFields": []
        }
    }


@responses.activate
def test_search_by_keywords() -> None:
    # 1ページ目
    set_mock_response(
        "POST",
        _PATH,
        200,
        res_json={"hits": [_record_hit(1)], "nextPageToken": "next"},
        req_json={
            "query": [{"operator": "AND", "keywords": ["abc", "def"]}],
            "sort": {"by": "RELEVANCE", "order": "DESC"},
            "limit": 20
        },
        strict=True,
        # 公式の検索APIはAPIトークン認証に対応していない
        auth=AuthMode.PASSWORD
    )
    # 2ページ目
    set_mock_response(
        "POST",
        _PATH,
        200,
        res_json={"hits": [_record_hit(2)], "nextPageToken": None},
        req_json={
            "query": [{"operator": "AND", "keywords": ["abc", "def"]}],
            "sort": {"by": "RELEVANCE", "order": "DESC"},
            "limit": 20,
            "pageToken": "next"
        },
        strict=True,
        auth=AuthMode.PASSWORD
    )
    actual: list[KintoneSearchResult] = [r for r in sut.search_by_keywords(["abc", "def"], access_data=DUMMY_ACCESS_DATA)]
    assert len(actual) == 2
    assert isinstance(actual[0], KintoneRecordSearchResult)
    assert actual[0].record_id == 1
    assert isinstance(actual[1], KintoneRecordSearchResult)
    assert actual[1].record_id == 2


@responses.activate
def test_search_with_all_options() -> None:
    set_mock_response(
        "POST",
        _PATH,
        200,
        res_json={"hits": [], "nextPageToken": None},
        req_json={
            "query": [
                {"operator": "AND", "keywords": ["abc"]},
                {"operator": "OR", "keywords": ["ghi", "jkl"]},
                {"operator": "NOT", "keywords": ["def"]}
            ],
            "types": ["RECORD"],
            "createdAfter": "2026-05-01T00:00:00+09:00",
            "createdBefore": "2026-05-31T23:59:59+09:00",
            "creators": ["user1"],
            "sort": {"by": "CREATED_AT", "order": "ASC"},
            "limit": 20
        },
        strict=True,
        auth=AuthMode.PASSWORD
    )
    assert [r for r in sut.search_by_keywords(
        keywords=["abc", " "],
        exclude_keywords=["def"],
        or_keywords=["ghi", "jkl"],
        types={KintoneSearchTypes.RECORD},
        created_after=datetime(2026, 5, 1),
        created_before=datetime(2026, 5, 31, 23, 59, 59),
        creators={"user1"},
        sort_by=KintoneSearchSortKeys.CREATED_AT,
        sort_order=KintoneSearchSortOrders.ASC,
        access_data=DUMMY_ACCESS_DATA
    )] == []


@responses.activate
def test_search_by_page_token() -> None:
    set_mock_response(
        "POST",
        _PATH,
        200,
        res_json={"hits": [_record_hit(1)], "nextPageToken": "next"},
        req_json={"limit": 5, "pageToken": "current"},
        auth=AuthMode.PASSWORD
    )
    results: list[KintoneSearchResult]
    next_page_token: str | None
    results, next_page_token = sut.search_by_page_token(
        conditions=[KintoneSearchCondition(KintoneSearchOperators.AND, ["abc"])],
        page_token="current",
        limit=5,
        access_data=DUMMY_ACCESS_DATA
    )
    assert len(results) == 1
    assert next_page_token == "next"


@responses.activate
def test_search_by_page_token_without_next_page_token() -> None:
    set_mock_response("POST", _PATH, 200, res_json={"hits": [], "nextPageToken": None}, auth=AuthMode.PASSWORD)
    results: list[KintoneSearchResult]
    next_page_token: str | None
    results, next_page_token = sut.search_by_page_token(
        conditions=[KintoneSearchCondition(KintoneSearchOperators.AND, ["abc"])],
        access_data=DUMMY_ACCESS_DATA
    )
    assert results == []
    assert next_page_token is None


@responses.activate
def test_search_by_keywords_with_limit() -> None:
    set_mock_response(
        "POST",
        _PATH,
        200,
        res_json={"hits": [_record_hit(1), _record_hit(2)], "nextPageToken": "next"},
        auth=AuthMode.PASSWORD
    )
    actual: list[KintoneSearchResult] = sut.search_by_keywords_with_limit(["abc"], 2, access_data=DUMMY_ACCESS_DATA)
    # nextPageTokenがあっても指定件数で打ち切る
    assert len(actual) == 2


@responses.activate
def test_search_skips_unconvertible_hits() -> None:
    set_mock_response(
        "POST",
        _PATH,
        200,
        res_json={
            "hits": [
                # 未知の種類
                {"type": "SOMETHING_NEW", "url": "https://test.cybozu.com/k/", "snippets": []},
                # 変換に失敗する
                {"type": "RECORD", "url": "https://test.cybozu.com/k/", "snippets": [], "record": {}},
                _record_hit(1)
            ],
            "nextPageToken": None
        },
        auth=AuthMode.PASSWORD
    )
    actual: list[KintoneSearchResult] = [r for r in sut.search_by_keywords(["abc"], access_data=DUMMY_ACCESS_DATA)]
    assert len(actual) == 1
    assert isinstance(actual[0], KintoneRecordSearchResult)
    assert actual[0].record_id == 1


@pytest.mark.parametrize(["keywords", "exclude_keywords", "or_keywords"], [
    # 検索条件なし
    [[], None, None],
    [[""], None, None],
    # NOTだけでは検索結果が必ず空になる
    [[], ["abc"], None],
    # 検索語が20個を超える
    [[str(i) for i in range(11)], [str(i) for i in range(10)], None],
])
def test_search_invalid_keywords(keywords: list[str], exclude_keywords: list[str] | None, or_keywords: list[str] | None) -> None:
    with pytest.raises(ValueError):
        [r for r in sut.search_by_keywords(keywords, exclude_keywords, or_keywords, access_data=DUMMY_ACCESS_DATA)]


def test_search_invalid_created_range() -> None:
    with pytest.raises(ValueError):
        [r for r in sut.search_by_keywords(
            ["abc"],
            created_after=datetime(2026, 5, 31),
            created_before=datetime(2026, 5, 1),
            access_data=DUMMY_ACCESS_DATA
        )]


def test_search_invalid_sort() -> None:
    with pytest.raises(ValueError):
        [r for r in sut.search_by_keywords(
            ["abc"],
            sort_by=KintoneSearchSortKeys.RELEVANCE,
            sort_order=KintoneSearchSortOrders.ASC,
            access_data=DUMMY_ACCESS_DATA
        )]


def test_search_too_many_creators() -> None:
    with pytest.raises(ValueError):
        [r for r in sut.search_by_keywords(["abc"], creators={f"user{i}" for i in range(21)}, access_data=DUMMY_ACCESS_DATA)]


@pytest.mark.parametrize(["limit"], [[0], [21]])
def test_search_by_page_token_invalid_limit(limit: int) -> None:
    with pytest.raises(ValueError):
        sut.search_by_page_token(
            conditions=[KintoneSearchCondition(KintoneSearchOperators.AND, ["abc"])],
            limit=limit,
            access_data=DUMMY_ACCESS_DATA
        )


def test_search_by_keywords_with_limit_invalid_limit() -> None:
    with pytest.raises(ValueError):
        sut.search_by_keywords_with_limit(["abc"], 0, access_data=DUMMY_ACCESS_DATA)


def test_search_by_conditions_too_many_conditions() -> None:
    with pytest.raises(ValueError):
        [r for r in sut.search_by_conditions(
            [KintoneSearchCondition(KintoneSearchOperators.AND, ["abc"]) for _ in range(21)],
            access_data=DUMMY_ACCESS_DATA
        )]

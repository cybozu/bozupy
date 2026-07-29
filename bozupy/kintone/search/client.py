from __future__ import annotations

import logging
from datetime import datetime
from typing import Iterator

from . import dxo
from .constant import KintoneSearchTypes, KintoneSearchOperators, KintoneSearchSortKeys, KintoneSearchSortOrders
from .dto import KintoneSearchCondition, KintoneSearchScope, KintoneSearchResult
from ..util import post
from ...cybozu.dto import AccessData

_MAX_LIMIT: int = 20
_MAX_CONDITION_COUNT: int = 20
_MAX_KEYWORD_COUNT: int = 20
_MAX_SCOPE_COUNT: int = 20
_MAX_CREATOR_COUNT: int = 20


def search_by_keywords(keywords: list[str],
                       exclude_keywords: list[str] | None = None,
                       or_keywords: list[str] | None = None,
                       types: set[KintoneSearchTypes] | None = None,
                       scopes: list[KintoneSearchScope] | None = None,
                       exclude_scopes: list[KintoneSearchScope] | None = None,
                       created_after: datetime | None = None,
                       created_before: datetime | None = None,
                       creators: set[str] | None = None,
                       sort_by: KintoneSearchSortKeys = KintoneSearchSortKeys.RELEVANCE,
                       sort_order: KintoneSearchSortOrders = KintoneSearchSortOrders.DESC,
                       access_data: AccessData | None = None) -> Iterator[KintoneSearchResult]:
    logging.info("Search by Keywords")
    yield from search_by_conditions(
        conditions=_to_conditions(keywords, exclude_keywords, or_keywords),
        types=types,
        scopes=scopes,
        exclude_scopes=exclude_scopes,
        created_after=created_after,
        created_before=created_before,
        creators=creators,
        sort_by=sort_by,
        sort_order=sort_order,
        access_data=access_data
    )


def search_by_keywords_with_limit(keywords: list[str],
                                  limit: int,
                                  exclude_keywords: list[str] | None = None,
                                  or_keywords: list[str] | None = None,
                                  types: set[KintoneSearchTypes] | None = None,
                                  scopes: list[KintoneSearchScope] | None = None,
                                  exclude_scopes: list[KintoneSearchScope] | None = None,
                                  created_after: datetime | None = None,
                                  created_before: datetime | None = None,
                                  creators: set[str] | None = None,
                                  sort_by: KintoneSearchSortKeys = KintoneSearchSortKeys.RELEVANCE,
                                  sort_order: KintoneSearchSortOrders = KintoneSearchSortOrders.DESC,
                                  access_data: AccessData | None = None) -> list[KintoneSearchResult]:
    logging.info("Search by Keywords with Limit")
    if limit < 1:
        raise ValueError("limit must be greater than 0")
    results: list[KintoneSearchResult] = []
    for result in search_by_keywords(
        keywords=keywords,
        exclude_keywords=exclude_keywords,
        or_keywords=or_keywords,
        types=types,
        scopes=scopes,
        exclude_scopes=exclude_scopes,
        created_after=created_after,
        created_before=created_before,
        creators=creators,
        sort_by=sort_by,
        sort_order=sort_order,
        access_data=access_data
    ):
        results.append(result)
        if limit <= len(results):
            break
    return results


def search_by_conditions(conditions: list[KintoneSearchCondition],
                         types: set[KintoneSearchTypes] | None = None,
                         scopes: list[KintoneSearchScope] | None = None,
                         exclude_scopes: list[KintoneSearchScope] | None = None,
                         created_after: datetime | None = None,
                         created_before: datetime | None = None,
                         creators: set[str] | None = None,
                         sort_by: KintoneSearchSortKeys = KintoneSearchSortKeys.RELEVANCE,
                         sort_order: KintoneSearchSortOrders = KintoneSearchSortOrders.DESC,
                         access_data: AccessData | None = None) -> Iterator[KintoneSearchResult]:
    logging.info("Search by Conditions")
    page_token: str | None = None
    while True:
        results: list[KintoneSearchResult]
        results, page_token = search_by_page_token(
            conditions=conditions,
            page_token=page_token,
            types=types,
            scopes=scopes,
            exclude_scopes=exclude_scopes,
            created_after=created_after,
            created_before=created_before,
            creators=creators,
            sort_by=sort_by,
            sort_order=sort_order,
            access_data=access_data
        )
        yield from results
        if page_token is None:
            break


def search_by_page_token(conditions: list[KintoneSearchCondition],
                         page_token: str | None = None,
                         limit: int = _MAX_LIMIT,
                         types: set[KintoneSearchTypes] | None = None,
                         scopes: list[KintoneSearchScope] | None = None,
                         exclude_scopes: list[KintoneSearchScope] | None = None,
                         created_after: datetime | None = None,
                         created_before: datetime | None = None,
                         creators: set[str] | None = None,
                         sort_by: KintoneSearchSortKeys = KintoneSearchSortKeys.RELEVANCE,
                         sort_order: KintoneSearchSortOrders = KintoneSearchSortOrders.DESC,
                         access_data: AccessData | None = None) -> tuple[list[KintoneSearchResult], str | None]:
    logging.info("Search by Page Token")
    if access_data is None:
        access_data = AccessData()
    _validate(conditions, limit, scopes, exclude_scopes, created_after, created_before, creators, sort_by, sort_order)
    # 公式の検索APIはAPIトークン認証に対応していないので、app_idは渡さずパスワード認証を使う
    json_: dict = post(
        path="search",
        json_=dxo.to_request_body(
            conditions=conditions,
            types=types,
            scopes=scopes,
            exclude_scopes=exclude_scopes,
            created_after=created_after,
            created_before=created_before,
            creators=creators,
            sort_by=sort_by,
            sort_order=sort_order,
            limit=limit,
            page_token=page_token
        ),
        access_data=access_data
    )
    results: list[KintoneSearchResult] = []
    for hit in json_["hits"]:
        try:
            result: KintoneSearchResult | None = dxo.to_search_result(hit, access_data.subdomain, access_data.is_dev)
            if result is not None:
                results.append(result)
        except Exception as e:
            logging.error("Failed to convert search result", exc_info=e)
    return results, json_.get("nextPageToken") or None


def _to_conditions(keywords: list[str],
                   exclude_keywords: list[str] | None,
                   or_keywords: list[str] | None) -> list[KintoneSearchCondition]:
    conditions: list[KintoneSearchCondition] = []
    for operator, keywords_ in [
        (KintoneSearchOperators.AND, keywords),
        (KintoneSearchOperators.OR, or_keywords),
        (KintoneSearchOperators.NOT, exclude_keywords)
    ]:
        stripped_keywords: list[str] = [keyword.strip() for keyword in keywords_ or [] if keyword.strip()]
        if stripped_keywords:
            conditions.append(KintoneSearchCondition(operator=operator, keywords=stripped_keywords))
    return conditions


def _validate(conditions: list[KintoneSearchCondition],
              limit: int,
              scopes: list[KintoneSearchScope] | None,
              exclude_scopes: list[KintoneSearchScope] | None,
              created_after: datetime | None,
              created_before: datetime | None,
              creators: set[str] | None,
              sort_by: KintoneSearchSortKeys,
              sort_order: KintoneSearchSortOrders) -> None:
    if not conditions:
        raise ValueError("At least one condition must be provided")
    if len(conditions) > _MAX_CONDITION_COUNT:
        raise ValueError(f"Too many conditions: {len(conditions)} (max {_MAX_CONDITION_COUNT})")
    keyword_count: int = sum([len(condition.keywords) for condition in conditions])
    if keyword_count > _MAX_KEYWORD_COUNT:
        raise ValueError(f"Too many keywords: {keyword_count} (max {_MAX_KEYWORD_COUNT})")
    if not [c for c in conditions if c.operator in {KintoneSearchOperators.AND, KintoneSearchOperators.OR}]:
        # NOTだけの検索条件では検索結果が必ず空になる
        raise ValueError("At least one AND or OR condition must be provided")
    if limit < 1 or limit > _MAX_LIMIT:
        raise ValueError(f"limit must be between 1 and {_MAX_LIMIT}: {limit}")
    for scopes_ in [scopes, exclude_scopes]:
        if scopes_ is not None and len(scopes_) > _MAX_SCOPE_COUNT:
            raise ValueError(f"Too many scopes: {len(scopes_)} (max {_MAX_SCOPE_COUNT})")
    if created_after is not None and created_before is not None and created_after > created_before:
        raise ValueError("created_after must be older than or equal to created_before")
    if creators is not None and len(creators) > _MAX_CREATOR_COUNT:
        raise ValueError(f"Too many creators: {len(creators)} (max {_MAX_CREATOR_COUNT})")
    if sort_by == KintoneSearchSortKeys.RELEVANCE and sort_order == KintoneSearchSortOrders.ASC:
        raise ValueError("ASC cannot be specified when sort_by is RELEVANCE")

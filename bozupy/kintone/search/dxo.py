from __future__ import annotations

import logging
from datetime import datetime

from .constant import KintoneSearchTypes, KintoneSearchSortKeys, KintoneSearchSortOrders
from .dto import KintoneSearchCondition, KintoneSearchScope, KintoneSearchMatchedField, KintoneSearchResult, \
    KintoneSpaceSearchResult, KintoneSpaceAttachmentSearchResult, KintoneThreadSearchResult, \
    KintoneThreadAttachmentSearchResult, KintoneThreadCommentSearchResult, \
    KintoneThreadCommentAttachmentSearchResult, KintoneRecordSearchResult, KintoneRecordAttachmentSearchResult, \
    KintoneRecordCommentSearchResult, KintonePeopleCommentSearchResult, \
    KintonePeopleCommentAttachmentSearchResult
from ...util import kintone_str_to_datetime, datetime_to_kintone_str, get_int_optional, get_str_optional, html_to_text


def to_request_body(
        conditions: list[KintoneSearchCondition],
        types: set[KintoneSearchTypes] | None = None,
        scopes: list[KintoneSearchScope] | None = None,
        exclude_scopes: list[KintoneSearchScope] | None = None,
        created_after: datetime | None = None,
        created_before: datetime | None = None,
        creators: set[str] | None = None,
        sort_by: KintoneSearchSortKeys = KintoneSearchSortKeys.RELEVANCE,
        sort_order: KintoneSearchSortOrders = KintoneSearchSortOrders.DESC,
        limit: int | None = None,
        page_token: str | None = None) -> dict:
    body: dict = {
        "query": [
            {
                "operator": condition.operator.value,
                "keywords": condition.keywords
            }
            for condition in conditions
        ],
        "sort": {
            "by": sort_by.value,
            "order": sort_order.value
        }
    }
    if types:
        body["types"] = sorted([type_.value for type_ in types])
    if scopes:
        body["scopes"] = [_to_scope_dict(scope) for scope in scopes]
    if exclude_scopes:
        body["excludeScopes"] = [_to_scope_dict(scope) for scope in exclude_scopes]
    if created_after is not None:
        body["createdAfter"] = datetime_to_kintone_str(created_after)
    if created_before is not None:
        body["createdBefore"] = datetime_to_kintone_str(created_before)
    if creators:
        body["creators"] = sorted(creators)
    if limit is not None:
        body["limit"] = int(limit)
    if page_token is not None:
        body["pageToken"] = page_token
    return body


def _to_scope_dict(scope: KintoneSearchScope) -> dict:
    scope_dict: dict = {"scope": scope.scope.value}
    if scope.ids:
        scope_dict["ids"] = sorted([int(id_) for id_ in scope.ids])
    if scope.codes:
        scope_dict["codes"] = sorted(scope.codes)
    return scope_dict


def to_search_result(hit: dict, subdomain: str, is_dev: bool) -> KintoneSearchResult | None:
    type_str: str = hit["type"]
    is_attachment: bool = type_str == KintoneSearchTypes.ATTACHMENT.value
    if is_attachment:
        type_str = hit["attachment"]["attachedTo"]
    match type_str:
        case "RECORD":
            record: dict = hit["record"]
            record_kwargs: dict = {
                "app_id": int(record["appId"]),
                "app_name": record["appName"],
                "record_id": int(record["recordId"]),
                "record_title": record["recordTitle"],
                "space_id": get_int_optional(record, "spaceId"),
                "space_name": get_str_optional(record, "spaceName"),
                "matched_fields": [
                    KintoneSearchMatchedField(code=matched_field["code"], label=matched_field["label"])
                    for matched_field in record.get("matchedFields", [])
                ]
            }
            if is_attachment:
                return KintoneRecordAttachmentSearchResult(
                    **_to_base_kwargs(hit, record, subdomain, is_dev),
                    **_to_attachment_kwargs(hit),
                    **record_kwargs
                )
            return KintoneRecordSearchResult(
                **_to_base_kwargs(hit, record, subdomain, is_dev),
                **record_kwargs
            )
        case "RECORD_COMMENT":
            record_comment: dict = hit["recordComment"]
            return KintoneRecordCommentSearchResult(
                **_to_base_kwargs(hit, record_comment, subdomain, is_dev),
                app_id=int(record_comment["appId"]),
                app_name=record_comment["appName"],
                record_id=int(record_comment["recordId"]),
                record_title=record_comment["recordTitle"],
                space_id=get_int_optional(record_comment, "spaceId"),
                space_name=get_str_optional(record_comment, "spaceName"),
                comment_id=int(record_comment["commentId"])
            )
        case "SPACE":
            space: dict = hit["space"]
            space_kwargs: dict = {
                "space_id": int(space["spaceId"]),
                "space_name": space["spaceName"]
            }
            if is_attachment:
                return KintoneSpaceAttachmentSearchResult(
                    **_to_base_kwargs(hit, space, subdomain, is_dev),
                    **_to_attachment_kwargs(hit),
                    **space_kwargs
                )
            return KintoneSpaceSearchResult(
                **_to_base_kwargs(hit, space, subdomain, is_dev),
                **space_kwargs
            )
        case "THREAD":
            thread: dict = hit["thread"]
            thread_kwargs: dict = {
                "space_id": int(thread["spaceId"]),
                "space_name": thread["spaceName"],
                "thread_id": int(thread["threadId"]),
                "thread_name": thread["threadName"]
            }
            if is_attachment:
                return KintoneThreadAttachmentSearchResult(
                    **_to_base_kwargs(hit, thread, subdomain, is_dev),
                    **_to_attachment_kwargs(hit),
                    **thread_kwargs
                )
            return KintoneThreadSearchResult(
                **_to_base_kwargs(hit, thread, subdomain, is_dev),
                **thread_kwargs
            )
        case "THREAD_COMMENT":
            thread_comment: dict = hit["threadComment"]
            thread_comment_kwargs: dict = {
                "space_id": int(thread_comment["spaceId"]),
                "space_name": thread_comment["spaceName"],
                "thread_id": int(thread_comment["threadId"]),
                "thread_name": thread_comment["threadName"],
                "comment_id": int(thread_comment["commentId"]),
                "reply_id": get_int_optional(thread_comment, "replyId")
            }
            if is_attachment:
                return KintoneThreadCommentAttachmentSearchResult(
                    **_to_base_kwargs(hit, thread_comment, subdomain, is_dev),
                    **_to_attachment_kwargs(hit),
                    **thread_comment_kwargs
                )
            return KintoneThreadCommentSearchResult(
                **_to_base_kwargs(hit, thread_comment, subdomain, is_dev),
                **thread_comment_kwargs
            )
        case "PEOPLE_COMMENT":
            people_comment: dict = hit["peopleComment"]
            people_comment_kwargs: dict = {
                "owner_code": people_comment["owner"]["code"],
                "owner_name": people_comment["owner"]["name"],
                "comment_id": int(people_comment["commentId"]),
                "reply_id": get_int_optional(people_comment, "replyId")
            }
            if is_attachment:
                return KintonePeopleCommentAttachmentSearchResult(
                    **_to_base_kwargs(hit, people_comment, subdomain, is_dev),
                    **_to_attachment_kwargs(hit),
                    **people_comment_kwargs
                )
            return KintonePeopleCommentSearchResult(
                **_to_base_kwargs(hit, people_comment, subdomain, is_dev),
                **people_comment_kwargs
            )
        case "MESSAGE_COMMENT":
            logging.info("MESSAGE_COMMENT is not supported yet...")
            return None
        case _ as unknown_type:
            logging.warning(f"{unknown_type} is not implemented yet...")
            return None


def _to_base_kwargs(hit: dict, target: dict, subdomain: str, is_dev: bool) -> dict:
    return {
        "raw_url": hit["url"],
        "snippets": [html_to_text(f"<div>{snippet}</div>").strip() for snippet in hit.get("snippets", [])],
        "created_at": kintone_str_to_datetime(target["createdAt"]),
        "creator_code": target["creator"]["code"],
        "creator_name": target["creator"]["name"],
        "subdomain": subdomain,
        "is_dev": is_dev
    }


def _to_attachment_kwargs(hit: dict) -> dict:
    attachment: dict = hit["attachment"]
    return {
        "file_key": attachment["fileKey"],
        "file_name": attachment["name"],
        "file_created_at": kintone_str_to_datetime(attachment["createdAt"]),
        "file_creator_code": attachment["creator"]["code"],
        "file_creator_name": attachment["creator"]["name"]
    }

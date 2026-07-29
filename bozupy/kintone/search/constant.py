from __future__ import annotations
from enum import Enum


class KintoneSearchTypes(Enum):
    RECORD = "RECORD"
    RECORD_COMMENT = "RECORD_COMMENT"
    SPACE = "SPACE"
    THREAD = "THREAD"
    THREAD_COMMENT = "THREAD_COMMENT"
    PEOPLE_COMMENT = "PEOPLE_COMMENT"
    MESSAGE_COMMENT = "MESSAGE_COMMENT"
    ATTACHMENT = "ATTACHMENT"


class KintoneSearchOperators(Enum):
    AND = "AND"
    OR = "OR"
    NOT = "NOT"


class KintoneSearchScopes(Enum):
    APP = "APP"
    SPACE = "SPACE"
    PEOPLE = "PEOPLE"
    MESSAGE = "MESSAGE"


class KintoneSearchSortKeys(Enum):
    RELEVANCE = "RELEVANCE"
    CREATED_AT = "CREATED_AT"


class KintoneSearchSortOrders(Enum):
    ASC = "ASC"
    DESC = "DESC"

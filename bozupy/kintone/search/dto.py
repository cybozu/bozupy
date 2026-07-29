from __future__ import annotations

from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from datetime import datetime

from .constant import KintoneSearchOperators, KintoneSearchScopes
from ..url.dto import KintoneUrl, KintoneSpaceUrl, KintoneThreadUrl, KintoneThreadCommentUrl, \
    KintoneThreadChildCommentUrl, KintonePeopleCommentUrl, KintonePeopleChildCommentUrl, KintoneRecordUrl, \
    KintoneRecordCommentUrl

_MAX_KEYWORD_COUNT: int = 20
_MIN_KEYWORD_LENGTH: int = 1
_MAX_KEYWORD_LENGTH: int = 50
_MAX_SCOPE_VALUE_COUNT: int = 20


@dataclass
class KintoneSearchCondition:
    operator: KintoneSearchOperators
    keywords: list[str]

    def __post_init__(self) -> None:
        if not self.keywords:
            raise ValueError("At least one keyword must be provided")
        if len(self.keywords) > _MAX_KEYWORD_COUNT:
            raise ValueError(f"Too many keywords: {len(self.keywords)} (max {_MAX_KEYWORD_COUNT})")
        for keyword in self.keywords:
            if len(keyword) < _MIN_KEYWORD_LENGTH or len(keyword) > _MAX_KEYWORD_LENGTH:
                raise ValueError(f"Keyword length must be between {_MIN_KEYWORD_LENGTH} and {_MAX_KEYWORD_LENGTH}: {keyword}")


@dataclass
class KintoneSearchScope:
    scope: KintoneSearchScopes
    ids: set[int] | None = None
    codes: set[str] | None = None

    def __post_init__(self) -> None:
        if self.scope in {KintoneSearchScopes.APP, KintoneSearchScopes.SPACE}:
            if self.codes:
                raise ValueError(f"codes cannot be specified for {self.scope.value} scope")
        elif self.ids:
            raise ValueError(f"ids cannot be specified for {self.scope.value} scope")
        if self.ids is not None and len(self.ids) > _MAX_SCOPE_VALUE_COUNT:
            raise ValueError(f"Too many ids: {len(self.ids)} (max {_MAX_SCOPE_VALUE_COUNT})")
        if self.codes is not None and len(self.codes) > _MAX_SCOPE_VALUE_COUNT:
            raise ValueError(f"Too many codes: {len(self.codes)} (max {_MAX_SCOPE_VALUE_COUNT})")


@dataclass
class KintoneSearchMatchedField:
    code: str
    label: str


@dataclass
class KintoneSearchResult(metaclass=ABCMeta):
    raw_url: str
    snippets: list[str]
    created_at: datetime
    creator_code: str
    creator_name: str
    subdomain: str
    is_dev: bool

    @property
    def text(self) -> str:
        return "\n".join(self.snippets)

    @property
    def is_attachment(self) -> bool:
        return isinstance(self, KintoneAttachmentSearchResult)

    @property
    @abstractmethod
    def url(self) -> KintoneUrl:
        raise NotImplementedError()


@dataclass
class KintoneAttachmentSearchResult(KintoneSearchResult, metaclass=ABCMeta):
    file_key: str
    file_name: str
    file_created_at: datetime
    file_creator_code: str
    file_creator_name: str


@dataclass
class KintoneSpaceSearchResult(KintoneSearchResult):
    space_id: int
    space_name: str

    @property
    def url(self) -> KintoneSpaceUrl:
        return KintoneSpaceUrl(
            subdomain=self.subdomain,
            is_dev=self.is_dev,
            space_id=self.space_id
        )


@dataclass
class KintoneThreadSearchResult(KintoneSpaceSearchResult):
    thread_id: int
    thread_name: str

    @property
    def url(self) -> KintoneThreadUrl:
        return KintoneThreadUrl(
            subdomain=self.subdomain,
            is_dev=self.is_dev,
            space_id=self.space_id,
            thread_id=self.thread_id
        )


@dataclass
class KintoneThreadCommentSearchResult(KintoneThreadSearchResult):
    comment_id: int
    reply_id: int | None

    @property
    def url(self) -> KintoneThreadCommentUrl | KintoneThreadChildCommentUrl:
        if self.reply_id is None:
            return KintoneThreadCommentUrl(
                subdomain=self.subdomain,
                is_dev=self.is_dev,
                space_id=self.space_id,
                thread_id=self.thread_id,
                comment_id=self.comment_id
            )
        return KintoneThreadChildCommentUrl(
            subdomain=self.subdomain,
            is_dev=self.is_dev,
            space_id=self.space_id,
            thread_id=self.thread_id,
            comment_id=self.reply_id,
            parent_comment_id=self.comment_id
        )


@dataclass
class KintoneRecordRelatedSearchResult(KintoneSearchResult, metaclass=ABCMeta):
    app_id: int
    app_name: str
    record_id: int
    record_title: str
    space_id: int | None
    space_name: str | None


@dataclass
class KintoneRecordSearchResult(KintoneRecordRelatedSearchResult):
    matched_fields: list[KintoneSearchMatchedField]

    @property
    def url(self) -> KintoneRecordUrl:
        return KintoneRecordUrl(
            subdomain=self.subdomain,
            is_dev=self.is_dev,
            app_id=self.app_id,
            record_id=self.record_id
        )


@dataclass
class KintoneRecordCommentSearchResult(KintoneRecordRelatedSearchResult):
    comment_id: int

    @property
    def url(self) -> KintoneRecordCommentUrl:
        return KintoneRecordCommentUrl(
            subdomain=self.subdomain,
            is_dev=self.is_dev,
            app_id=self.app_id,
            record_id=self.record_id,
            comment_id=self.comment_id
        )


@dataclass
class KintonePeopleCommentSearchResult(KintoneSearchResult):
    owner_code: str
    owner_name: str
    comment_id: int
    reply_id: int | None

    @property
    def url(self) -> KintonePeopleCommentUrl | KintonePeopleChildCommentUrl:
        if self.reply_id is None:
            return KintonePeopleCommentUrl(
                subdomain=self.subdomain,
                is_dev=self.is_dev,
                user_code=self.owner_code,
                comment_id=self.comment_id
            )
        return KintonePeopleChildCommentUrl(
            subdomain=self.subdomain,
            is_dev=self.is_dev,
            user_code=self.owner_code,
            comment_id=self.reply_id,
            parent_comment_id=self.comment_id
        )


@dataclass
class KintoneSpaceAttachmentSearchResult(KintoneSpaceSearchResult, KintoneAttachmentSearchResult):
    pass


@dataclass
class KintoneThreadAttachmentSearchResult(KintoneThreadSearchResult, KintoneAttachmentSearchResult):
    pass


@dataclass
class KintoneThreadCommentAttachmentSearchResult(KintoneThreadCommentSearchResult, KintoneAttachmentSearchResult):
    pass


@dataclass
class KintoneRecordAttachmentSearchResult(KintoneRecordSearchResult, KintoneAttachmentSearchResult):
    pass


@dataclass
class KintonePeopleCommentAttachmentSearchResult(KintonePeopleCommentSearchResult, KintoneAttachmentSearchResult):
    pass

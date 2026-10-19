from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, time, date

from ..base.dto import GaroonComment
from ..constant import EventTypes
from ..url.dto import GaroonEventUrl


@dataclass
class Facility:
    code: str
    id: int
    name: str
    parent_id: int | None = None


@dataclass
class RepeatInfo:
    type: str
    start_time: time | None
    end_time: time | None
    period_start: date
    period_end: date
    day_of_week: int | None
    day_of_month: int | str | None


@dataclass
class GaroonEventBase:
    id: int
    subject: str
    creator_code: str
    event_type: EventTypes
    created_at: datetime
    attendee_codes: set[str]
    watcher_codes: set[str]
    facility_codes: set[str]
    note: str | None
    label: str | None


@dataclass
class GaroonEvent(GaroonEventBase):
    start: datetime
    end: datetime | None


@dataclass
class GaroonRepeatEvent(GaroonEventBase):
    repeat_info: RepeatInfo


@dataclass(order=True)
class GaroonEventComment(GaroonComment):
    event_id: int = field(compare=False)
    # 宛先に「予定の参加者全員」が指定されているか
    is_mention_all: bool = field(compare=False, default=False)

    @property
    def url(self) -> GaroonEventUrl:
        # コメント単位のURLはないので予定のURLを返す
        return GaroonEventUrl(
            subdomain=self.subdomain,
            is_dev=self.is_dev,
            event_id=self.event_id
        )

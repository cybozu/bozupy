from datetime import datetime, time, date

from .dto import GaroonEvent, Facility, RepeatInfo, GaroonEventBase, GaroonRepeatEvent
from ..constant import EventTypes
from ...util import str_to_datetime, str_to_time, str_to_date


def _day_of_week_to_int(day_of_week_str: str) -> int | None:
    mapping: dict[str, int] = {
        "MON": 1,
        "TUE": 2,
        "WED": 3,
        "THU": 4,
        "FRI": 5,
        "SAT": 6,
        "SUN": 0
    }
    return mapping.get(day_of_week_str.upper())


def to_event_base(event_json: dict) -> GaroonEventBase:
    event_type: EventTypes = EventTypes.from_str(event_json["eventType"])
    event_id: int = int(event_json["id"])
    subject: str = event_json["subject"]
    creator_code: str = event_json["creator"]["code"]
    created_at: datetime = str_to_datetime(event_json["createdAt"])
    attendee_codes: set[str] = set([attendee["code"] for attendee in event_json.get("attendees", [])])
    watcher_codes: set[str] = set([watcher["code"] for watcher in event_json.get("watchers", [])])
    facility_codes: set[str] = set([facility["code"] for facility in event_json.get("facilities", [])])
    note: str | None = event_json.get("note", None)
    label: str | None = event_json.get("label", None)
    return GaroonEventBase(
        id=event_id,
        subject=subject,
        creator_code=creator_code,
        event_type=event_type,
        created_at=created_at,
        attendee_codes=attendee_codes,
        watcher_codes=watcher_codes,
        facility_codes=facility_codes,
        note=note,
        label=label
    )


def to_repeat_event(event_json: dict) -> GaroonRepeatEvent:
    base_event: GaroonEventBase = to_event_base(event_json)
    repeat_info_json: dict = event_json["repeatInfo"]
    period_start: date = str_to_date(repeat_info_json["period"]["start"])
    period_end: date = str_to_date(repeat_info_json["period"]["end"])
    start_time: time | None = None
    end_time: time | None = None
    if "time" in repeat_info_json:
        if "start" in repeat_info_json["time"] and repeat_info_json["time"]["start"]:
            start_time = str_to_time(repeat_info_json["time"]["start"])
        if "end" in repeat_info_json["time"] and repeat_info_json["time"]["end"]:
            end_time = str_to_time(repeat_info_json["time"]["end"])
    return GaroonRepeatEvent(
        id=base_event.id,
        subject=base_event.subject,
        creator_code=base_event.creator_code,
        event_type=base_event.event_type,
        created_at=base_event.created_at,
        attendee_codes=base_event.attendee_codes,
        watcher_codes=base_event.watcher_codes,
        facility_codes=base_event.facility_codes,
        note=base_event.note,
        label=base_event.label,
        repeat_info=RepeatInfo(
            type=repeat_info_json["type"],
            start_time=start_time,
            end_time=end_time,
            period_start=period_start,
            period_end=period_end,
            day_of_week=_day_of_week_to_int(repeat_info_json.get("dayOfWeek", "")),
            day_of_month=repeat_info_json.get("dayOfMonth", None)
        )
    )


def to_normal_event(event_json: dict) -> GaroonEvent:
    base_event: GaroonEventBase = to_event_base(event_json)
    start: datetime = str_to_datetime(event_json["start"]["dateTime"])
    end: datetime | None = str_to_datetime(event_json["end"]["dateTime"]) if "end" in event_json and event_json["end"] else None
    return GaroonEvent(
        id=base_event.id,
        subject=base_event.subject,
        creator_code=base_event.creator_code,
        event_type=base_event.event_type,
        created_at=base_event.created_at,
        attendee_codes=base_event.attendee_codes,
        watcher_codes=base_event.watcher_codes,
        facility_codes=base_event.facility_codes,
        note=base_event.note,
        label=base_event.label,
        start=start,
        end=end
    )


def to_event(event_json: dict) -> GaroonEventBase:
    if "start" in event_json and "dateTime" in event_json["start"]:
        return to_normal_event(event_json)
    return to_repeat_event(event_json)


def to_facility(facility_json: dict) -> Facility:
    return Facility(
        code=facility_json["code"],
        id=int(facility_json["id"]),
        name=facility_json["name"],
        parent_id=int(facility_json["parentId"]) if "parentId" in facility_json else None
    )

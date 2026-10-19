from datetime import datetime
from typing import Type

import pytest

from bozupy.garoon.schedule import dxo as sut, GaroonEvent
from bozupy.garoon.schedule.dto import GaroonEventBase, GaroonRepeatEvent, GaroonEventComment
from ...testtool import load, DUMMY_ACCESS_DATA


@pytest.mark.parametrize(["filename", "expected_class"], [
    ["event.json", GaroonEvent],
    ["event_no_watchers.json", GaroonEvent],
    ["event-repeating.json", GaroonRepeatEvent]
])
def test_to_event(filename: str, expected_class: Type[GaroonEventBase]):
    event_json: dict = load(filename)
    actual: GaroonEventBase = sut.to_event(event_json)
    assert isinstance(actual, expected_class)
    assert actual.id
    assert actual.subject
    assert actual.creator_code
    assert actual.event_type
    assert actual.created_at


@pytest.mark.parametrize(["filename"], [
    ["facilities.json"]
])
def test_to_facility(filename: str):
    facility_json: dict = load(filename)["facilities"][0]
    actual = sut.to_facility(facility_json)
    assert actual.code
    assert actual.id
    assert actual.name


def test_to_event_comment() -> None:
    actual: GaroonEventComment = sut.to_event_comment(load("event-comment.json"), 123, DUMMY_ACCESS_DATA.subdomain, DUMMY_ACCESS_DATA.is_dev)
    assert actual.id == 2
    # HTMLエスケープされずに返ってくるのでそのまま保持する
    assert actual.text == "<b>明日</b>の会議資料を共有します。"
    # UTCで返ってくるのでJSTに変換される
    assert actual.commented_at == datetime(2024, 4, 19, 13, 46, 25)
    assert actual.creator_code == "user2"
    assert actual.like_count == 0
    assert actual.like_codes == set([])
    # 削除済みの宛先は含まれない
    assert actual.mention_codes == {"user3"}
    assert actual.mention_org_codes == {"org1"}
    assert actual.mention_group_codes == {"role1"}
    assert actual.is_mention_all is False
    assert actual.event_id == 123
    assert str(actual.url) == "https://test.cybozu.com/g/schedule/view.csp?event=123"


def test_to_event_comment_参加者全員が宛先で作成者が削除済みの場合() -> None:
    actual: GaroonEventComment = sut.to_event_comment(load("event-comment-mention-all.json"), 123, DUMMY_ACCESS_DATA.subdomain, DUMMY_ACCESS_DATA.is_dev)
    assert actual.is_mention_all is True
    assert actual.mention_codes == set([])
    assert actual.mention_org_codes == set([])
    assert actual.mention_group_codes == set([])
    assert actual.creator_code == ""

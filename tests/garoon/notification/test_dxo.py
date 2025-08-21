import pytest

from bozupy.garoon.notification.dto import GaroonNotification
from ...testtool import load, DUMMY_ACCESS_DATA

from bozupy.garoon.notification import dxo as sut


@pytest.mark.parametrize(["filename"], [
    ["notification.json"]
])
def test_to_garoon_notification(filename: str):
    for ntf_json in load(filename)["items"]:
        actual: GaroonNotification = sut.to_garoon_notification(ntf_json, DUMMY_ACCESS_DATA.subdomain, DUMMY_ACCESS_DATA.is_dev)
        assert actual.notify_at
        assert actual.user_code
        assert actual.text
        assert actual.link
        assert actual.module
        assert actual.creator_id
        assert actual.operation_type
        assert actual.body

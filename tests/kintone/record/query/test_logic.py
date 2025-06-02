from datetime import date, datetime

import pytest

from bozupy.kintone.record.query import logic as sut
from bozupy.kintone.record.dto import KintoneRecordSingleLineTextField, KintoneRecordCheckBoxField, \
    KintoneRecordNumberField, KintoneRecordUserSelectField, KintoneRecordDateField, KintoneRecordDateTimeField
from bozupy.kintone.record.query.dto import LoginUser, PrimaryOrg, Now, Today, Yesterday, Tomorrow, FromToday, ThisWeek, \
    LastWeek, NextWeek, ThisMonth, LastMonth, NextMonth, ThisYear, LastYear, NextYear


# noinspection SpellCheckingInspection
@pytest.mark.parametrize(["builder", "expected"], [
    [sut.KintoneQueryBuilder(), 'limit 500 offset 0'],
    [
        sut.KintoneQueryBuilder()
            .equal(  # noqa: E131
                "code",
                "value",
                KintoneRecordSingleLineTextField
            ),
        'code = "value" limit 500 offset 0'
    ],
    [
        sut.KintoneQueryBuilder()
            .equal(  # noqa: E131
                "code",
                "value",
                KintoneRecordSingleLineTextField,
                is_not=True
            ),
        'code != "value" limit 500 offset 0'
    ],
    [
        sut.KintoneQueryBuilder()
                         .equal(  # noqa: E131
            "code",
            None,
            KintoneRecordSingleLineTextField,
        ),
        'code = "" limit 500 offset 0'
    ],
    [
        sut.KintoneQueryBuilder()
                         .equal(  # noqa: E131
            "code",
            None,
            KintoneRecordNumberField,
        ),
        'code = "" limit 500 offset 0'
    ],
    [
        sut.KintoneQueryBuilder()
            .contain(  # noqa: E131
                "code",
                {"value"},
                KintoneRecordCheckBoxField
            ),
        'code in ("value") limit 500 offset 0'
    ],
    [
        sut.KintoneQueryBuilder()
            .contain(  # noqa: E131
                "code",
                {"value"},
                KintoneRecordCheckBoxField,
                is_not=True
            ),
        'code not in ("value") limit 500 offset 0'
    ],
    [
        sut.KintoneQueryBuilder()
            .greater_than(  # noqa: E131
                "code",
                1,
                KintoneRecordNumberField
            ),
        'code > 1 limit 500 offset 0'
    ],
    [
        sut.KintoneQueryBuilder()
            .greater_than(  # noqa: E131
                "code",
                1,
                KintoneRecordNumberField,
                equable=True
            ),
        'code >= 1 limit 500 offset 0'
    ],
    [
        sut.KintoneQueryBuilder()
            .less_than(  # noqa: E131
                "code",
                1,
                KintoneRecordNumberField
            ),
        'code < 1 limit 500 offset 0'
    ],
    [
        sut.KintoneQueryBuilder()
            .less_than(  # noqa: E131
                "code",
                1,
                KintoneRecordNumberField,
                equable=True
            ),
        'code <= 1 limit 500 offset 0'
    ],
    [
        sut.KintoneQueryBuilder()
            .like(  # noqa: E131
                "code",
                "value",
                KintoneRecordSingleLineTextField
            ),
        'code like "value" limit 500 offset 0'
    ],
    [
        sut.KintoneQueryBuilder()
            .like(  # noqa: E131
                "code",
                "value",
                KintoneRecordSingleLineTextField,
                is_not=True
            ),
        'code not like "value" limit 500 offset 0'
    ],
    [
        sut.KintoneQueryBuilder()
            .equal(  # noqa: E131
                "code",
                "value",
                KintoneRecordSingleLineTextField
            ).limit(10),
        'code = "value" limit 10 offset 0'
    ],
    [
        sut.KintoneQueryBuilder()
            .equal(  # noqa: E131
                "code",
                "value",
                KintoneRecordSingleLineTextField
            ).offset(10),
        'code = "value" limit 500 offset 10'
    ],
    [
        sut.KintoneQueryBuilder()
            .equal(  # noqa: E131
                "code",
                "value",
                KintoneRecordSingleLineTextField
            ).order_by("code", False),
        'code = "value" order by code asc limit 500 offset 0'
    ],
    [
        sut.KintoneQueryBuilder()
            .equal(  # noqa: E131
                "code",
                "value",
                KintoneRecordSingleLineTextField
            ).order_by("code", True),
        'code = "value" order by code desc limit 500 offset 0'
    ],
    [
        sut.KintoneQueryBuilder()
            .equal(  # noqa: E131
                "code",
                "value",
                KintoneRecordSingleLineTextField
            )
            .order_by("code", True)  # noqa: E131
            .order_by("code1", False),  # noqa: E131
        'code = "value" order by code desc, code1 asc limit 500 offset 0'
    ],
    [
        sut.KintoneQueryBuilder()
            .equal(  # noqa: E131
                "code",
                "value",
                KintoneRecordSingleLineTextField
            )
            .order_by("code", False)  # noqa: E131
            .limit(10),  # noqa: E131
        'code = "value" order by code asc limit 10 offset 0'
    ],
    [
        sut.KintoneQueryBuilder()
            .equal(  # noqa: E131
                "code",
                "value",
                KintoneRecordSingleLineTextField
            )
            .order_by("code", False)  # noqa: E131
            .limit(10)  # noqa: E131
            .offset(10),  # noqa: E131
        'code = "value" order by code asc limit 10 offset 10'
    ],
    [
        sut.KintoneQueryBuilder()
            .equal(  # noqa: E131
                "code",
                'value"value',
                KintoneRecordSingleLineTextField
            ),
        'code = "value\"value" limit 500 offset 0'
    ],
    [
        sut.KintoneQueryBuilder()
            .equal(  # noqa: E131
                "code",
                "value\\value",
                KintoneRecordSingleLineTextField
            ),
        'code = "value\\\\value" limit 500 offset 0'
    ],
    [
        sut.KintoneQueryBuilder()
            .equal("code", "value", KintoneRecordSingleLineTextField)  # noqa: E131
            .equal("code1", "value", KintoneRecordSingleLineTextField),
        'code = "value" and code1 = "value" limit 500 offset 0'
    ],
    [
        sut.KintoneQueryBuilder()
            .equal("code", "value", KintoneRecordSingleLineTextField)  # noqa: E131
            .or_()
            .equal("code1", "value", KintoneRecordSingleLineTextField),
        'code = "value" or code1 = "value" limit 500 offset 0'
    ],
    [
        sut.KintoneQueryBuilder()
            .equal("code", "value", KintoneRecordSingleLineTextField)  # noqa: E131
            .equal("code1", "value", KintoneRecordSingleLineTextField)
            .equal("code2", "value", KintoneRecordSingleLineTextField),
        'code = "value" and code1 = "value" and code2 = "value" limit 500 offset 0'
    ],
    [
        sut.KintoneQueryBuilder()
            .equal("code", "value", KintoneRecordSingleLineTextField)  # noqa: E131
            .open_()
            .equal("code1", "value", KintoneRecordSingleLineTextField)
            .or_()
            .equal("code2", "value", KintoneRecordSingleLineTextField),
        'code = "value" and (code1 = "value" or code2 = "value") limit 500 offset 0'
    ],
    [
        sut.KintoneQueryBuilder()
            .equal("code", "value", KintoneRecordSingleLineTextField)  # noqa: E131
            .open_()
            .equal("code1", "value", KintoneRecordSingleLineTextField)
            .or_()
            .equal("code2", "value", KintoneRecordSingleLineTextField)
            .close_(),
        'code = "value" and (code1 = "value" or code2 = "value") limit 500 offset 0'
    ],
    [
        sut.KintoneQueryBuilder()
             .equal("code", "value", KintoneRecordSingleLineTextField)  # noqa: E131
             .or_()
             .equal("code1", "value", KintoneRecordSingleLineTextField)
             .equal("code2", "value", KintoneRecordSingleLineTextField),
        'code = "value" or (code1 = "value" and code2 = "value") limit 500 offset 0'
    ],
    [
        sut.KintoneQueryBuilder()
            .open_()  # noqa: E131
            .equal("code", "value", KintoneRecordSingleLineTextField)
            .equal("code1", "value", KintoneRecordSingleLineTextField)
            .close_()
            .or_()
            .equal("code2", "value", KintoneRecordSingleLineTextField),
        '(code = "value" and code1 = "value") or code2 = "value" limit 500 offset 0'
    ],
    [
        sut.KintoneQueryBuilder()
            .equal("code", "value", KintoneRecordSingleLineTextField)  # noqa: E131
            .open_()
                .open_()  # noqa: E131
                .equal("code1", "value", KintoneRecordSingleLineTextField)
                .equal("code3", "value", KintoneRecordSingleLineTextField)
                .close_()
            .or_()
            .equal("code2", "value", KintoneRecordSingleLineTextField),
        'code = "value" and ((code1 = "value" and code3 = "value") or code2 = "value") limit 500 offset 0'
    ],
    [
        sut.KintoneQueryBuilder()
            .contain("code", {LoginUser()}, KintoneRecordUserSelectField),  # noqa: E131
        'code in (LOGINUSER()) limit 500 offset 0'
    ],
    [
        sut.KintoneQueryBuilder()
            .contain("code", {PrimaryOrg()}, KintoneRecordUserSelectField),  # noqa: E131
        'code in (PRIMARY_ORGANIZATION()) limit 500 offset 0'
    ],
    [
        sut.KintoneQueryBuilder()
            .equal("code", Now(), KintoneRecordDateField),  # noqa: E131
        'code = NOW() limit 500 offset 0'
    ],
    [
        sut.KintoneQueryBuilder()
            .greater_than("code", Now(), KintoneRecordDateField),  # noqa: E131
        'code > NOW() limit 500 offset 0'
    ],
    [
        sut.KintoneQueryBuilder()
            .equal("code", Today(), KintoneRecordDateField),  # noqa: E131
        'code = TODAY() limit 500 offset 0'
    ],
    [
        sut.KintoneQueryBuilder()
            .greater_than("code", Today(), KintoneRecordDateField),  # noqa: E131
        'code > TODAY() limit 500 offset 0'
    ],
    [
        sut.KintoneQueryBuilder()
            .equal("code", Yesterday(), KintoneRecordDateField),  # noqa: E131
        'code = YESTERDAY() limit 500 offset 0'
    ],
    [
        sut.KintoneQueryBuilder()
            .greater_than("code", Yesterday(), KintoneRecordDateField),  # noqa: E131
        'code > YESTERDAY() limit 500 offset 0'
    ],
    [
        sut.KintoneQueryBuilder()
            .equal("code", Tomorrow(), KintoneRecordDateField),  # noqa: E131
        'code = TOMORROW() limit 500 offset 0'
    ],
    [
        sut.KintoneQueryBuilder()
            .greater_than("code", Tomorrow(), KintoneRecordDateField),  # noqa: E131
        'code > TOMORROW() limit 500 offset 0'
    ],
    [
        sut.KintoneQueryBuilder()
            .equal("code", FromToday(1, "days"), KintoneRecordDateField),  # noqa: E131
        'code = FROM_TODAY(1, DAYS) limit 500 offset 0'
    ],
    [
        sut.KintoneQueryBuilder()
            .equal("code", ThisWeek(), KintoneRecordDateField),  # noqa: E131
        'code = THIS_WEEK() limit 500 offset 0'
    ],
    [
        sut.KintoneQueryBuilder()
            .equal("code", ThisWeek("sunday"), KintoneRecordDateField),  # noqa: E131
        'code = THIS_WEEK(SUNDAY) limit 500 offset 0'
    ],
    [
        sut.KintoneQueryBuilder()
            .equal("code", LastWeek(), KintoneRecordDateField),  # noqa: E131
        'code = LAST_WEEK() limit 500 offset 0'
    ],
    [
        sut.KintoneQueryBuilder()
            .equal("code", LastWeek("sunday"), KintoneRecordDateField),  # noqa: E131
        'code = LAST_WEEK(SUNDAY) limit 500 offset 0'
    ],
    [
        sut.KintoneQueryBuilder()
            .equal("code", NextWeek(), KintoneRecordDateField),  # noqa: E131
        'code = NEXT_WEEK() limit 500 offset 0'
    ],
    [
        sut.KintoneQueryBuilder()
            .equal("code", NextWeek("sunday"), KintoneRecordDateField),  # noqa: E131
        'code = NEXT_WEEK(SUNDAY) limit 500 offset 0'
    ],
    [
        sut.KintoneQueryBuilder()
            .equal("code", ThisMonth(), KintoneRecordDateField),  # noqa: E131
        'code = THIS_MONTH() limit 500 offset 0'
    ],
    [
        sut.KintoneQueryBuilder()
             .equal("code", LastMonth(), KintoneRecordDateField),  # noqa: E131
        'code = LAST_MONTH() limit 500 offset 0'
    ],
    [
        sut.KintoneQueryBuilder()
            .equal("code", NextMonth(), KintoneRecordDateField),  # noqa: E131
        'code = NEXT_MONTH() limit 500 offset 0'
    ],
    [
        sut.KintoneQueryBuilder()
            .equal("code", ThisYear(), KintoneRecordDateField),  # noqa: E131
        'code = THIS_YEAR() limit 500 offset 0'
    ],
    [
        sut.KintoneQueryBuilder()
            .equal("code", LastYear(), KintoneRecordDateField),  # noqa: E131
        'code = LAST_YEAR() limit 500 offset 0'
    ],
    [
        sut.KintoneQueryBuilder().equal("code", NextYear(), KintoneRecordDateField),
        'code = NEXT_YEAR() limit 500 offset 0'
    ],
    [
        sut.KintoneQueryBuilder().equal("code", date(2020, 1, 1), KintoneRecordDateField),
        'code = "2020-01-01" limit 500 offset 0'
    ],
    [
        sut.KintoneQueryBuilder().equal("code", datetime(2020, 1, 1, 9, 0, 0), KintoneRecordDateTimeField),
        'code = "2020-01-01T00:00:00Z" limit 500 offset 0'
    ],
    [
        sut.KintoneQueryBuilder().open_().equal("code", "B", field_type=KintoneRecordSingleLineTextField).or_().equal("code", "A", field_type=KintoneRecordSingleLineTextField).close_(),
        'code = "B" or code = "A" limit 500 offset 0'
    ],
    [
        sut.KintoneQueryBuilder()
            .open_()  # noqa: E131
                .equal("code", "B", field_type=KintoneRecordSingleLineTextField)  # noqa: E131
                .equal("code1", "value", KintoneRecordSingleLineTextField)
            .close_()
            .or_()
            .open_()
                .equal("code", "A", field_type=KintoneRecordSingleLineTextField)
                .equal("code1", "value", KintoneRecordSingleLineTextField)
            .close_(),
        '(code = "B" and code1 = "value") or (code = "A" and code1 = "value") limit 500 offset 0'
    ]
])
def test_query(builder: sut.KintoneQueryBuilder, expected: str):
    assert builder.build() == expected


def test_query_child_to_parent():
    parent_builder: sut.KintoneQueryBuilder = sut.KintoneQueryBuilder().open_().equal("code", "B", field_type=KintoneRecordSingleLineTextField)
    child_builder: sut.KintoneQueryBuilder = parent_builder.or_()
    parent_builder.equal("code", "A", field_type=KintoneRecordSingleLineTextField).close_()
    assert child_builder is not None
    assert parent_builder.build() == 'code = "B" or code = "A" limit 500 offset 0'

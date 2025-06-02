from typing import Type

import pytest
from bozupy.kintone.record.dto import KintoneRecord, KintoneRecordField, KintoneRecordIDField, \
    KintoneRecordRevisionField, KintoneRecordCreatorField, KintoneRecordCreatedTimeField, KintoneRecordModifierField, \
    KintoneRecordUpdatedTimeField, KintoneRecordSingleLineTextField, KintoneRecordMultiLineTextField, \
    KintoneRecordRichTextField, KintoneRecordNumberField, KintoneRecordCalcField, KintoneRecordCheckBoxField, \
    KintoneRecordRadioButtonField, KintoneRecordMultiSelectField, KintoneRecordDropDownField, \
    KintoneRecordUserSelectField, KintoneRecordOrgSelectField, KintoneRecordGroupSelectField, KintoneRecordDateField, \
    KintoneRecordTimeField, KintoneRecordDateTimeField, KintoneRecordFileField, KintoneRecordLinkField, \
    KintoneRecordSubtableField, KintoneRecordCategoryField, KintoneRecordStatusField, \
    KintoneRecordAssigneeField, KintoneRecordCodeField, KIntoneRecordSubtableRow

from bozupy.kintone.record import dxo as sut


# noinspection SpellCheckingInspection
@pytest.mark.parametrize(["input_", "expected_class"], [
    [
        {"フィールドコード": {
            "type": "RECORD_NUMBER",
            "value": "1"
        }},
        KintoneRecordCodeField
    ],
    [
        {"フィールドコード": {
            "type": "__ID__",
            "value": "1"
        }},
        KintoneRecordIDField
    ],
    [
        {"フィールドコード": {
            "type": "__REVISION__",
            "value": "5"
        }},
        KintoneRecordRevisionField
    ],
    [
        {"フィールドコード": {
            "type": "CREATOR",
            "value": {
                "code": "sato",
                "name": "Noboru Sato"
            }
        }},
        KintoneRecordCreatorField
    ],
    [
        {"フィールドコード": {
            "type": "CREATED_TIME",
            "value": "2012-01-11T11:30:00Z"
        }},
        KintoneRecordCreatedTimeField
    ],
    [
        {"フィールドコード": {
            "type": "MODIFIER",
            "value": {
                "code": "sato",
                "name": "Noboru Sato"
            }
        }},
        KintoneRecordModifierField
    ],
    [
        {"フィールドコード": {
            "type": "UPDATED_TIME",
            "value": "2012-01-11T11:30:00Z"
        }},
        KintoneRecordUpdatedTimeField
    ],
    [
        {"フィールドコード": {
            "type": "SINGLE_LINE_TEXT",
            "value": "テストです。"
        }},
        KintoneRecordSingleLineTextField
    ],
    [
        {"フィールドコード": {
            "type": "MULTI_LINE_TEXT",
            "value": "テスト\nです。"
        }},
        KintoneRecordMultiLineTextField
    ],
    [
        {"フィールドコード": {
            "type": "RICH_TEXT",
            "value": "<a href=\"http://www.example.com\">サンプル</a>"
        }},
        KintoneRecordRichTextField
    ],
    [
        {"フィールドコード": {
            "type": "NUMBER",
            "value": "123"
        }},
        KintoneRecordNumberField
    ],
    [
        {"フィールドコード": {
            "type": "CALC",
            "value": "123"
        }},
        KintoneRecordCalcField
    ],
    [
        {"フィールドコード": {
            "type": "CHECK_BOX",
            "value": [
                "選択肢1",
                "選択肢2"
            ]
        }},
        KintoneRecordCheckBoxField
    ],
    [
        {"フィールドコード": {
            "type": "RADIO_BUTTON",
            "value": "選択肢3"
        }},
        KintoneRecordRadioButtonField
    ],
    [
        {"フィールドコード": {
            "type": "MULTI_SELECT",
            "value": [
                "選択肢1",
                "選択肢2"
            ]
        }},
        KintoneRecordMultiSelectField
    ],
    [
        {"フィールドコード": {
            "type": "DROP_DOWN",
            "value": "選択肢3"
        }},
        KintoneRecordDropDownField
    ],
    [
        {"フィールドコード": {
            "type": "USER_SELECT",
            "value": [
                {
                    "code": "sato",
                    "name": "Noboru Sato"
                },
                {
                    "code": "kato",
                    "name": "Misaki Kato"
                }
            ]
        }},
        KintoneRecordUserSelectField
    ],
    [
        {"フィールドコード": {
            "type": "ORGANIZATION_SELECT",
            "value": [
                {
                    "code": "kaihatsu",
                    "name": "開発部"
                },
                {
                    "code": "jinji",
                    "name": "人事部"
                }
            ]
        }},
        KintoneRecordOrgSelectField
    ],
    [
        {"フィールドコード": {
            "type": "GROUP_SELECT",
            "value": [
                {
                    "code": "project_manager",
                    "name": "プロジェクトマネージャー"
                },
                {
                    "code": "team_leader",
                    "name": "チームリーダー"
                }
            ]
        }},
        KintoneRecordGroupSelectField
    ],
    [
        {"フィールドコード": {
            "type": "DATE",
            "value": "2012-01-11"
        }},
        KintoneRecordDateField
    ],
    [
        {"フィールドコード": {
            "type": "TIME",
            "value": "11:30"
        }},
        KintoneRecordTimeField
    ],
    [
        {"フィールドコード": {
            "type": "DATETIME",
            "value": "2012-01-11T11:30:00Z"
        }},
        KintoneRecordDateTimeField
    ],
    [
        {"フィールドコード": {
            "type": "LINK",
            "value": "http://www.example.com/"
        }},
        KintoneRecordLinkField
    ],
    [
        {"フィールドコード": {
            "type": "FILE",
            "value": [
                {
                    "contentType": "text/plain",
                    "fileKey": "201202061155587E339F9067544F1A92C743460E3D12B3297",
                    "name": "17to20_VerupLog （1）.txt",
                    "size": "23175"
                },
                {
                    "contentType": "text/plain",
                    "fileKey": "201202061155583C763E30196F419E83E91D2E4A03746C273",
                    "name": "17to20_VerupLog.txt",
                    "size": "23175"
                }
            ]
        }},
        KintoneRecordFileField
    ],
    # [
    #     {"フィールドコード": {
    #         "type": "LOOKUP",
    #         "value": "Code001"
    #     }},
    #     KintoneRecordLookupField
    # ],
    [
        {"フィールドコード": {
            "type": "CATEGORY",
            "value": [
                "category1",
                "category2"
            ]
        }},
        KintoneRecordCategoryField
    ],
    [
        {"フィールドコード": {
            "type": "STATUS",
            "value": "未処理"
        }},
        KintoneRecordStatusField
    ],
    [
        {"フィールドコード": {
            "type": "STATUS_ASSIGNEE",
            "value": [
                {
                    "code": "sato",
                    "name": "Noboru Sato"
                }
            ]
        }},
        KintoneRecordAssigneeField
    ],
    [
        {"フィールドコード": {
            "type": "DATE",
            "value": None
        }},
        KintoneRecordDateField
    ],
    [
        {"フィールドコード": {
            "type": "TIME",
            "value": None
        }},
        KintoneRecordTimeField
    ],
    [
        {"フィールドコード": {
            "type": "DATETIME",
            "value": ""
        }},
        KintoneRecordDateTimeField
    ],
    [
        {"フィールドコード": {
            "type": "DROP_DOWN",
            "value": None
        }},
        KintoneRecordDropDownField
    ],
    [
        {"フィールドコード": {
            "type": "RADIO_BUTTON",
            "value": None
        }},
        KintoneRecordRadioButtonField
    ],
])
def test_to_record(input_: dict, expected_class: Type[KintoneRecordField]) -> None:
    actual: KintoneRecord = sut.to_record(input_, 1, 1)
    assert actual.app_id == 1
    assert actual.id == 1
    assert "フィールドコード" in actual.fields
    assert isinstance(actual.fields["フィールドコード"], expected_class)


def test_to_record_SUBTABLE():
    input_: dict = {"フィールドコード": {
            "type": "SUBTABLE",
            "value": [
                {
                    "id": "48290",
                    "value": {
                        "文字列__1行__0": {
                            "type": "SINGLE_LINE_TEXT",
                            "value": "サンプル１"
                        },
                        "数値_0": {
                            "type": "NUMBER",
                            "value": "1"
                        },
                        "チェックボックス_0": {
                            "type": "CHECK_BOX",
                            "value": ["選択肢1"]
                        }
                    }
                },
                {
                    "id": "48291",
                    "value": {
                        "文字列__1行__0": {
                            "type": "SINGLE_LINE_TEXT",
                            "value": "サンプル２"
                        },
                        "数値_0": {
                            "type": "NUMBER",
                            "value": "2"
                        },
                        "チェックボックス_0": {
                            "type": "CHECK_BOX",
                            "value": ["選択肢2"]
                        }
                    }
                }
            ]
        }
    }
    actual_record: KintoneRecord = sut.to_record(input_, 1, 1)
    assert actual_record.app_id == 1
    assert actual_record.id == 1
    assert "フィールドコード" in actual_record.fields
    actual_field: KintoneRecordField = actual_record.fields["フィールドコード"]
    assert isinstance(actual_field, KintoneRecordSubtableField)
    actual_rows: list[KIntoneRecordSubtableRow] = actual_field.value
    assert len(actual_rows) == 2
    assert actual_rows[0].id == 48290
    assert "文字列__1行__0" in actual_rows[0].fields
    assert isinstance(actual_rows[0].fields["文字列__1行__0"], KintoneRecordSingleLineTextField)
    assert "数値_0" in actual_rows[0].fields
    assert isinstance(actual_rows[0].fields["数値_0"], KintoneRecordNumberField)
    assert "チェックボックス_0" in actual_rows[0].fields
    assert isinstance(actual_rows[0].fields["チェックボックス_0"], KintoneRecordCheckBoxField)
    assert actual_rows[1].id == 48291
    assert "文字列__1行__0" in actual_rows[1].fields
    assert isinstance(actual_rows[1].fields["文字列__1行__0"], KintoneRecordSingleLineTextField)
    assert "数値_0" in actual_rows[1].fields
    assert isinstance(actual_rows[1].fields["数値_0"], KintoneRecordNumberField)
    assert "チェックボックス_0" in actual_rows[1].fields
    assert isinstance(actual_rows[1].fields["チェックボックス_0"], KintoneRecordCheckBoxField)


@pytest.mark.parametrize(["input_"], [
    [KintoneRecord(app_id=1, id=1)]
])
def test_to_dict(input_: KintoneRecord) -> None:
    assert sut.to_dict(input_) is not None


def test_to_dict_update() -> None:
    record: KintoneRecord = KintoneRecord(app_id=1, id=1)
    record.set_field(KintoneRecordIDField("id", 1))
    assert len(sut.to_dict(record, True)) == 0

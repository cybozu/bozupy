from typing import Type

import pytest

from bozupy.kintone.record.dto import KintoneRecordField, KintoneRecordIDField, KintoneRecordCodeField, \
    KintoneRecordRevisionField, KintoneRecordCreatorField, KintoneRecordCreatedTimeField, KintoneRecordModifierField, \
    KintoneRecordUpdatedTimeField, KintoneRecordSingleLineTextField, KintoneRecordMultiLineTextField, \
    KintoneRecordRichTextField, KintoneRecordNumberField, KintoneRecordCalcField, KintoneRecordCheckBoxField, \
    KintoneRecordRadioButtonField, KintoneRecordMultiSelectField, KintoneRecordDropDownField, \
    KintoneRecordUserSelectField, KintoneRecordOrgSelectField, KintoneRecordGroupSelectField, KintoneRecordDateField, \
    KintoneRecordTimeField, KintoneRecordDateTimeField, KintoneRecordLinkField, KintoneRecordFileField, \
    KintoneRecordSubtableField


# noinspection SpellCheckingInspection
@pytest.mark.parametrize(["input_", "class_", "expected"], [
    [
        {
            "フィールドコード": {
                "type": "RECORD_NUMBER",
                "value": "1"
            }
        },
        KintoneRecordIDField,
        None
    ],
    [
        {
            "フィールドコード": {
                "type": "__ID__",
                "value": "1"
            }
        },
        KintoneRecordCodeField,
        None
    ],
    [
        {
            "フィールドコード": {
                "type": "__REVISION__",
                "value": "5"
            }
        },
        KintoneRecordRevisionField,
        None
    ],
    [
        {
            "フィールドコード": {
                "type": "CREATOR",
                "value": {
                    "code": "sato",
                    "name": "Noboru Sato"
                }
            }
        },
        KintoneRecordCreatorField,
        None
    ],
    [
        {
            "フィールドコード": {
                "type": "CREATED_TIME",
                "value": "2012-01-11T11:30:00Z"
            }
        },
        KintoneRecordCreatedTimeField,
        None
    ],
    [
        {
            "フィールドコード": {
                "type": "MODIFIER",
                "value": {
                    "code": "sato",
                    "name": "Noboru Sato"
                }
            }
        },
        KintoneRecordModifierField,
        None
    ],
    [
        {
            "フィールドコード": {
                "type": "UPDATED_TIME",
                "value": "2012-01-11T11:30:00Z"
            }
        },
        KintoneRecordUpdatedTimeField,
        None
    ],
    [
        {
            "フィールドコード": {
                "type": "SINGLE_LINE_TEXT",
                "value": "テストです。"
            }
        },
        KintoneRecordSingleLineTextField,
        {"value": "テストです。"}
    ],
    [
        {
            "フィールドコード": {
                "type": "MULTI_LINE_TEXT",
                "value": "テスト\nです。"
            }
        },
        KintoneRecordMultiLineTextField,
        {"value": "テスト\nです。"}
    ],
    [
        {
            "フィールドコード": {
                "type": "RICH_TEXT",
                "value": "<a href=\"http://www.example.com\">サンプル</a>"
            }
        },
        KintoneRecordRichTextField,
        {"value": "<a href=\"http://www.example.com\">サンプル</a>"}
    ],
    [
        {
            "フィールドコード": {
                "type": "NUMBER",
                "value": "123"
            }
        },
        KintoneRecordNumberField,
        {"value": "123.0"}
    ],
    [
        {
            "フィールドコード": {
                "type": "NUMBER",
                "value": ""
            }
        },
        KintoneRecordNumberField,
        {"value": None}
    ],
    [
        {
            "フィールドコード": {
                "type": "CALC",
                "value": "123"
            }
        },
        KintoneRecordCalcField,
        {"value": "123"}
    ],
    [
        {
            "フィールドコード": {
                "type": "CHECK_BOX",
                "value": [
                    "選択肢1",
                    "選択肢2"
                ]
            }
        },
        KintoneRecordCheckBoxField,
        {"value": ["選択肢1", "選択肢2"]}
    ],
    [
        {
            "フィールドコード": {
                "type": "RADIO_BUTTON",
                "value": "選択肢3"
            }
        },
        KintoneRecordRadioButtonField,
        {"value": "選択肢3"}
    ],
    [
        {
            "フィールドコード": {
                "type": "RADIO_BUTTON",
                "value": None
            }
        },
        KintoneRecordRadioButtonField,
        {"value": None}
    ],
    [
        {
            "フィールドコード": {
                "type": "MULTI_SELECT",
                "value": [
                    "選択肢1",
                    "選択肢2"
                ]
            }
        },
        KintoneRecordMultiSelectField,
        {"value": ["選択肢1", "選択肢2"]}
    ],
    [
        {
            "フィールドコード": {
                "type": "DROP_DOWN",
                "value": "選択肢3"
            }
        },
        KintoneRecordDropDownField,
        {"value": "選択肢3"}
    ],
    [
        {
            "フィールドコード": {
                "type": "DROP_DOWN",
                "value": None
            }
        },
        KintoneRecordDropDownField,
        {"value": None}
    ],
    [
        {
            "フィールドコード": {
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
            }
        },
        KintoneRecordUserSelectField,
        {"value": [{"code": "kato"}, {"code": "sato"}]}
    ],
    [
        {
            "フィールドコード": {
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
            }
        },
        KintoneRecordOrgSelectField,
        {"value": [{"code": "jinji"}, {"code": "kaihatsu"}]}
    ],
    [
        {
            "フィールドコード": {
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
            }
        },
        KintoneRecordGroupSelectField,
        {"value": [{"code": "project_manager"}, {"code": "team_leader"}]}
    ],
    [
        {
            "フィールドコード": {
                "type": "DATE",
                "value": "2012-01-11"
            }
        },
        KintoneRecordDateField,
        {"value": "2012-01-11"}
    ],
    [
        {
            "フィールドコード": {
                "type": "TIME",
                "value": "11:30"
            }
        },
        KintoneRecordTimeField,
        {"value": "11:30"}
    ],
    [
        {
            "フィールドコード": {
                "type": "DATETIME",
                "value": "2012-01-11T11:30:00Z"
            }
        },
        KintoneRecordDateTimeField,
        {"value": "2012-01-11T11:30:00Z"}
    ],
    [
        {
            "フィールドコード": {
                "type": "LINK",
                "value": "http://www.example.com/"
            }
        },
        KintoneRecordLinkField,
        {"value": "http://www.example.com/"}
    ],
    [
        {
            "フィールドコード": {
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
            }
        },
        KintoneRecordFileField,
        {
            "value": [
                {"fileKey": "201202061155587E339F9067544F1A92C743460E3D12B3297"},
                {"fileKey": "201202061155583C763E30196F419E83E91D2E4A03746C273"}
            ]
        }
    ]
    # [
    #     {
    #         "フィールドコード": {
    #             "value": "Code001"
    #         }
    #     },
    #     KintoneRecordLookupField,
    #     {"value": "Code001"}
    # ]
])
def test_KintoneRecordField_json_convert(input_: dict, class_: Type[KintoneRecordField], expected: dict | None):
    actual: KintoneRecordField = class_.from_json("フィールドコード", input_["フィールドコード"]["value"])
    if expected is not None:
        assert actual.to_json() == expected


def test_KintoneRecordSubtableField_json_convert():
    # input_: dict = {
    #     "フィールドコード": {
    #         "type": "SUBTABLE",
    #         "value": [
    #             {
    #                 "id": "48290",
    #                 "value": {
    #                     "文字列__1行__0": {
    #                         "type": "SINGLE_LINE_TEXT",
    #                         "value": "サンプル１"
    #                     },
    #                     "数値_0": {
    #                         "type": "NUMBER",
    #                         "value": "1"
    #                     },
    #                     "チェックボックス_0": {
    #                         "type": "CHECK_BOX",
    #                         "value": ["選択肢1"]
    #                     }
    #                 }
    #             },
    #             {
    #                 "id": "48291",
    #                 "value": {
    #                     "文字列__1行__0": {
    #                         "type": "SINGLE_LINE_TEXT",
    #                         "value": "サンプル２"
    #                     },
    #                     "数値_0": {
    #                         "type": "NUMBER",
    #                         "value": "2"
    #                     },
    #                     "チェックボックス_0": {
    #                         "type": "CHECK_BOX",
    #                         "value": ["選択肢2"]
    #                     }
    #                 }
    #             }
    #         ]
    #     }
    # }
    actual: KintoneRecordSubtableField = KintoneRecordSubtableField.from_json(
        code="フィールドコード",
        value=[
            (
                48290,
                [
                    KintoneRecordSingleLineTextField.from_json(code="文字列__1行__0", value="サンプル１"),
                    KintoneRecordNumberField.from_json(code="数値_0", value=1),
                    KintoneRecordCheckBoxField.from_json(code="チェックボックス_0", value=["選択肢1"])
                ]
            ),
            (
                48291,
                [
                    KintoneRecordSingleLineTextField.from_json(code="文字列__1行__0", value="サンプル２"),
                    KintoneRecordNumberField.from_json(code="数値_0", value=2),
                    KintoneRecordCheckBoxField.from_json(code="チェックボックス_0", value=["選択肢2"])
                ]
            )
        ]
    )
    expected: dict = {
        "value": [
            {
                "id": "48290",
                "value": {
                    "文字列__1行__0": {
                        "value": "サンプル１"
                    },
                    "数値_0": {
                        "value": "1.0"
                    },
                    "チェックボックス_0": {
                        "value": ["選択肢1"]
                    }
                }
            },
            {
                "id": "48291",
                "value": {
                    "文字列__1行__0": {
                        "value": "サンプル２"
                    },
                    "数値_0": {
                        "value": "2.0"
                    },
                    "チェックボックス_0": {
                        "value": ["選択肢2"]
                    }
                }
            }
        ]
    }
    assert actual.to_json() == expected

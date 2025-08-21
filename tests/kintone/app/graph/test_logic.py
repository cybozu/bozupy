
import pytest

from bozupy.kintone.app.graph import logic as sut, KintoneDateGrouper, KintoneTimeGrouper, KintoneDateFreqs, \
    KintoneTimeFreqs
from bozupy.kintone.record import KintoneRecordRadioButtonField, KintoneRecordCalcField, KintoneRecordCreatedTimeField
from bozupy.kintone.record.dto import KintoneRecordNumberField, KintoneRecordTimeField


@pytest.mark.parametrize(["builder", "expected"], [
    [
        sut.barplot(
            "初期設定",
            sut.KintoneGraphFrame()
                    .groupby(("ラジオボタン", KintoneRecordRadioButtonField))  # noqa: E131
                    .count()
                    .sort_values(ascending=False)
        ),
        {
            "chartType": "BAR",
            "chartMode": "NORMAL",
            "name": "初期設定",
            "groups": [
                {
                    "code": "ラジオボタン"
                }
            ],
            "aggregations": [
                {
                    "type": "COUNT"
                }
            ],
            "sorts": [
                {
                    "by": "TOTAL",
                    "order": "DESC"
                }
            ]
        }
    ],
    [
        sut.tableplot(
            "様々なグラフの設定",
            sut.KintoneGraphFrame()
                    .groupby(("ラジオボタン", KintoneRecordRadioButtonField))  # noqa: E131
                    .groupby(KintoneDateGrouper("作成日時", KintoneRecordCreatedTimeField, KintoneDateFreqs.YEAR))
                    .groupby(KintoneTimeGrouper("時刻", KintoneRecordTimeField, KintoneTimeFreqs.MINUTE))
                    .count()
                    .sum("数値", KintoneRecordNumberField)
                    .average("計算", KintoneRecordCalcField)
                    .max("作成日時", KintoneRecordCreatedTimeField)
                    .min("時刻", KintoneRecordTimeField)
                    .sort_values(ascending=False)
                    .sort_values("ラジオボタン", ascending=True)
                    .sort_values("作成日時", ascending=False)
        ),
        {
            "chartType": "TABLE",
            "name": "様々なグラフの設定",
            "groups": [
                {
                    "code": "ラジオボタン"
                },
                {
                    "code": "作成日時",
                    "per": "YEAR"
                },
                {
                    "code": "時刻",
                    "per": "MINUTE"
                }
            ],
            "aggregations": [
                {
                    "type": "COUNT"
                },
                {
                    "type": "SUM",
                    "code": "数値"
                },
                {
                    "type": "AVERAGE",
                    "code": "計算"
                },
                {
                    "type": "MAX",
                    "code": "作成日時"
                },
                {
                    "type": "MIN",
                    "code": "時刻"
                }
            ],
            "sorts": [
                {
                    "by": "TOTAL",
                    "order": "DESC"
                },
                {
                    "by": "GROUP1",
                    "order": "ASC"
                },
                {
                    "by": "GROUP2",
                    "order": "DESC"
                }
            ],
        }
    ]
])
def test_query(builder: sut.KintoneGraphBuilder, expected: dict):
    assert builder.build() == expected

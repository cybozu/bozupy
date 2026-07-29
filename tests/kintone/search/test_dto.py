import pytest

from bozupy.kintone.search.constant import KintoneSearchOperators, KintoneSearchScopes
from bozupy.kintone.search.dto import KintoneSearchCondition, KintoneSearchScope

from ...testtool import not_raises


@pytest.mark.parametrize(["keywords"], [
    # 検索語が0個
    [[]],
    # 検索語が20個を超える
    [[str(i) for i in range(21)]],
    # 検索語が0文字
    [[""]],
    # 検索語が50文字を超える
    [["a" * 51]],
])
def test_condition_invalid_keywords(keywords: list[str]) -> None:
    with pytest.raises(ValueError):
        KintoneSearchCondition(KintoneSearchOperators.AND, keywords)


def test_condition_valid_keywords() -> None:
    with not_raises():
        KintoneSearchCondition(KintoneSearchOperators.AND, [str(i) for i in range(20)])
        KintoneSearchCondition(KintoneSearchOperators.NOT, ["a" * 50])


@pytest.mark.parametrize(["scope", "ids", "codes"], [
    # アプリ・スペースにログイン名は指定できない
    [KintoneSearchScopes.APP, None, {"user1"}],
    [KintoneSearchScopes.SPACE, {1}, {"user1"}],
    # ピープル・メッセージにIDは指定できない
    [KintoneSearchScopes.PEOPLE, {1}, None],
    [KintoneSearchScopes.MESSAGE, {1}, {"user1"}],
    # 21個以上は指定できない
    [KintoneSearchScopes.APP, set(range(21)), None],
    [KintoneSearchScopes.PEOPLE, None, {f"user{i}" for i in range(21)}],
])
def test_scope_invalid(scope: KintoneSearchScopes, ids: set[int] | None, codes: set[str] | None) -> None:
    with pytest.raises(ValueError):
        KintoneSearchScope(scope, ids, codes)


def test_scope_valid() -> None:
    with not_raises():
        # 省略した場合はすべてのアプリ・スペース・ピープル・メッセージが対象になる
        KintoneSearchScope(KintoneSearchScopes.APP)
        KintoneSearchScope(KintoneSearchScopes.APP, ids={1, 2})
        KintoneSearchScope(KintoneSearchScopes.SPACE, ids=set(range(20)))
        KintoneSearchScope(KintoneSearchScopes.PEOPLE, codes={"user1"})
        KintoneSearchScope(KintoneSearchScopes.MESSAGE, codes={"user1"})

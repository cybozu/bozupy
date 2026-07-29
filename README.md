# bozupy

> [!WARNING]
> This is not an officially supported Cybozu/Kintone product. Please do not send requests for additional features or bug fixes to account manager or customer support.

> [!WARNING]
> このリポジトリは cybozu.com の一利用者として業務で kintone を利用しているサイボウズ社員によって作られたものを現状のまま ("AS IS") で公開しているものです。kintone のサービスの一部として提供しているものではありません。機能の追加や不具合の修正のリクエストをカスタマーサポートや担当営業に送ることはお控えください。公式の SDK の提供要望は [kintone 開発チームへのフィードバックとしてお送りください](https://jp.cybozu.help/k/ja/trouble_shooting/general/send_feedback.html) 😉


[![test](https://github.com/cybozu/bozupy/actions/workflows/test.yaml/badge.svg)](https://github.com/cybozu/bozupy/actions/workflows/test.yaml)
![PyPI - Version](https://img.shields.io/pypi/v/bozupy)

cybozu.com Python library

## 設定
### 環境変数

以下の環境変数を設定すると自動で使用してくれます。

```env
CYBOZU_SUBDOMAIN=
CYBOZU_USERNAME=
CYBOZU_PASSWORD=

KINTONE_APP_TOKEN_<アプリID>=
```

### シークレットの外部参照

`CYBOZU_PASSWORD` と `KINTONE_APP_TOKEN_<アプリID>` は、値を直接書く代わりに以下のプレフィックスを付けると外部のシークレットストアから取得します。

| 記法 | 取得先 | 例 |
| --- | --- | --- |
| `aws:<シークレットID>` | AWS Secrets Manager | `CYBOZU_PASSWORD=aws:my/cybozu/password` |
| `op://<Vault>/<アイテム>/<フィールド>` | 1Password (`op` コマンド) | `CYBOZU_PASSWORD=op://Private/cybozu/password` |

- `aws:` は `AWS_SECRET_PROFILE` (なければ `AWS_PROFILE`)、`AWS_SECRET_REGION_NAME` (なければ `AWS_REGION_NAME`、デフォルト `ap-northeast-1`) を使います。
- `op://` は [1Password CLI](https://developer.1password.com/docs/cli/) の `op read` を実行するため、事前にインストールとサインインが必要です。`op:<Vault>/<アイテム>/<フィールド>` のように `//` を省略した記法も使えます。複数アカウントを使い分けている場合は `OP_ACCOUNT` を、`op` 以外のコマンド名を使う場合は `OP_COMMAND` を設定してください。

## 使い方

```python
# kintone
from bozupy import kintone
from bozupy.kintone.record import KintoneRecord, KintoneRecordSingleLineTextField

# env: KINTONE_APP_TOKEN_1=xxxxx を設定しておくとアクセストークンを使ってアクセスする 
# それがなければユーザー名とパスワードを使ってアクセスする
record: KintoneRecord = kintone.record.get_record(app_id=1, record_id=1)
print(record.get_field("code", KintoneRecordSingleLineTextField).value)

## 環境変数以外の認証情報を使うことも可能
from bozupy import AccessData
access_data: AccessData = AccessData('<subdomain>', 'username', 'password')
record = kintone.record.get_record(app_id=1, record_id=1, access_data=access_data)


# garoon
from bozupy import garoon
from bozupy.garoon.schedule import GaroonEvent

event: GaroonEvent = garoon.schedule.get_event(event_id=1)

# slash
from bozupy import slash
from bozupy.slash import User

users: list[User] = [u for u in slash.get_users(access_data=access_data)]
```

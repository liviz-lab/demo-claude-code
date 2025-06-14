# やりたいこと
## FastAPIのミドルウェア周りの検証と確認
1. GET POST PUT DELETE メソッドを用意
   1. FastAPi DependsでDI注入
2. pydanticモデルを使用して、バリデーションさせる
   1. schemasディレクトリ配下に作る requests responses 別ける
   2. パスパラメータとクエリーとボディのJSONからリクエスト想定
   3. 返却は全てJSON
3. バリデーションエラーと必須パラメータエラーのメッセージを作る
   1. core/error.py に作る
4. ミドルウェア用意して、pydanticのエラーレスポンスをカスタムさせる
5. deps用意 factriesで、DI注入させる
   1. db.pyはセッション周り
   2. auth.pyは必須ヘッダーを適当に用意して、無かったらエラーにさせる
### アーキテクチャとか
- DBはインメモリとかでOK.ローカルで動作確認できれば良い
- 環境変数から諸々の設定を取得できる形に .env -> core/config.pyでpydantic経由で取得する

```
demo-claude-code
app/
├── api/
│   └── endpoints.py
├── domain
├── usecase/
│   ├── command
│   └── query
├── deps/
│   ├── factories
│   ├── db.py
│   └── auth.py 
└── main.py
schemas/
├── reqests
└── responses
tests/
├── api
├── domain
├── usecase
```

## リファクタリング1
- エンドポイントの引数は、pydanticモデルを経由して受け取る  
```python
# NOW
async def get_users(
    name: Optional[str] = Query(None, description="名前で検索"),
    min_age: Optional[int]  = Query(None, ge=0,  description="最小年齢"),
    max_age: Optional[int]  = Query(None, le=120, description="最大年齢"),
    limit:     int          = Query(10, ge=1,  le=100, description="取得件数"),
    offset:    int          = Query(0,  ge=0,  description="オフセット"),
    user_factory: UserFactory = Depends(get_user_factory),
    api_key: str = Depends(verify_api_key),
)

# feat
async def get_users(query: Annotated[UsersQuery, Depends()])
```
- pydanticモデルでレスポンス文を書くけど、`limit` などは共通で使用するので **common 的な型**で定義して、`UsersQuery` に継承させる  
- `deps / factories` は DI で注入するだけ。ドメインロジックを書く場所ではない  
- `endpoints → usecase → domain` の順に依存  
- `ports` を新規で作成し、`infra` に対する ORM のインターフェース定義を作成  
- `infra` ディレクトリを削除し、インメモリに対する ORM を作成  
- `usecase` は複数エンドポイントに分ける。**1 エンドポイント＝1 usecase**  
- `usecases` は **オーケストレーション** が責務  
- `domain` に **ドメインロジック** を書け  
- `core/error` に、バリデーションエラー時と必須エラー時の **カスタムレスポンス**に使用するメッセージを定義  
- 上記のエラー時は以下の構造で返却させる  

```json
{
  "message": "",
  "code": "",
  "detail": ""
}
```

## リファクタリング2
- endpoints_new をendpointsに変更
  - 旧ファイルが残っているので削除してね
- python3.13で推奨している型ヒントの書き方に変更してください
- mypyの型ヒントエラーが発生している個所を修正してください
- .vscodeディレクトリを作成して、ruffのフォーマットを保存時にさせるsettingsを作って
  - 保存時にruffのフォーマット、インポート
- pyprojectかsettingsにruffの一行制限を119文字にする設定を追加
- エラー時のメッセージについて
  - バリデーションエラー時に、バリデーションエラーとなっている入力値を出力させる
  - 必須項目がないときに、必須項目名を出力させる

## リファクタリング3
- api_key をエンドポイントのメソッドの引数に渡すことでバリデーションをするのではなく、middlewareでヘッダーの値を確認してバリデーションして
  - 多分今そうゆう形になってるけど、routerの中に設定していないので設定して
  - その後メソッドからapi_keyを削除できるはず
- エンドポイントファイルないで、インポートが複数になっているものを、__init__とかでまとめてインポートするように修正してください（無理なら我慢する）
-  usecase: GetUsersUseCase = Depends(get_get_users_usecase)の書き方がおかしいので、しゅうせいしてくれ

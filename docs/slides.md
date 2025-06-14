---
marp: true
theme: default
paginate: true
style: |
  section {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    font-size: 18px;
  }
  h1 {
    color: #ffffff;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    font-size: 2.2em;
  }
  h2 {
    color: #f8f9fa;
    border-bottom: 2px solid #ffd700;
    padding-bottom: 10px;
    font-size: 1.8em;
  }
  h3 {
    font-size: 1.3em;
    margin-bottom: 10px;
  }
  code {
    background: #2d3748;
    color: #68d391;
    border-radius: 4px;
    padding: 2px 6px;
    font-size: 0.9em;
    font-weight: 500;
  }
  pre {
    background: #1a1a1a;
    border: 1px solid #4a5568;
    border-radius: 8px;
    padding: 20px;
    margin: 10px 0;
    overflow-x: auto;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
  }
  pre code {
    background: transparent;
    color: #f7fafc;
    padding: 0;
    font-size: 0.9em;
    line-height: 1.5;
    font-weight: 400;
    text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
  }
  /* 文字列の色を見やすく */
  pre code .hljs-string,
  pre code .token.string,
  pre code .string {
    color: #87ceeb !important;
  }
  /* 変数・プロパティを区別 */
  pre code .hljs-variable,
  pre code .token.variable,
  pre code .hljs-property,
  pre code .token.property {
    color: #ffa500 !important;
  }
  /* f-string内の変数 */
  pre code .hljs-subst,
  pre code .token.interpolation,
  pre code .token.embedded-expression {
    color: #ffeb3b !important;
  }
  /* コメント */
  pre code .hljs-comment,
  pre code .token.comment {
    color: #a0aec0 !important;
    font-style: italic;
  }
  /* キーワード */
  pre code .hljs-keyword,
  pre code .token.keyword {
    color: #81a2be !important;
    font-weight: 600;
  }
  /* 関数名 */
  pre code .hljs-function,
  pre code .token.function {
    color: #f0c674 !important;
  }
  .columns {
    display: flex;
    gap: 15px;
  }
  .column {
    flex: 1;
  }
  .highlight {
    background: rgba(255,215,0,0.2);
    padding: 12px;
    border-radius: 8px;
    border-left: 4px solid #ffd700;
    font-size: 0.95em;
  }
  ul, ol {
    font-size: 0.95em;
    line-height: 1.4;
  }
---

# FastAPI Clean Architecture
## DI & Middleware Deep Dive

### from liviz (AI丸投げ開発day1)
---

## 📋 Agenda

<div class="columns">
<div class="column">

### アーキテクチャ設計
- Clean Architecture概要
- レイヤー分離戦略
- CQRS パターン
- ヘキサゴナルアーキテクチャ

</div>
<div class="column">

### FastAPI実装
- 依存性注入(DI)システム
- ミドルウェアスタック
- エラーハンドリング
- 実装のベストプラクティス

</div>
</div>

---

## 🏗️ アーキテクチャ全体像

```
┌─────────────────────────────────────────────────────────┐
│                   Presentation Layer                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │ Endpoints   │  │ Middleware  │  │ Schemas     │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
└─────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────┐
│                  Application Layer                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │ Commands    │  │ Queries     │  │ Use Cases   │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
└─────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────┐
│                    Domain Layer                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │ Entities    │  │ Services    │  │ Ports       │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
└─────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────┐
│                Infrastructure Layer                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │ Repository  │  │ Database    │  │ External    │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
└─────────────────────────────────────────────────────────┘
```

---

## 🔄 Clean Architecture の原則

<div class="highlight">

### 依存性逆転の原則 (Dependency Inversion)
- **内側の層は外側の層を知らない**
- **抽象に依存し、具象に依存しない**
- **ドメインロジックの独立性を保つ**

</div>

<div class="columns">
<div class="column">

### ✅ 良い例
```python
# Domain Layer
class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo  # 抽象に依存
```

</div>
<div class="column">

### ❌ 悪い例
```python
# Domain Layer
class UserService:
    def __init__(self):
        self.repo = SQLUserRepository()  # 具象に依存
```

</div>
</div>

---

## 📁 ディレクトリ構造とレイヤー責任

<div class="columns">
<div class="column">

```
app/
├── api/           # Presentation
│   └── endpoints.py
├── usecase/       # Application
│   ├── command/
│   └── query/
├── domain/        # Domain
│   ├── entities.py
│   └── services.py
├── ports/         # Abstractions
│   └── repositories.py
├── infra/         # Infrastructure
│   └── repository_impl.py
└── deps/          # DI Container
    └── factories/
```

</div>
<div class="column">

### レイヤー責任

**Domain**: ビジネスルール・エンティティ
**Application**: ユースケース・オーケストレーション
**Presentation**: HTTP・バリデーション
**Infrastructure**: 外部システム・永続化

</div>
</div>

---

## 🎯 CQRS パターン実装

<div class="highlight">

### Command Query Responsibility Segregation
**書き込み操作と読み取り操作を明確に分離**

</div>

<div class="columns">
<div class="column">

### Commands (書き込み)
```python
class CreateUserUseCase:
    def __init__(self, 
                 repo: UserRepository,
                 service: UserService):
        self.repo = repo
        self.service = service
    
    def execute(self, request: UserCreateRequest) -> User:
        # ビジネスルール検証
        self.service.validate_email_uniqueness(
            request.email)
        
        # エンティティ作成
        user = User(...)
        return self.repo.create(user)
```

</div>
<div class="column">

### Queries (読み取り)
```python
class GetUsersUseCase:
    def __init__(self, repo: UserRepository):
        self.repo = repo
    
    def execute(self, query: UsersQuery) -> tuple[list[User], int]:
        # フィルタリング・ページネーション
        return self.repo.find_all(
            name_filter=query.name,
            min_age=query.min_age,
            max_age=query.max_age,
            limit=query.limit,
            offset=query.offset
        )
```

</div>
</div>

---

## 🔧 FastAPI 依存性注入システム

### なぜ DI が必要なのか？

<div class="highlight">

### 🎯 DI の嬉しいポイント
- **テスタビリティ**: モックオブジェクトの注入が簡単
- **再利用性**: 同じロジックを複数のエンドポイントで共有
- **保守性**: 依存関係の変更が局所化される
- **型安全性**: FastAPIが自動的に型チェックとバリデーション

</div>

---

## 💡 FastAPI DI の何ができるのか

<div class="columns">
<div class="column">

### 自動実行される処理
- **バリデーション**: 自動的な入力検証
- **型変換**: 文字列→数値等の自動変換
- **エラーハンドリング**: 失敗時の自動エラーレスポンス
- **キャッシュ**: 同一リクエスト内での結果キャッシュ

</div>
<div class="column">

### 依存関係の管理
- **階層的依存**: 依存が依存を持つ構造
- **スコープ管理**: リクエスト/セッション単位
- **条件分岐**: 認証状態による動的な依存
- **オーバーライド**: テスト時の依存差し替え

</div>
</div>

---

## 🧩 Depends の詳細解説

### 基本的な使い方

```python
from typing import Annotated
from fastapi import Depends

# ✅ Python 3.9+ 推奨記法
async def get_users(
    query: Annotated[UsersQuery, Depends()],
    usecase: Annotated[GetUsersUseCase, Depends(get_users_usecase)],
) -> UserListResponse:
    users, total = usecase.execute(query)
    return UserListResponse(...)

# ❌ 非推奨記法  
async def get_users_old(
    query: UsersQuery = Depends(),
    usecase: GetUsersUseCase = Depends(get_users_usecase),
):
    pass
```

---

## 🔍 Depends の動作原理

### 1. 自動バリデーション

```python
class UsersQuery(BaseModel):
    name: str | None = None
    min_age: int | None = Field(None, ge=0)
    max_age: int | None = Field(None, le=120)
    limit: int = Field(10, ge=1, le=100)
    offset: int = Field(0, ge=0)

# FastAPIが自動実行
async def get_users(
    query: Annotated[UsersQuery, Depends()],  # ← 自動バリデーション！
):
    # クエリパラメータが自動的にUsersQueryオブジェクトに変換
    # バリデーションエラーは自動的に422レスポンス
    pass
```

---

## 🔗 階層的依存関係の構築

### 依存の連鎖でクリーンアーキテクチャを実現

<div class="highlight">

### 🎯 依存関係の流れ
- **Database** → **Repository** → **UseCase** → **Endpoint**
- **自動解決**: FastAPIが依存関係を自動的に解決
- **シングルトン**: 同一リクエスト内では同じインスタンス

</div>

```python
# DB → Repository → UseCase → Endpoint
def get_database() -> Database:
    return Database()

def get_repository(db: Annotated[Database, Depends(get_database)]) -> Repository:
    return Repository(db)

def get_usecase( repo: Annotated[Repository, Depends(get_repository)]) -> UseCase:
    return UseCase(repo)

async def endpoint(usecase: Annotated[UseCase, Depends(get_usecase)]):
    return usecase.execute()
```

---

## 🚀 DI の高度な活用パターン

### 条件付き依存関係

```python
def get_current_user(request: Request) -> User | None:
    token = request.headers.get("Authorization")
    if token:
        return decode_jwt_token(token)
    return None

def get_authenticated_user(
    user: Annotated[User | None, Depends(get_current_user)]
) -> User:
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user

# 認証が必要なエンドポイント
async def protected_endpoint(
    user: Annotated[User, Depends(get_authenticated_user)]
):
    return {"message": f"Hello, {user.name}!"}
```

---

## ⚡ FastAPI DI の自動キャッシュ機能

### 同一リクエスト内での依存キャッシュ

<div class="highlight">

### 🎯 キャッシュの仕組み
- **同一リクエスト内**: 一度実行された依存は結果がキャッシュされる
- **重複実行防止**: 複数のエンドポイントが同じ依存を使っても1回だけ実行
- **パフォーマンス向上**: 重い処理（DB接続、外部API呼び出し）の最適化

</div>

```python
def expensive_computation():
    print("重い計算実行中...")  # デバッグ用
    time.sleep(1)  # 1秒の重い処理をシミュレート
    return "expensive_result"

# 複数の場所で使用されても1回だけ実行される
async def endpoint1(result: Annotated[str, Depends(expensive_computation)]):
    return {"endpoint1": result}

async def endpoint2(result: Annotated[str, Depends(expensive_computation)]):
    return {"endpoint2": result}

# 同じリクエスト内なら expensive_computation は1回だけ実行
```

---

## 🏭 Factory Pattern for DI

<div class="columns">
<div class="column">

### Repository Factory
```python
# Singleton Pattern
_database: InMemoryDatabase | None = None
_user_repository: InMemoryUserRepository | None = None

def get_database() -> InMemoryDatabase:
    global _database
    if _database is None:
        _database = InMemoryDatabase()
    return _database

def get_user_repository() -> InMemoryUserRepository:
    global _user_repository
    if _user_repository is None:
        _user_repository = InMemoryUserRepository(
            get_database())
    return _user_repository
```

</div>
<div class="column">

### UseCase Factory
```python
def get_users_usecase(
    repo: Annotated[InMemoryUserRepository, 
                   Depends(get_user_repository)]
) -> GetUsersUseCase:
    return GetUsersUseCase(repo)

def get_create_user_usecase(
    repo: Annotated[InMemoryUserRepository,
                   Depends(get_user_repository)],
    service: Annotated[UserService, 
                      Depends(get_user_service)]
) -> CreateUserUseCase:
    return CreateUserUseCase(repo, service)
```

</div>
</div>

---

## 🛡️ ミドルウェアスタック設計

### セキュリティファーストアプローチ

```python
# main.py - ミドルウェア登録順序が重要
app.add_middleware(SecurityHeadersMiddleware)    # 1. セキュリティヘッダー
app.add_middleware(APIKeyAuthMiddleware)         # 2. 認証
app.add_middleware(RequestLoggingMiddleware)     # 3. ログ記録
app.add_middleware(                              # 4. CORS
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

<div class="highlight">

**処理順序**: リクエスト時は上から下、レスポンス時は下から上

</div>

---

## 🔐 認証ミドルウェア実装

```python
class APIKeyAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # パブリックエンドポイントのバイパス
        if request.url.path in ["/", "/docs", "/redoc", "/openapi.json"] or \
           request.url.path.endswith("/health"):
            return await call_next(request)
        
        # API Key検証
        api_key = request.headers.get(settings.AUTH_HEADER_NAME)
        
        if not api_key:
            return JSONResponse(
                status_code=401,
                content={
                    "message": f"Missing header: {settings.AUTH_HEADER_NAME}",
                    "code": "missing_api_key"
                }
            )
        
        if api_key != settings.AUTH_HEADER_VALUE:
            return JSONResponse(
                status_code=401,
                content={"message": "Invalid API key", "code": "invalid_api_key"}
            )
        
        return await call_next(request)
```

---

## 📊 リクエスト処理ミドルウェア

<div class="columns">
<div class="column">

### ログ記録・メトリクス
```python
class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        logger.info(f"START [{request_id}] {request.method}")
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            logger.info(f"END [{request_id}] {response.status_code} "
                       f"- {process_time:.3f}s")
            
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
        except Exception as e:
            # エラー処理...
```

</div>
<div class="column">

### セキュリティヘッダー
```python
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request,
                      call_next: Callable) -> Response:
        response = await call_next(request)
        
        # OWASP推奨セキュリティヘッダー
        response.headers.update({
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY", 
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": 
                "max-age=31536000; includeSubDomains",
            "Referrer-Policy": 
                "strict-origin-when-cross-origin"
        })
        
        return response
```

</div>
</div>

---

## 🚨 構造化エラーハンドリング

### 階層的例外設計

```python
class CustomHTTPException(HTTPException):
    def __init__(self, status_code: int, message: str, code: str, detail: str | None = None):
        self.message = message
        self.code = code
        self.detail = detail
        super().__init__(status_code=status_code, detail=detail)

# 特定エラー型
class AuthenticationError(CustomHTTPException):
    def __init__(self, message: str = "認証に失敗しました", detail: str | None = None):
        super().__init__(status_code=401, message=message, code="AUTH_001", detail=detail)

class ValidationErrorException(CustomHTTPException):
    def __init__(self, message: str = "バリデーションエラーが発生しました", detail: str | None = None):
        super().__init__(status_code=422, message=message, code="VALIDATION_001", detail=detail)
```

---

## 🎯 例外ハンドラー登録

```python
# main.py
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(CustomHTTPException, custom_http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# エラーハンドラー実装
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error_details = []
    for error in exc.errors():
        field_name = " -> ".join(str(loc) for loc in error["loc"])
        error_details.append({
            "field": field_name,
            "message": error["msg"],
            "input_value": error.get("input", "N/A")
        })
    
    return JSONResponse(
        status_code=422,
        content={
            "message": "バリデーションエラーが発生しました",
            "code": "VALIDATION_001", 
            "errors": error_details
        }
    )
```

---

## 🧪 DI を活用したテスト戦略

### DIオーバーライドの威力

<div class="highlight">

### テストでの依存差し替え
- **本番**: DB、外部API、重い処理
- **テスト**: モック、インメモリ、軽量処理  
- **自動切り替え**: テスト実行時だけ差し替え

</div>

<div class="columns">
<div class="column">

### テストフィクスチャ
```python
@pytest.fixture
def client(test_repo: InMemoryUserRepository):
    def get_test_repo():
        return test_repo
    # 依存を差し替え
    app.dependency_overrides[get_user_repository] = get_test_repo
    with TestClient(app) as client:
        yield client
    
    app.dependency_overrides.clear()
```

</div>
<div class="column">

### テストケース
```python
def test_create_user(client: TestClient, auth_headers):
    response = client.post(
        "/api/v1/users",
        json={"name": "テスト", "email": "test@example.com", "age": 25},
        headers=auth_headers
    )
    
    assert response.status_code == 201
    assert response.json()["user"]["name"] == "テスト"
```

</div>
</div>

---

## ⚡ パフォーマンス最適化

### DI のベストプラクティス

<div class="highlight">

### シングルトンパターンの活用
- **重いオブジェクトは一度だけ生成**
- **データベース接続・リポジトリインスタンス**
- **メモリ効率とパフォーマンスの向上**

</div>

```python
# ✅ 推奨: Singleton
_user_repository: InMemoryUserRepository | None = None

def get_user_repository() -> InMemoryUserRepository:
    global _user_repository
    if _user_repository is None:
        _user_repository = InMemoryUserRepository(get_database())
    return _user_repository

# ❌ 非推奨: 毎回新しいインスタンス
def get_user_repository_bad() -> InMemoryUserRepository:
    return InMemoryUserRepository(get_database())  # 毎回作成
```

---

## 🎨 アーキテクチャの利点

<div class="columns">
<div class="column">

### 🔧 保守性
- **関心事の分離**
- **明確な責任境界**
- **テスタブルな設計**

### 🚀 拡張性  
- **新機能の追加が容易**
- **実装の交換可能性**
- **水平スケーリング対応**

</div>
<div class="column">

### 🛡️ 堅牢性
- **エラー処理の一元化**
- **セキュリティレイヤー**
- **ログ・監視の統合**

### 👥 チーム開発
- **コード品質の統一**
- **責任範囲の明確化**
- **レビューしやすい構造**

</div>
</div>

---

## 📈 今後の拡張ポイント

<div class="columns">
<div class="column">

### 認証・認可の強化
- JWT認証への移行
- ロールベースアクセス制御
- OAuth 2.0 / OpenID Connect

### パフォーマンス最適化
- Redis キャッシュ層
- データベースクエリ最適化
- 非同期処理の活用

</div>
<div class="column">

### 運用・監視の充実
- メトリクス収集 (Prometheus)
- 分散トレーシング (Jaeger)
- 構造化ログ (ELK Stack)

### インフラ対応
- Kubernetes デプロイメント
- CI/CD パイプライン
- コンテナ最適化

</div>
</div>

---

## 🎯 まとめ

<div class="highlight">

### Clean Architecture + FastAPI = 🚀

**企業レベルの品質とスケーラビリティを実現**

</div>

### Key Takeaways

1. **依存性逆転の原則**でドメインロジックを保護
2. **ミドルウェアスタック**でクロスカッティングな関心事を処理
3. **Factory Pattern**で DI を効率的に管理
4. **構造化エラーハンドリング**で堅牢性を確保
5. **テスト駆動開発**で品質を保証

---

## 📚 参考資料・Next Steps

### アーキテクチャ学習
- Clean Architecture (Robert C. Martin)
- Hexagonal Architecture (Alistair Cockburn)
- Domain-Driven Design (Eric Evans)

### FastAPI 深掘り
- [FastAPI公式ドキュメント](https://fastapi.tiangolo.com/)
- [Dependency Injection詳解](https://fastapi.tiangolo.com/tutorial/dependencies/)
- [Middleware Guide](https://fastapi.tiangolo.com/tutorial/middleware/)

### 実装確認
```bash
# このプロジェクトを試してみる
git clone https://github.com/liviz-lab/demo-claude-code.git
cd demo-claude-code
uv sync
uv run pytest
uv run uvicorn main:app --reload
```

**Thank you for your attention! 🎉**
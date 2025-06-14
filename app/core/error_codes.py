"""エラーコードとメッセージの定義"""

# 認証エラー
AUTH_ERROR_CODE = "AUTH_001"
AUTH_ERROR_MESSAGE = "認証に失敗しました"

# バリデーションエラー
VALIDATION_ERROR_CODE = "VAL_001"
VALIDATION_ERROR_MESSAGE = "入力値にエラーがあります"

EMAIL_DUPLICATE_CODE = "VAL_002"
EMAIL_DUPLICATE_MESSAGE = "このメールアドレスは既に使用されています"

REQUIRED_FIELD_CODE = "VAL_003"
REQUIRED_FIELD_MESSAGE = "必須項目が入力されていません"

# リソースエラー
NOT_FOUND_CODE = "RES_001"
NOT_FOUND_MESSAGE = "指定されたリソースが見つかりません"

USER_NOT_FOUND_CODE = "RES_002"
USER_NOT_FOUND_MESSAGE = "ユーザーが見つかりません"

# システムエラー
INTERNAL_ERROR_CODE = "SYS_001"
INTERNAL_ERROR_MESSAGE = "システム内部でエラーが発生しました"

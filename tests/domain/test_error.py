from typing import Any
from unittest.mock import Mock

import pytest
from fastapi import Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, ValidationError

from app.core.error import (
    AuthenticationError,
    CustomHTTPException,
    EmailDuplicateError,
    NotFoundError,
    UserNotFoundError,
    ValidationErrorException,
    convert_validation_error_to_details,
    custom_http_exception_handler,
    general_exception_handler,
    validation_exception_handler,
)
from app.core.error_codes import (
    AUTH_ERROR_CODE,
    AUTH_ERROR_MESSAGE,
    EMAIL_DUPLICATE_CODE,
    EMAIL_DUPLICATE_MESSAGE,
    INTERNAL_ERROR_CODE,
    INTERNAL_ERROR_MESSAGE,
    NOT_FOUND_CODE,
    NOT_FOUND_MESSAGE,
    USER_NOT_FOUND_CODE,
    USER_NOT_FOUND_MESSAGE,
    VALIDATION_ERROR_CODE,
    VALIDATION_ERROR_MESSAGE,
)


class TestCustomExceptions:
    """カスタム例外のテスト"""

    @pytest.mark.unit
    def test_custom_http_exception(self) -> None:
        """CustomHTTPException基本テスト"""
        exc = CustomHTTPException(status_code=400, code="TEST_001", message="テストエラー", detail="詳細情報")

        assert exc.status_code == 400
        assert exc.code == "TEST_001"
        assert exc.message == "テストエラー"
        assert exc.detail == "詳細情報"

    @pytest.mark.unit
    def test_authentication_error(self) -> None:
        """AuthenticationErrorテスト"""
        exc = AuthenticationError(message="カスタム認証エラー", detail="詳細情報")

        assert exc.status_code == 401
        assert exc.code == AUTH_ERROR_CODE
        assert exc.message == "カスタム認証エラー"
        assert exc.detail == "詳細情報"

    @pytest.mark.unit
    def test_authentication_error_default_message(self) -> None:
        """AuthenticationErrorデフォルトメッセージテスト"""
        exc = AuthenticationError()

        assert exc.status_code == 401
        assert exc.code == AUTH_ERROR_CODE
        assert exc.message == AUTH_ERROR_MESSAGE
        assert exc.detail == AUTH_ERROR_MESSAGE

    @pytest.mark.unit
    def test_not_found_error(self) -> None:
        """NotFoundErrorテスト"""
        exc = NotFoundError(message="カスタムリソースが見つかりません", detail="詳細情報")

        assert exc.status_code == 404
        assert exc.code == NOT_FOUND_CODE
        assert exc.message == "カスタムリソースが見つかりません"
        assert exc.detail == "詳細情報"

    @pytest.mark.unit
    def test_not_found_error_default_message(self) -> None:
        """NotFoundErrorデフォルトメッセージテスト"""
        exc = NotFoundError()

        assert exc.status_code == 404
        assert exc.code == NOT_FOUND_CODE
        assert exc.message == NOT_FOUND_MESSAGE
        assert exc.detail == NOT_FOUND_MESSAGE

    @pytest.mark.unit
    def test_user_not_found_error(self) -> None:
        """UserNotFoundErrorテスト"""
        exc = UserNotFoundError(123)

        assert exc.status_code == 404
        assert exc.code == USER_NOT_FOUND_CODE
        assert exc.message == USER_NOT_FOUND_MESSAGE
        assert exc.detail == "ユーザーID: 123"

    @pytest.mark.unit
    def test_validation_error_exception(self) -> None:
        """ValidationErrorExceptionテスト"""
        exc = ValidationErrorException(message="カスタムバリデーションエラー", detail="詳細情報")

        assert exc.status_code == 422
        assert exc.code == VALIDATION_ERROR_CODE
        assert exc.message == "カスタムバリデーションエラー"
        assert exc.detail == "詳細情報"

    @pytest.mark.unit
    def test_validation_error_exception_default_message(self) -> None:
        """ValidationErrorExceptionデフォルトメッセージテスト"""
        exc = ValidationErrorException()

        assert exc.status_code == 422
        assert exc.code == VALIDATION_ERROR_CODE
        assert exc.message == VALIDATION_ERROR_MESSAGE
        assert exc.detail == VALIDATION_ERROR_MESSAGE

    @pytest.mark.unit
    def test_email_duplicate_error(self) -> None:
        """EmailDuplicateErrorテスト"""
        exc = EmailDuplicateError("test@example.com")

        assert exc.status_code == 422
        assert exc.code == EMAIL_DUPLICATE_CODE
        assert exc.message == EMAIL_DUPLICATE_MESSAGE
        assert exc.detail == "メールアドレス: test@example.com"


class TestValidationErrorConversion:
    """バリデーションエラー変換のテスト"""

    @pytest.mark.unit
    def test_convert_pydantic_validation_error(self) -> None:
        """Pydantic ValidationErrorの変換テスト"""

        class TestModel(BaseModel):
            name: str = Field(..., min_length=1)
            age: int = Field(..., ge=0)

        try:
            TestModel(name="", age=-1)
        except ValidationError as e:
            details = convert_validation_error_to_details(e)

            assert len(details) == 2
            assert all(hasattr(detail, "loc") for detail in details)
            assert all(hasattr(detail, "msg") for detail in details)
            assert all(hasattr(detail, "type") for detail in details)

    @pytest.mark.unit
    def test_convert_request_validation_error(self) -> None:
        """RequestValidationErrorの変換テスト"""
        # RequestValidationErrorのモックを作成
        error_data: list[dict[str, Any]] = [
            {"loc": ("body", "name"), "msg": "field required", "type": "value_error.missing"},
            {
                "loc": ("body", "age"),
                "msg": "ensure this value is greater than or equal to 0",
                "type": "value_error.number.not_ge",
                "ctx": {"limit_value": 0},
            },
        ]

        class MockRequestValidationError:
            def errors(self) -> list[dict[str, Any]]:
                return error_data

        mock_error = MockRequestValidationError()
        details = convert_validation_error_to_details(mock_error)

        assert len(details) == 2
        assert details[0].loc == ["body", "name"]
        assert details[0].msg == "field required"
        assert details[0].type == "value_error.missing"
        assert details[1].ctx == {"limit_value": 0}


class TestExceptionHandlers:
    """例外ハンドラーのテスト"""

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_validation_exception_handler(self) -> None:
        """バリデーション例外ハンドラーテスト"""
        # リクエストモック
        request = Mock(spec=Request)

        # RequestValidationErrorモック
        error_data: list[dict[str, Any]] = [{"loc": ("body", "name"), "msg": "field required", "type": "value_error.missing"}]

        class MockRequestValidationError:
            def errors(self) -> list[dict[str, Any]]:
                return error_data

        exc = MockRequestValidationError()

        response = await validation_exception_handler(request, exc)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 422

        # レスポンスの内容を確認
        import json

        content = json.loads(response.body.decode())
        assert content["code"] == VALIDATION_ERROR_CODE
        assert content["message"] == "リクエストのバリデーションに失敗しました"
        assert content["detail"] == "必須項目が不足しています: body -> name"
        assert "details" in content

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_custom_http_exception_handler_auth_error(self) -> None:
        """認証エラーハンドラーテスト"""
        request = Mock(spec=Request)
        exc = AuthenticationError("認証に失敗しました")

        response = await custom_http_exception_handler(request, exc)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 401

        import json

        content = json.loads(response.body.decode())
        assert content["code"] == AUTH_ERROR_CODE
        assert content["message"] == "認証に失敗しました"

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_custom_http_exception_handler_not_found(self) -> None:
        """NotFoundエラーハンドラーテスト"""
        request = Mock(spec=Request)
        exc = NotFoundError("リソースが見つかりません")

        response = await custom_http_exception_handler(request, exc)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 404

        import json

        content = json.loads(response.body.decode())
        assert content["code"] == NOT_FOUND_CODE
        assert content["message"] == "リソースが見つかりません"

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_custom_http_exception_handler_validation_error(self) -> None:
        """バリデーションエラーハンドラーテスト"""
        request = Mock(spec=Request)
        exc = ValidationErrorException(message="バリデーションエラー", detail="詳細情報")

        response = await custom_http_exception_handler(request, exc)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 422

        import json

        content = json.loads(response.body.decode())
        assert content["code"] == VALIDATION_ERROR_CODE
        assert content["message"] == "バリデーションエラー"
        assert content["detail"] == "詳細情報"

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_custom_http_exception_handler_generic(self) -> None:
        """汎用カスタム例外ハンドラーテスト"""
        request = Mock(spec=Request)
        exc = CustomHTTPException(status_code=400, code="CUSTOM_001", message="カスタムエラー")

        response = await custom_http_exception_handler(request, exc)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 400

        import json

        content = json.loads(response.body.decode())
        assert content["code"] == "CUSTOM_001"
        assert content["message"] == "カスタムエラー"

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_general_exception_handler(self) -> None:
        """一般例外ハンドラーテスト"""
        request = Mock(spec=Request)
        exc = Exception("予期しないエラー")

        response = await general_exception_handler(request, exc)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 500

        import json

        content = json.loads(response.body.decode())
        assert content["code"] == INTERNAL_ERROR_CODE
        assert content["message"] == INTERNAL_ERROR_MESSAGE
        assert "Exception: 予期しないエラー" in content["detail"]


class TestErrorIntegration:
    """エラーハンドリング統合テスト"""

    @pytest.mark.integration
    def test_error_response_format_consistency(self) -> None:
        """エラーレスポンス形式の一貫性テスト"""
        errors = [
            AuthenticationError("認証エラー"),
            NotFoundError("リソースなし"),
            ValidationErrorException("バリデーションエラー"),
            CustomHTTPException(400, "CUSTOM_001", "カスタムエラー"),
        ]

        for error in errors:
            assert hasattr(error, "status_code")
            assert hasattr(error, "code")
            assert hasattr(error, "message")
            assert isinstance(error.status_code, int)
            assert isinstance(error.code, str)
            assert isinstance(error.message, str)

    @pytest.mark.integration
    def test_error_inheritance_chain(self) -> None:
        """エラークラス継承チェーンテスト"""
        auth_error = AuthenticationError()
        not_found_error = NotFoundError()
        validation_error = ValidationErrorException()

        assert isinstance(auth_error, CustomHTTPException)
        assert isinstance(not_found_error, CustomHTTPException)
        assert isinstance(validation_error, CustomHTTPException)

        # HTTPExceptionも継承している
        from fastapi import HTTPException

        assert isinstance(auth_error, HTTPException)
        assert isinstance(not_found_error, HTTPException)
        assert isinstance(validation_error, HTTPException)

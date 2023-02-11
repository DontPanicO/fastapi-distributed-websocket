__all__ = ('WebSocketOAuth2PasswordBearer',)

from fastapi import WebSocket, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.security.utils import get_authorization_scheme_param


class WebSocketOAuth2PasswordBearer(OAuth2PasswordBearer):
    def __init__(
        self,
        token_url: str,
        scheme_name: str | None = None,
        scopes: dict[str, str] | None = None,
        description: str | None = None,
        auto_error: bool = True,
    ) -> None:
        super().__init__(
            token_url,
            scheme_name,
            scopes,
            description,
            auto_error,
        )

    async def __call__(self, websocket: WebSocket) -> str | None:
        authorization: str = websocket.headers.get('Authorization')
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != 'bearer':
            if self.auto_error:
                await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            else:
                return None
        return param

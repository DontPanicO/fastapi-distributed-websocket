__all__ = ['WebSocketOAuth2PasswordBearer']

from typing import Optional, Any, NoReturn

from fastapi import WebSocket, status
from fastapi.security.utils import get_authorization_scheme_param
from fastapi.security import OAuth2PasswordBearer


class WebSocketOAuth2PasswordBearer(OAuth2PasswordBearer):
    def __init__(
        self,
        token_url: str,
        scheme_name: Optional[str] = None,
        scopes: Optional[dict[str, str]] = None,
        description: Optional[str] = None,
        auto_error: bool = True,
    ) -> NoReturn:
        super().__init__(
            token_url,
            scheme_name,
            scopes,
            description,
            auto_error,
        )

    async def __call__(self, websocket: WebSocket) -> Optional[str]:
        authorization: str = websocket.headers.get('Authorization')
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != 'bearer':
            if self.auto_error:
                await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            else:
                return None
        return param

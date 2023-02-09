import pytest

from distributed_websocket._decorators import handle, ahandle


def test_handle():
    def _exc_handler(exc: Exception) -> None:
        return f'exc: {exc}'

    @handle(RuntimeError, _exc_handler)
    def raise_error():
        raise RuntimeError('test')

    assert raise_error() == 'exc: test'


@pytest.mark.asyncio
async def test_ahandle_async_async():
    async def _exc_handler(exc: Exception) -> None:
        return f'exc: {exc}'

    @ahandle(RuntimeError, _exc_handler)
    async def raise_error():
        raise RuntimeError('test')

    assert await raise_error() == 'exc: test'


@pytest.mark.asyncio
async def test_ahandle_async_sync():
    async def _exc_handler(exc: Exception) -> None:
        return f'exc: {exc}'

    @ahandle(RuntimeError, _exc_handler)
    def raise_error():
        raise RuntimeError('test')

    assert await raise_error() == 'exc: test'

from starlette.datastructures import MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send


class ClientCacheMiddleware:
    def __init__(self, app: ASGIApp, max_age: int = 60) -> None:
        self.app = app
        self.max_age = max_age

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def send_wrapper(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = MutableHeaders(scope=message)
                headers["Cache-Control"] = f"public, max-age={self.max_age}"

            await send(message)

        await self.app(scope, receive, send_wrapper)

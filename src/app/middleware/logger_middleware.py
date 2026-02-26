from starlette.types import ASGIApp, Receive, Scope, Send


class LoggerMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        # Logic for request_id or pre-logging goes here

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                # message["status"] contains the status code
                # Perform your logging here
                pass
            await send(message)

        await self.app(scope, receive, send_wrapper)

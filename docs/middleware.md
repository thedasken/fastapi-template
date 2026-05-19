# Middleware

Prefer pure ASGI middleware for custom middleware in this template. Avoid
subclassing `BaseHTTPMiddleware`.

`BaseHTTPMiddleware` can read or buffer the full response before passing it back
to the client. That behavior may block `StreamingResponse` responses and can
interfere with the asynchronous flow of the API. This is especially easy to hit
when middleware inspects request or response bodies.

More context: https://stackoverflow.com/questions/68830274/blocked-code-while-using-middleware-and-dependency-injections-to-log-requests-in

Use a pure ASGI middleware instead. For example, a response logger can wrap the
`send` callable and inspect messages without consuming the response:

```python
from starlette.types import ASGIApp, Receive, Send, Message


class LogResponseMDW:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope, receive, send):
        async def send_wrapper(message: Message):
            # Inspect or log the message here without consuming it.
            # For example, log the body when message["type"] == "http.response.body".
            await send(message)

        await self.app(scope, receive, send_wrapper)
```

Register it like any other middleware:

```python
app.add_middleware(LogResponseMDW)
```

Recommendation: always implement custom middleware as pure ASGI middleware in
this template rather than inheriting from `BaseHTTPMiddleware`.

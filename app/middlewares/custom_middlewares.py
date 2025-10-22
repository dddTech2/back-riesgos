# Example of a custom middleware
#
# from starlette.middleware.base import BaseHTTPMiddleware
# from fastapi import Request, Response
#
# class ExampleMiddleware(BaseHTTPMiddleware):
#     async def dispatch(self, request: Request, call_next) -> Response:
#         # Do something before the request is handled
#         response = await call_next(request)
#         # Do something after the request is handled
#         return response
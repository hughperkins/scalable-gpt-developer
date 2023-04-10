import os
from aiohttp import web
from aiohttp.web import FileResponse, RouteTableDef
import handlers
import middlewares


app = web.Application(middlewares=[middlewares.cors_middleware])
routes = RouteTableDef()


@routes.post('/chat')
async def chat(request: web.Request) -> web.Response:
    return await handlers.chat_handler(request)

app.add_routes(routes)
app.router.add_get('/', lambda _: FileResponse('./static/index.html'))
app.router.add_static('/static', './static')

if __name__ == '__main__':
    web.run_app(app, host='localhost', port=8080)

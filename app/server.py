import os
import aiohttp.web
from aiohttp import web
from chat_handler import chat_handler

app = aiohttp.web.Application()
app.router.add_post('/chat', chat_handler)

app.router.add_get('/', lambda _: web.FileResponse('./static/index.html'))
app.router.add_static('/static', './static')

async def on_prepare(request, response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'POST'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'

app.on_response_prepare.append(on_prepare)

if __name__ == '__main__':
    aiohttp.web.run_app(app, host='localhost', port=8080)
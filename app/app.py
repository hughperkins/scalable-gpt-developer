import os
from aiohttp import web
from aiohttp.web_middlewares import normalize_path_middleware
from aiohttp_middlewares import cors_middleware
from handlers.chat_handler import chat_handler


async def create_app() -> web.Application:
    app = web.Application(middlewares=[normalize_path_middleware(append_slash=False), cors_middleware(allow_all=True)])
    app.router.add_route('POST', '/chat', chat_handler)
    app['openai_api_key'] = os.getenv('OPENAI_API_KEY')

    return app


async def main():
    app = await create_app()
    web.run_app(app, host='0.0.0.0', port=8080)


if __name__ == '__main__':
    web.run_app(main(), host='0.0.0.0', port=8080)

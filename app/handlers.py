import os
import openai
import json
from aiohttp import web
from response_parser import parse_response

openai.api_key = os.getenv("OPENAI_API_KEY")


async def handle_chat_request(request):
    try:
        data = await request.json()
        messages = data.get('messages', [])

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages
        )

        parsed_response, files = parse_response(response)

        return web.json_response({'completion': parsed_response, 'files': files})
    except Exception as e:
        return web.json_response({'error': str(e)}, status=500)

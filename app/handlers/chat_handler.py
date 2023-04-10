from aiohttp import web
from ai_chat import get_chat_completion


async def chat_handler(request):
    data = await request.json()
    prompt = data['prompt']

    messages = [
        {
            "role": "user",
            "content": prompt
        }
    ]

    completion = get_chat_completion(model="gpt-4", messages=messages)

    return web.json_response({"completion": completion})

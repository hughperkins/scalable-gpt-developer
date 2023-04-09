import aiohttp
import openai
import json
import os
import re
from aiohttp import web
from openai_wrapper import get_completion


async def chat_handler(request):
    data = await request.json()
    prompt = data.get('prompt', '')

    try:
        completion = await get_completion(prompt)
    except Exception as e:
        raise web.HTTPBadRequest(text=f'Error generating completion: {str(e)}')

    # Separate files from the completion
    file_contents = {}
    completion_lines = completion.split('\n')

    file_pattern = r'^([a-zA-Z0-9_]+\.[a-zA-Z]+)$'
    code_block_pattern = r'^```[a-zA-Z]*$'

    i = 0
    while i < len(completion_lines):
        line = completion_lines[i].strip()

        if re.match(file_pattern, line):
            file_name = line.rstrip()
            i += 1
            if i < len(completion_lines) and re.match(code_block_pattern, completion_lines[i].strip()):
                i += 1
                file_content = ''

                while i < len(completion_lines) and not re.match(code_block_pattern, completion_lines[i].strip()):
                    file_content += completion_lines[i] + '\n'
                    i += 1

                if len(file_content) > 0:
                    file_contents[file_name] = file_content.rstrip()
            i += 1

        else:
            i += 1

    # Remove files from the completion
    filtered_completion = ''
    for line in completion_lines:
        if not re.match(file_pattern, line.strip()) and not re.match(code_block_pattern, line.strip()):
            filtered_completion += line + '\n'

    response = {
        'completion': filtered_completion.strip(),
        'files': file_contents,
    }

    return web.json_response(response)

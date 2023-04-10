import openai
import os
from typing import List, Dict


openai.api_key = os.getenv('OPENAI_API_KEY')


def get_chat_completion(model: str, messages: List[Dict[str, str]]) -> str:
    res = openai.ChatCompletion.create(
        model=model,
        messages=messages
    )

    completion = res.choices[0].message['content']

    return completion

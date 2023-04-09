import os
import openai


async def get_completion(prompt):
    openai.api_key = os.getenv('OPENAI_API_KEY')

    try:
        res = openai.ChatCompletion.create(
            model='gpt-4',
            messages=[
                {'role': 'user', 'content': prompt}
            ]
        )

        completion = res.choices[0].message.get('content', '')
        return completion
    except Exception as e:
        return 'Error: ' + str(e)
import re
from typing import Tuple, Dict


def parse_response(response: dict) -> Tuple[str, Dict[str, str]]:
    # Extract message content
    message_content = response.get('choices', [])[0].get('message', {}).get('content', '')

    # Initialize the file dictionary
    file_dict = {}

    # Search for files in the content
    file_pattern = re.compile(r'(?P<name>[\w_]+\.\w+)\n```(?:\w+\n)?(?P<content>[\s\S]+?)```')
    file_matches = list(file_pattern.finditer(message_content))

    # For each match, add the file to the file_dict
    for match in file_matches:
        name, content = match.group('name'), match.group('content')
        file_dict[name] = content

    # Remove files from content
    message_without_files = file_pattern.sub('', message_content).strip()

    return message_without_files, file_dict

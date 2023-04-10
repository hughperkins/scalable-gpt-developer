# assumes that openai api key is in env var OPENAI_API_KEY
import os
import subprocess
import openai
import argparse
from os import path
from os.path import join
import json
import shutil
import tenacity


api_spec_instructions = """api_spec description:

api_spec is a dictionary. The keys are the filepaths of
each file in the project. Each value contains the api information about that file,
sufficient that someone can write a correct implementation of that file, without
reading any other parts of the program. The format of this value is a dictionary,
which we will refer to here as api_info.

api_info has a value 'depends', that contains a list of the names of all the project files
that this file depends on directly. Do NOT include standard libraries, system libraries or
third-party libraries in 'depends' value.

The key 'exported_functions' describes any functions that are exported from the file.
It includes full details of parameter names and types, and return type.
The key 'exported_classes' desccribes any classes that are exported from the file.
The key 'web_methods' describes any http methods exported from the file, such as get or post.
The format of both the json request, and the json response, should be fully and clearly specified.
Make sure that any project filenames are not easy to confuse with external library names.
Make sure that all filepaths are relative paths, not absolute paths.
Try not to use dictionaries when specifying function and method parameters, or return types. Use classes
instead, e.g. dataclasses, or named tuples.

If a file will call a method in a second file, that method MUST be defined in the api spec of the
second file, along with parameter names and types, and the return type.

Reminder: Do NOT include standard libraries, system libraries or
third-party libraries in 'depends' value.
"""

updating_api_spec = """If you find that the api_spec is wrong, or inconsistent, or lacks detail, please add a key to
output_dict 'updated_api'. The value for this key should be another dictionary, let's call
it updated_api_info. updated_api_info should contain a key for each filename whose api you need to update,
and the value should be the full updated api_info for that file. Do not add keys for files whose api does not need
updating.
"""

file_instructions = """
If this is a python file, please ensure that mypy types are added to all method and function parameters,
and to the return type.
If this is a python file, please ensure that it is pep8-compliant.
"""

file_correctness_check = """File correctness check:
Please check the contents of the file against the api_spec, against the linter_output, for correctness.
If the file calls a function imported from another file, that function MUST be defined in the api
spec for the other file.

If the contents of the file need to be updated, please add a key {filename} to output_dict, where
the value is a string which is the complete updated implementation of {filename}.
If no changes are needed to the file do NOT add the key {filename} to output_dict.

If you are unable to write the full implementation, then make sure to update the api spec
so that you have sufficient information to complete the task; or update the api spec to break the file into
multiple smaller files.
"""

g_prompt_initial = """Task:
{task}
(End of task description)

Please divide the project into small self-contained classes or similar.

Please start by creating api_spec json document.

{api_spec_instructions}

Output only the api_spec json dictionary. Do not write any explanations.
"""


g_prompt_file = """Task:
{task}
(End of task description)

Here is a set of api specifications you wrote earlier.
{api_spec}
(end of api_spec)

{api_spec_instructions}

You are going to write the full implementation of the file {filename}.

{file_correctness_check}

{file_instructions}

Please output a json dictionary, which we will refer to as output_dict.
Add a key {filename} to output_dict, whose value is a string which is the complete implementation of {filename}.

{updating_api_spec}

Output only output_dict. Do not write explanations.
"""


g_prompt_file_update = """Task:
{task}
(End of task description)

Here is a set of api specifications you wrote earlier.
{api_spec}
(end of api_spec)

{api_spec_instructions}

Here is the current contents of {filename}:
{file_contents}
(End of file contents)

Linter output:
{linter_output}
(end of linter output)

Output:
Your output should be a json dictionary. We will refer to it here as output_dict.

{file_correctness_check}

{api_spec_instructions}

{updating_api_spec}

If you need to update the file, or the api_spec,
please add a key to the output json 'reason', where you explain what you've changed in
the file; and a key {filename} whose value is a string containing the full corrected implementation.

please add a key to output_dict 'thoughts', which is a list of your thoughts. Please think step by step about what you
need to change, and write each thought into 'thoughts' value. Please write out the thoughts key first, before any other
keys

Do not write any explanations. Only output output_dict.
"""

# If the file is completely correct, and the api_spec is sufficient to unambiguously ensure that the rest of the
# application will work fine, and only then, then please add a key 'valid' to output_dict, with the value 'true'.


@tenacity.retry(stop=tenacity.stop_after_attempt(7), wait=tenacity.wait_fixed(0.1))
def run_openai(prompt, model) -> str:
    res = openai.ChatCompletion.create(
        messages=[{'role': 'user', 'content': prompt}],
        model=model,
        max_tokens=1024,
        stream=True)
    print('assistant writes:')
    res_str = ''
    for bit_dict in res:
        bit_str = bit_dict['choices'][0]['delta'].get('content', '')
        print(bit_str, end='', flush=True)
        res_str += bit_str
    print('')
    return res_str


def load_files(base_dir: str, files: dict[str, str], rel_dir: str, exclude_dirs: list[str]) -> None:
    dir_path = join(base_dir, rel_dir)
    for filename in os.listdir(dir_path):
        _full_path = join(dir_path, filename)
        if path.isdir(_full_path):
            if filename not in exclude_dirs:
                load_files(base_dir=base_dir, files=files, rel_dir=join(rel_dir, filename), exclude_dirs=exclude_dirs)
        elif path.isfile(_full_path):
            with open(_full_path) as f:
                _contents = f.read()
            rel_filepath = join(rel_dir, filename)
            if rel_filepath.startswith('./'):
                rel_filepath = rel_filepath[2:]
            files[rel_filepath] = _contents
            print('loaded', rel_filepath)


def run_flake8(working_dir: str, rel_filepath: str) -> str:
    p = subprocess.run(['flake8', rel_filepath], cwd=working_dir, stdout=subprocess.PIPE)
    flake8_output = p.stdout.decode('utf-8')
    return flake8_output


def run(args):
    if args.wipe_working_dir:
        assert args.in_working_dir not in ['', '.', '/']
        if os.path.exists(args.in_working_dir):
            shutil.rmtree(args.in_working_dir)
    if not os.path.exists(args.in_working_dir):
        os.makedirs(args.in_working_dir)

    files = {}
    load_files(args.in_working_dir, files, '.', args.exclude_dirs)

    with open(args.in_task_file) as f:
        task = f.read()
    print('task', task)

    api_spec = None
    api_spec_filepath = os.path.join(args.in_working_dir, 'api_spec.json')
    if os.path.isfile(api_spec_filepath):
        with open(api_spec_filepath) as f:
            api_spec = json.load(f)
    if api_spec is None:
        prompt = g_prompt_initial.format(task=task, api_spec_instructions=api_spec_instructions)
        while True:
            try:
                res_str = run_openai(prompt=prompt, model=args.model)
                res_str = res_str.replace('None', 'null')
                api_spec = json.loads(res_str)
                break
            except json.decoder.JSONDecodeError as e:
                print(e)
                print('retrying file...')
        with open(api_spec_filepath, 'w') as f:
            json.dump(api_spec, f, indent=2)
            print('saved api_spec to ', api_spec_filepath)

    if api_spec is not None and args.wipe_missing_from_api_spec:
        _file_names = list(files.keys())
        for filename in _file_names:
            if filename not in api_spec and filename != 'api_spec.json':
                _filepath = join(args.in_working_dir, filename)
                os.remove(_filepath)
                print('wiped file not in api spec: ', _filepath)
                del files[filename]
    api_spec_updated = True
    while api_spec_updated:
        api_spec_updated = False
        for filename in api_spec.keys():
            print(filename)
            got_new_contents = False
            while True:
                try:
                    if filename in files:
                        if filename.endswith('.py'):
                            linter_output = run_flake8(working_dir=args.in_working_dir, rel_filepath=filename)
                        else:
                            linter_output = ''
                        prompt = g_prompt_file_update.format(
                            api_spec=api_spec, filename=filename, task=task, file_contents=files[filename],
                            linter_output=linter_output,
                            api_spec_instructions=api_spec_instructions,
                            file_correctness_check=file_correctness_check,
                            updating_api_spec=updating_api_spec)
                    else:
                        prompt = g_prompt_file.format(
                            api_spec=api_spec, filename=filename, task=task,
                            api_spec_instructions=api_spec_instructions,
                            file_correctness_check=file_correctness_check,
                            file_instructions=file_instructions,
                            updating_api_spec=updating_api_spec)
                    res_str = run_openai(prompt=prompt, model=args.model)
                    # if res_str.strip().upper() == 'VALID':
                    #     got_new_contents = False
                    #     break
                    # res_str = res_str.replace('None', 'null')
                    res_dict = json.loads(res_str)
                    # if 'valid' in res_dict:
                    #     got_new_contents = False
                    #     continue
                    if filename in res_dict:
                        got_new_contents = True
                    break
                except json.decoder.JSONDecodeError as e:
                    print(e)
                    print('retrying file...')
            if got_new_contents:
                print('got changes. processing', filename)
                files[filename] = res_dict[filename]
                assert '..' not in filename
                assert not filename.startswith('/')
                # if filename.startswith('/'):
                #     filename = filename[1:]
                _target_file_path = join(args.in_working_dir, filename)
                _target_file_parent_dir = path.dirname(_target_file_path)
                if not path.isdir(_target_file_parent_dir):
                    os.makedirs(_target_file_parent_dir)
                    print('created dir', _target_file_parent_dir)
                with open(_target_file_path, 'w') as f:
                    f.write(res_dict[filename])
                    print('wrote', _target_file_path)
            else:
                print('no change to file')
            if 'updated_api' in res_dict and len(res_dict['updated_api']) > 0:
                print('updating api spec')
                for filename, file_spec in res_dict['updated_api'].items():
                    if api_spec[filename] != file_spec:
                        api_spec[filename] = file_spec
                        api_spec_updated = True
                if api_spec_updated:
                    with open(api_spec_filepath, 'w') as f:
                        json.dump(api_spec, f, indent=2)
                        print('saved updated api_spec to ', api_spec_filepath)
                    break


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--in-task-file', type=str, default='tasks/react_app1.txt',
        help='task file to read, describing the app to create')
    parser.add_argument('--in-working-dir', type=str, default='app', help='where to write generated files to')
    parser.add_argument('--wipe-working-dir', action='store_true', help='wipe contents of --in-working-dir')
    parser.add_argument(
        '--wipe-missing-from-api-spec', action='store_true', help='wipe any files not in api_spec, and not excluded')
    parser.add_argument('--model', type=str, default='gpt-4', help='name of openai chat model')
    parser.add_argument(
        '--exclude-dirs', nargs='+', default=['__pycache__', '.git'],
        help='folders to not load files fromon app start')
    args = parser.parse_args()
    run(args)

# assumes that openai api key is in env var OPENAI_API_KEY
import os
import openai
import argparse
from os import path
from os.path import join
import json
import shutil
import tenacity


g_prompt_initial = """Task:
{task}
(End of task description)

Please divide the project into small self-contained classes or similar.

Please start by creating a json document, where the keys are the names of
each file in the program. Each value will contain the api information about that file,
sufficient that someone can write a correct implementation of that file, without
reading any other parts of the program. The format of this value is a dictionary,
which we will refer to here as api_info.
api_info has a value 'depends', that contains a list of the names of all the files
that this file depends on directly. Create any other values in api_info dictionary to
fully describe the public api of each file or class. Do not write any explanations.
"""


g_prompt_file = """Task:
{task}
(End of task description)

Here is a set of api specifications you wrote earlier. The keys are filenames, and the
values are descriptions of the api of each file. Let's call each value api_info. So,
each api_info has a key 'depends', which is a list of the filenames of all the files on which
a file depends directly, e.g. imports from.

{api_spec}
(end of api spec)

You are going to write full implementation of the file {filename}. Please output a json dictionary
with a key {filename}, and the value is a string which is the complete implementation of {filename}.
If you find that the api_spec is wrong, or inconsistent, or lacks detail, please add a key to
the output json dictionary 'updated_api'. The value for this key should be another dictionary, let's call
it updated_api_info. updated_api_info should contain a key for each filename whose api you need to update,
and the value should be the full updated api_info for that file. Do not write any explanations.

If you are unable to write the full implementation, then make sure to update the api spec, using update_api,
so that you have sufficient information to complete the task; or update update_api to break the file into
multiple smaller files.

Do not write placeholder implementations without outputing an updated update_api
"""


g_prompt_file_update = """Task:
{task}
(End of task description)

Here is a set of api specifications you wrote earlier. The keys are filenames, and the
values are descriptions of the api of each file. Let's call each value api_info. So,
each api_info has a key 'depends', which is a list of the filenames of all the files on which
a file depends directly, e.g. imports from.

{api_spec}
(end of api spec)

Here is the current contents of {filename}:
{file_contents}
(End of file contents)

Please check the contents of this file against the api_spec, and also check if it is valid.

If it is valid then please output only VALID.

If the contents of the file need to be updated, then please output a json dictionary
with a key {filename}, and the value is a string which is the complete updated implementation of {filename}.
If you find that the api_spec is wrong, or inconsistent, or lacks detail, please add a key to
the output json dictionary 'updated_api'. The value for this key should be another dictionary, let's call
it updated_api_info. updated_api_info should contain a key for each filename whose api you need to update,
and the value should be the full updated api_info for that file. Do not write any explanations.

If you are unable to write the full implementation, then make sure to update the api spec, using update_api,
so that you have sufficient information to complete the task; or update update_api to break the file into
multiple smaller files.

Do not write placeholder implementations without outputing an updated update_api
"""


@tenacity.retry(stop=tenacity.stop_after_attempt(7), wait=tenacity.wait_fixed(0.1))
def run_openai(prompt, model) -> str:
    res = openai.ChatCompletion.create(
        messages=[{'role': 'user', 'content': prompt}],
        model=model,
        max_tokens=1024,
        stream=True)
    print('')
    print('assistant writes:')
    res_str = ''
    for bit_dict in res:
        bit_str = bit_dict['choices'][0]['delta'].get('content', '')
        print(bit_str, end='', flush=True)
        res_str += bit_str
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
        prompt = g_prompt_initial.format(task=task)
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
            got_new_contents = False
            while True:
                try:
                    if filename in files:
                        prompt = g_prompt_file_update.format(
                            api_spec=api_spec, filename=filename, task=task, file_contents=files[filename])
                    else:
                        prompt = g_prompt_file.format(api_spec=api_spec, filename=filename, task=task)
                    res_str = run_openai(prompt=prompt, model=args.model)
                    if res_str.strip().upper() == 'VALID':
                        got_new_contents = False
                        break
                    res_str = res_str.replace('None', 'null')
                    res_dict = json.loads(res_str)
                    got_new_contents = True
                    break
                except json.decoder.JSONDecodeError as e:
                    print(e)
                    print('retrying file...')
            if not got_new_contents:
                print('no change => skipping')
                continue
            print('got changes. processing')
            files[filename] = res_dict[filename]
            assert '..' not in filename
            _target_file_path = join(args.in_working_dir, filename)
            _target_file_parent_dir = path.dirname(_target_file_path)
            if not path.isdir(_target_file_parent_dir):
                os.makedirs(_target_file_parent_dir)
                print('created dir', _target_file_parent_dir)
            with open(_target_file_path, 'w') as f:
                f.write(res_dict[filename])
            if 'updated_api' in res_dict and len(res_dict['updated_api']) > 0:
                print('updating api spec')
                for filename, file_spec in res_dict['updated_api'].items():
                    api_spec[filename] = file_spec
                with open(api_spec_filepath, 'w') as f:
                    json.dump(api_spec, f, indent=2)
                    print('saved api_spec to ', api_spec_filepath)
                api_spec_updated = True
                break


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--in-task-file', type=str, default='tasks/react_app1.txt',
        help='task file to read, describing the app to create')
    parser.add_argument('--in-working-dir', type=str, default='app', help='where to write generated files to')
    parser.add_argument('--wipe-working-dir', action='store_true', help='wipe contents of --in-working-dir')
    parser.add_argument('--wipe-missing-from-api-spec', action='store_true', help='wipe any files not in api_spec, and not excluded')
    parser.add_argument('--model', type=str, default='gpt-4', help='name of openai chat model')
    parser.add_argument(
        '--exclude-dirs', nargs='+', default=['__pycache__', '.git'],
        help='folders to not load files fromon app start')
    args = parser.parse_args()
    run(args)

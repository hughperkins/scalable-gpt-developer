# assumes that openai api key is in env var OPENAI_API_KEY
import os
import subprocess
from typing import Any, Dict, Optional
import openai
import argparse
from os import path
from os.path import join
import json
import shutil
import tenacity

from scalable_gpt_developer import api_spec_prompts, file_prompts, arch_prompts


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


class GptDeveloper:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.api_spec: Optional[Dict[str, Dict[str, Any]]]

    def run(self) -> None:
        if args.wipe_working_dir:
            assert args.working_dir not in ['', '.', '/']
            if os.path.exists(args.working_dir):
                shutil.rmtree(args.working_dir)
        if not os.path.exists(args.working_dir):
            os.makedirs(args.working_dir)

        self.files: Dict[str, str] = {}
        self.load_files(args.working_dir, self.files, '.', args.exclude_dirs)

        with open(args.task_file) as f:
            self.task = f.read()
        print('task', self.task)

        self.arch_spec: Optional[Dict[str, Dict[str, Any]]] = None
        self.arch_spec_filepath = os.path.join(args.working_dir, 'arch_spec.json')
        if os.path.isfile(self.arch_spec_filepath):
            with open(self.arch_spec_filepath) as f:
                self.arch_spec: Optional[Dict[str, Dict[str, Any]]] = json.load(f)
        if self.arch_spec is None:
            self.create_arch_spec()
        assert self.arch_spec is not None
        self.verify_arch_spec()

        self.api_spec: Optional[Dict[str, Dict[str, Any]]] = None
        self.api_spec_filepath = os.path.join(args.working_dir, 'api_spec.json')
        if os.path.isfile(self.api_spec_filepath):
            with open(self.api_spec_filepath) as f:
                self.api_spec: Optional[Dict[str, Dict[str, Any]]] = json.load(f)
        if self.api_spec is None:
            self.create_api_spec()
            self.verify_api_spec()
        assert self.api_spec is not None

        if self.api_spec is not None and args.wipe_missing_from_api_spec:
            _file_names = list(self.files.keys())
            for filename in _file_names:
                if filename not in self.api_spec and filename != 'api_spec.json':
                    _filepath = join(args.working_dir, filename)
                    os.remove(_filepath)
                    print('wiped file not in api spec: ', _filepath)
                    del self.files[filename]
        api_spec_updated = True
        while api_spec_updated:
            api_spec_updated = False
            for filename, filename_api_spec in self.api_spec.items():
                if args.rewrite_specific_file is not None and filename != args.rewrite_specific_file:
                    continue
                print(filename)
                got_new_contents = False
                target_file_path = join(args.working_dir, filename)
                target_file_parent_dir = path.dirname(target_file_path)
                while True:
                    try:
                        file_instructions_lang_specific = ''
                        filetype = '.' + filename.split('.')[-1].lower()
                        if filetype == '.py':
                            file_instructions_lang_specific = file_prompts.file_instructions_python
                        elif filetype in ['.js', '.jsx', '.tsx']:
                            file_instructions_lang_specific = file_prompts.file_instructions_javascript
                        if filename in self.files:
                            # existing file
                            if filename.endswith('.py'):
                                linter_output = self.run_flake8(working_dir=args.working_dir, rel_filepath=filename)
                            else:
                                linter_output = ''
                            prompt = file_prompts.prompt_update_file.format(
                                filename_api_spec=filename_api_spec,
                                filename=filename,
                                task=self.task,
                                prompt_api_spec_fail=file_prompts.prompt_api_spec_fail,
                                file_contents=self.files[filename],
                                linter_output=linter_output,
                                file_correctness_check=file_prompts.file_correctness_check,
                                file_instructions_lang_specific=file_instructions_lang_specific)
                        else:
                            # new file
                            prompt = file_prompts.prompt_create_file.format(
                                filename_api_spec=filename_api_spec,
                                filename=filename,
                                task=self.task,
                                prompt_api_spec_fail=file_prompts.prompt_api_spec_fail,
                                file_correctness_check=file_prompts.file_correctness_check,
                                file_instructions_lang_specific=file_instructions_lang_specific)
                        if args.prompt_dir is not None and args.prompt_dir != '':
                            _prompt_filepath = f'{args.prompt_dir}/{filename}.prompt.txt'
                            _prompt_parent_dir = path.dirname(_prompt_filepath)
                            if not path.exists(_prompt_parent_dir):
                                os.makedirs(_prompt_parent_dir)
                            with open(_prompt_filepath, 'w') as f:
                                f.write(prompt)
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
                    self.files[filename] = res_dict[filename]
                    assert '..' not in filename
                    assert not filename.startswith('/')
                    # if filename.startswith('/'):
                    #     filename = filename[1:]
                    if not path.isdir(target_file_parent_dir):
                        os.makedirs(target_file_parent_dir)
                        print('created dir', target_file_parent_dir)
                    with open(target_file_path, 'w') as f:
                        f.write(res_dict[filename])
                        print('wrote', target_file_path)
                else:
                    print('no change to file')
                if 'updated_api' in res_dict and len(res_dict['updated_api']) > 0:
                    print('updating api spec')
                    for filename, file_spec in res_dict['updated_api'].items():
                        if self.api_spec[filename] != file_spec:
                            self.api_spec[filename] = file_spec
                            api_spec_updated = True
                    if api_spec_updated:
                        with open(self.api_spec_filepath, 'w') as f:
                            json.dump(self.api_spec, f, indent=2)
                            print('saved updated api_spec to ', self.api_spec_filepath)
                        break

    def load_files(self, base_dir: str, files: dict[str, str], rel_dir: str, exclude_dirs: list[str]) -> None:
        dir_path = join(base_dir, rel_dir)
        for filename in os.listdir(dir_path):
            _full_path = join(dir_path, filename)
            if path.isdir(_full_path):
                if filename not in exclude_dirs:
                    self.load_files(
                        base_dir=base_dir, files=files, rel_dir=join(rel_dir, filename), exclude_dirs=exclude_dirs)
            elif path.isfile(_full_path):
                with open(_full_path) as f:
                    _contents = f.read()
                rel_filepath = join(rel_dir, filename)
                if rel_filepath.startswith('./'):
                    rel_filepath = rel_filepath[2:]
                files[rel_filepath] = _contents
                print('loaded', rel_filepath)

    def run_flake8(self, working_dir: str, rel_filepath: str) -> str:
        p = subprocess.run(['flake8', rel_filepath], cwd=working_dir, stdout=subprocess.PIPE)
        flake8_output = p.stdout.decode('utf-8')
        return flake8_output

    def create_arch_spec(self):
        prompt = arch_prompts.prompt_create_arch_spec.format(
            task=self.task, arch_spec_instructions=arch_prompts.arch_spec_instructions)
        while True:
            try:
                res_str = run_openai(prompt=prompt, model=args.model)
                res_str = res_str.replace('None', 'null')
                self.arch_spec = json.loads(res_str)
                break
            except json.decoder.JSONDecodeError as e:
                print(e)
                print('retrying file...')
        with open(self.arch_spec_filepath, 'w') as f:
            json.dump(self.arch_spec, f, indent=2)
            print('saved arch_spec to ', self.arch_spec_filepath)

    def verify_arch_spec(self):
        prompt = arch_prompts.prompt_verify_arch_spec.format(
            task=self.task, arch_spec_instructions=arch_prompts.arch_spec_instructions,
            arch_spec=self.arch_spec)
        while True:
            try:
                res_str = run_openai(prompt=prompt, model=args.model)
                res_str = res_str.replace('None', 'null')
                arch_spec_envelope = json.loads(res_str)
                break
            except json.decoder.JSONDecodeError as e:
                print(e)
                print('retrying file...')
        print(arch_spec_envelope['changes'])
        print("different?", arch_spec_envelope['updated_arch_spec'] == self.arch_spec)
        self.arch_spec = arch_spec_envelope['updated_arch_spec']
        with open(self.arch_spec_filepath, 'w') as f:
            json.dump(self.arch_spec, f, indent=2)
            print('saved updated arch_spec into ', self.arch_spec_filepath)

    def create_api_spec(self):
        prompt = api_spec_prompts.prompt_create_api_spec.format(
            task=self.task, api_spec_instructions=api_spec_prompts.api_spec_instructions)
        while True:
            try:
                res_str = run_openai(prompt=prompt, model=args.model)
                res_str = res_str.replace('None', 'null')
                self.api_spec = json.loads(res_str)
                break
            except json.decoder.JSONDecodeError as e:
                print(e)
                print('retrying file...')
        with open(self.api_spec_filepath, 'w') as f:
            json.dump(self.api_spec, f, indent=2)
            print('saved api_spec to ', self.api_spec_filepath)

    def verify_api_spec(self):
        prompt = api_spec_prompts.prompt_create_api_spec.format(
            task=self.task, api_spec_instructions=api_spec_prompts.api_spec_instructions,
            api_spec=self.api_spec)
        while True:
            try:
                res_str = run_openai(prompt=prompt, model=args.model)
                res_str = res_str.replace('None', 'null')
                api_spec_envelope = json.loads(res_str)
                break
            except json.decoder.JSONDecodeError as e:
                print(e)
                print('retrying file...')
        print(api_spec_envelope['changes'])
        print("different?", api_spec_envelope['updated_api_spec'] == self.api_spec)
        self.api_spec = api_spec_envelope['updated_api_spec']
        with open(self.api_spec_filepath, 'w') as f:
            json.dump(self.api_spec, f, indent=2)
            print('saved updated api_spec to ', self.api_spec_filepath)


def run(args):
    GptDeveloper(args).run()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--task-file', type=str, default='tasks/react_app1.txt',
        help='task file to read, describing the app to create')
    parser.add_argument('--working-dir', type=str, default='app', help='where to write generated files to')
    parser.add_argument('--prompt-dir', type=str, help='if provided, writes prompts to here')
    parser.add_argument('--wipe-working-dir', action='store_true', help='wipe contents of --in-working-dir')
    parser.add_argument(
        '--wipe-missing-from-api-spec', action='store_true', help='wipe any files not in api_spec, and not excluded')
    parser.add_argument('--model', type=str, default='gpt-4', help='name of openai chat model')
    parser.add_argument('--rewrite-specific-file', type=str, help='only rewrite a specific existing file')
    parser.add_argument(
        '--exclude-dirs', nargs='+', default=['__pycache__', '.git'],
        help='folders to not load files fromon app start')
    args = parser.parse_args()
    run(args)

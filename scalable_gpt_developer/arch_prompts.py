arch_spec_instructions = """# Architecture specifications

arch_spec is a dictionary. The keys are the filepaths of
each file in the project, e.g. a python class file, or a javascript class file.
Each value is a dictionary with the following keys.

## `description` key
Describe the goal and purpose of this file

## `uses` key
List the other files from this project that this file will directly import, call, or otherwise use.

## `used_by` key
List the other files that will directly import call or otherwise use this file.

Make sure that any names used in the project, including filenames and function names,
are not easy to confuse with external library names, or with system library names.

Make sure that all filepaths are relative paths, not absolute paths.
"""

updating_arch_spec = """If you find that the arch_spec is wrong, or inconsistent, or lacks detail, please add a key to
output_dict 'updated_arch'. The value for this key should be another dictionary, let's call
it updated_arch_info. updated_arch_info should contain a key for each filename whose architecture you need to update,
and the value should be the full updated arch_info for that file. Do not add keys for files whose api does not need
updating. If any file needs deleting, please add a key output_dict 'deleted_files', which contains a list of the
filepaths of files to delete.
"""

prompt_create_arch_spec = """Task:
{task}
(End of task description)

Please divide the project into small self-contained classes or similar.

Please start by creating arch_spec json document.

{arch_spec_instructions}

Output only the arch_spec json dictionary. Do not write any explanations.
"""

prompt_verify_arch_spec = """Here is a task we want to build an application for:
```
{task}
```

Here are instructions for building an arch_spec for this task:
{arch_spec_instructions}

Here is the existing arch_spec:
{arch_spec}

Please write out a json dict with the key "updated_arch_spec", containing the full arch_spec, correcting any mistakes.
Also add a key "changes" detailing what you have changed, if anything, and why.
Only output this json dictionary. Do not write any explanations.
"""

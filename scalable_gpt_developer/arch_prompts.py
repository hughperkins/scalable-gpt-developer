arch_spec_instructions = """# Architecture specifications

arch_spec is a dictionary. The keys are the filepaths of
each file in the project, e.g. a python class file, or a javascript class file.
Each value is a dictionary with the following keys.

## `description` key
Describe the goal and purpose of this file

## `uses` key
List the other files from this project that this file will import, call, connect with, or otherwise use,
including connecting over rpc, web, http, or other network calls.
If this file makes an http connection with another file's http endpoint, then that file should be in 'uses'.

## `used_by` key
List the other files that will import call or otherwise connect with, or use this file, including
connecting over rpc, web, http, or other network calls.
If this file advertises an http endpoint, then 'used_by' should include all client files of this endpoint.

Make sure that any names used in the project, including filenames and function names,
are not easy to confuse with external library names, or with system library names.

Make sure that all filepaths are relative paths, not absolute paths.

The graph described by each file as a node, and each uses and used_by as connections, should comprise a single
connected component. Try to ensure the graph is a directed acyclic graph, without dependency loops, if possible
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

Please write out a json dict output_dict..
First write a key "inconsistencies" detailing any inconsistencies, contradictions, or ambiguities in these
instructions or the task.
Next write a key "design decisions", containing key design decisions.
Next write a key "arch_spec", containing the full arch_spec
Output only the output_dict json dictionary. Do not write any explanations.
"""

prompt_verify_arch_spec = """Here is a task we want to build an application for:
```
{task}
```

Here are instructions for building an arch_spec for this task:
{arch_spec_instructions}

Here is the existing arch_spec:
```
{arch_spec}
```

Please write out a json dict with the key "updated_arch_spec", containing the full arch_spec, correcting any mistakes.
First write a key "inconsistencies" detailing any inconsistencies, contradictions, or ambiguities in these
instructions or the task.
Next, write a key "criticisms", whose value is a string where you write out any issues,
concerns, criticisms of the existing arch_spec.
Once you have finished writing out the "updated_arch_spec" key,
add a key "changes" detailing what you have changed, if anything, and why.
Only output this json dictionary. Do not write any explanations.
"""

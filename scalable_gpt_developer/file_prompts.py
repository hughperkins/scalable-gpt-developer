file_instructions_python = (
    """Please ensure that mypy types are added to all method and function parameters, and to the return type.
    Please ensure that it is pep8-compliant.""")

file_instructions_javascript = (
    """ ALWAYS use named exports. Always use named imports when importing
from other project files. In other words all exported functions and classes should be explicitly
exported like this:
```
export const my_func = () => {
};
```
Make sure to check this point, and state the check in your thoughts.
""")

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

prompt_api_spec_fail = (
    """If the provided api spec does not provide sufficient information for you to write the complete implementation
such that it is guaranteed to work with the other project files, then please add a key 'api_fail' to output_dict.
'api_file' should have a string value where you explain clearly, concisely, and completely, why the current api_spec is
not sufficient for you to unambigously write a correct implementation.""")

prompt_create_file = """Task:
{task}
(End of task description)

You are going to write the full implementation of the file {filename}.

Here is the api specification for {filename}:
```
{filename_api_spec}
```

{file_instructions_lang_specific}

{file_correctness_check}

Please output a json dictionary, which we will refer to as output_dict.
Add a key {filename} to output_dict, whose value is a string which is the complete implementation of {filename}.

{prompt_api_spec_fail}

Output only output_dict. Do not write explanations.
"""


prompt_update_file = """Task:
{task}
(End of task description)

Here is the api specification for {filename}:
```
{filename_api_spec}
```

Here is the current contents of {filename}:
```
{file_contents}
```

Linter output:
```
{linter_output}
```

Output:
Your output should be a json dictionary. We will refer to it here as output_dict.

{file_instructions_lang_specific}

{file_correctness_check}

Make sure to read the Task description above clearly, and ensure that {filename} will meet
the task requirements.

Please add a key {filename} to output_dict whose value is a string containing the full contents
of {filename}. If no changes
are required to the file, then write out the file exactly the same as the original. Otherwise, make any
changes required to match the task requirements, and the api spec requirements.

If you needed to update the file, please add a key to output_dict 'reason', where you explain what you've changed in
the file, and why. 

{prompt_api_spec_fail}

Do not write any explanations. Only output output_dict.
"""

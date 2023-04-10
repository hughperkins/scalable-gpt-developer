api_spec_instructions = """api_spec description:

api_spec is a dictionary. The keys are the filepaths of
each file in the project. Each value contains the api information about that file,
sufficient that someone can write a correct implementation of that file, without
reading any other parts of the program. The format of this value is a dictionary,
which we will refer to here as api_info.

'imported_functions' key
Describes any functions that are imported by the file,
from other files. Do not include functions imported from system libraries, or third-party libraries,
or built-in libraries. It includes full details of parameter names and types, and return type.
Make sure to include the full path to the function, including any packages or similar.
Do NOT include calls to system libraries, built-in libraries, or third-party libraries.
ONLY include calls to other files in this application.

'imported_classes' key
Describes any classes that are imported by the file.

'consumed_web_methods' key
Describes any http methods consumed by the file, using e.g. get or post.
The format of both the json request, and the json response, should be fully and clearly specified.

'exported_functions' key
Give the names of any exported functions. Give a brief description of each.

'exported_classes' key
Give the names of any exported classes. Give a brief description of each.

'published_web_methods' key
Describes the url and http method of any http methods published by the file.
Give a brief description of each method.

In general, try not to use dictionaries when specifying function and method parameters, or return types. Use classes
instead, e.g. dataclasses, or named tuples.

Make sure that any names used in the project, including filenames and function names,
are not easy to confuse with external library names, or with system library names.

Make sure that all filepaths are relative paths, not absolute paths.
"""

updating_api_spec = """If you find that the api_spec is wrong, or inconsistent, or lacks detail, please add a key to
output_dict 'updated_api'. The value for this key should be another dictionary, let's call
it updated_api_info. updated_api_info should contain a key for each filename whose api you need to update,
and the value should be the full updated api_info for that file. Do not add keys for files whose api does not need
updating.
"""

prompt_create_api_spec = """Task:
{task}
(End of task description)

Please divide the project into small self-contained classes or similar.

Please start by creating api_spec json document.

{api_spec_instructions}

Output only the api_spec json dictionary. Do not write any explanations.
"""

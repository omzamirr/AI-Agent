import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types

from functions.get_files_info import get_files_info, schema_get_files_info
from functions.get_file_content import get_file_content, schema_get_file_content
from functions.run_python import run_python_file, schema_run_python_file
from functions.write_file_content import write_file, schema_write_file
from config import WORKING_DIR

if len(sys.argv) <= 1:
    print("Error: prompt required")
    print("Usage: python main.py <your prompt> [--verbose]")
    sys.exit(1)

verbose = False
args = sys.argv[1:]
if "--verbose" in args:
    verbose = True
    args.remove("--verbose")

user_prompt = " ".join(args)

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

messages = [
    types.Content(role="user", parts=[types.Part(text=user_prompt)]),
]

available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_get_file_content,
        schema_run_python_file,
        schema_write_file,
    ]
)

system_prompt = """
You are a helpful AI coding agent.

When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

- List files and directories
- Read file contents
- Execute Python files with optional arguments (if no arguments are needed, use an empty list for args)
- Write or overwrite files

All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.

For example, to run tests.py, call run_python_file({'file_path': 'tests.py'}).
"""

config = types.GenerateContentConfig(
    tools=[available_functions],
    system_instruction=system_prompt
)

function_map = {
    "get_files_info": get_files_info,
    "get_file_content": get_file_content,
    "run_python_file": run_python_file,
    "write_file": write_file,
}

def call_function(function_call_part, verbose=False):
    if verbose:
        print(
            f" - Calling function: {function_call_part.name}({function_call_part.args})"
        )
    else:
        print(f" - Calling function: {function_call_part.name}")
    function_name = function_call_part.name
    if function_name not in function_map:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response=f"Unknown function: {function_name}",
                )
            ],
        )
    args = dict(function_call_part.args)
    try:
        if function_name == "run_python_file":
            file_path = args.get("file_path")
            script_args = args.get("args", [])
            function_result = run_python_file(
                WORKING_DIR, file_path, script_args
            )
        else:
            args["working_directory"] = WORKING_DIR
            function_result = function_map[function_name](**args)
    except Exception as e:
        function_result = f"Error: {e}"
    # Return the result as a string, not a dict
    return types.Content(
        role="tool",
        parts=[
            types.Part.from_function_response(
                name=function_name,
                response=function_result,
            )
        ],
    )

response = client.models.generate_content(
    model='gemini-2.0-flash-001',
    contents=messages,
    config=config,
)

if hasattr(response, "function_calls") and response.function_calls:
    function_call_results = []
    for function_call_part in response.function_calls:
        function_call_result = call_function(function_call_part, verbose=verbose)
        if (
            not function_call_result.parts
            or not hasattr(function_call_result.parts[0], "function_response")
            or not hasattr(function_call_result.parts[0].function_response, "response")
        ):
            raise RuntimeError("Fatal: No function response returned!")
        if verbose:
            print(f"-> {function_call_result.parts[0].function_response.response}")
        function_call_results.append(function_call_result)
    messages.extend(function_call_results)
    # Ask the model for a final response, now that it has the function result
    final_response = client.models.generate_content(
        model='gemini-2.0-flash-001',
        contents=messages,
        config=config,
    )
    print(final_response.candidates[0].content.parts[0].text)
else:
    print(response.candidates[0].content.parts[0].text)

sys.exit(0)
import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types

from functions.get_files_info import get_files_info
from functions.get_files_content import get_file_content
from functions.run_python import run_python_file
from functions.write_files import write_file
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

# Define schemas here (not in the function files)
schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in the specified directory along with their sizes, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="The directory to list files from, relative to the working directory. If not provided, lists files in the working directory itself.",
                default="."
            ),
        },
    ),
)

schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Reads and returns the contents of the specified file, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the file to read, relative to the working directory.",
            ),
        },
        required=["file_path"],
    ),
)

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Executes a Python file with optional arguments, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the Python file to execute, relative to the working directory.",
            ),
            "args": types.Schema(
                type=types.Type.ARRAY,
                items=types.Schema(type=types.Type.STRING),
                description="Optional list of arguments to pass to the Python file.",
                default=[],
            ),
        },
        required=["file_path"],
    ),
)

schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Writes or overwrites the specified file with the provided content, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the file to write, relative to the working directory.",
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="The content to write to the file.",
            ),
        },
        required=["file_path", "content"],
    ),
)

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
    function_name = function_call_part.name
    args = dict(function_call_part.args)

    if verbose:
        print(f"Calling function: {function_call_part.name}({function_call_part.args})")
    else:
        print(f" - Calling function: {function_call_part.name}")

    if function_name not in function_map:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response={"error": f"Unknown function: {function_name}"},
                )
            ],
        )

    try:
        if function_name == "run_python_file":
            file_path = args.get("file_path")
            script_args = args.get("args", [])
            function_result = run_python_file(WORKING_DIR, file_path, script_args)
        else:
            args["working_directory"] = WORKING_DIR
            function_result = function_map[function_name](**args)
    except Exception as e:
        function_result = f"Error: {e}"

    return types.Content(
        role="tool",
        parts=[
            types.Part.from_function_response(
                name=function_name,
                response={"result": function_result},
            )
        ],
    )

MAX_ITERATIONS = 20
iteration = 0

while iteration < MAX_ITERATIONS:
    response = client.models.generate_content(
        model='gemini-2.0-flash-001',
        contents=messages,
        config=config,
    )

    # Add all candidate contents to the conversation
    for candidate in response.candidates:
        if candidate.content is not None:
            messages.append(candidate.content)

    # Gather all function call parts from all candidates, in order
    function_call_parts = []
    for candidate in response.candidates:
        if candidate.content is not None and candidate.content.parts:
            for part in candidate.content.parts:
                if hasattr(part, "function_call") and part.function_call is not None:
                    function_call_parts.append(part.function_call)

    # If there are function calls, respond to each in order
    if function_call_parts:
        for function_call_part in function_call_parts:
            function_call_result = call_function(function_call_part, verbose=verbose)
            messages.append(function_call_result)
        iteration += 1
        continue  # Go to next iteration
    else:
    # No function call, print all text parts from all candidates and break
        for candidate in response.candidates:
            if candidate.content is not None and candidate.content.parts:
                for part in candidate.content.parts:
                    if hasattr(part, "text") and part.text:
                        print(part.text)
        break
else:
    
    print("Max iterations reached. Exiting.")

sys.exit(0)
from functions.run_python import run_python_file

if __name__ == "__main__":
    print('Ran run_python_file("calculator", "main.py")')
    print(run_python_file("calculator", "main.py"))
    print()

    print('Ran run_python_file("calculator", "tests.py")')
    print(run_python_file("calculator", "tests.py"))
    print()

    print('Ran run_python_file("calculator", "../main.py")')
    print(run_python_file("calculator", "../main.py"))
    print()

    print('Ran run_python_file("calculator", "nonexistent.py")')
    print(run_python_file("calculator", "nonexistent.py"))
    print()
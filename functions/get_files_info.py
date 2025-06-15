import os

def get_files_info(working_directory, directory=None):
    if directory is None or directory == ".":
        directory = working_directory
    try:
        abs_working_directory = os.path.abspath(working_directory)
        abs_directory = os.path.abspath(directory)
        if not abs_directory.startswith(abs_working_directory):
            return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'
        if not os.path.isdir(abs_directory):
            return f'Error: "{directory}" is not a directory'

        entries = []
        for entry in os.listdir(abs_directory):
            entry_path = os.path.join(abs_directory, entry)
            is_dir = os.path.isdir(entry_path)
            try:
                file_size = os.path.getsize(entry_path)
            except Exception as e:
                return f'Error: Could not get size for "{entry}": {e}'
            entry_str = f'- {entry}: file_size={file_size} bytes, is_dir={is_dir}'
            # If it's a .py file, include the first 10 lines
            if entry.endswith('.py') and not is_dir:
                try:
                    with open(entry_path, 'r', encoding='utf-8') as f:
                        lines = []
                        for _ in range(10):
                            line = f.readline()
                            if not line:
                                break
                            lines.append(line.rstrip())
                    if lines:
                        entry_str += "\n" + "\n".join(lines)
                except Exception as e:
                    entry_str += f"\nError: Could not read file: {e}"
            entries.append(entry_str)

        return "\n".join(entries)
    except Exception as e:
        return f'Error: {e}'
# FileFlow: Python Import Dependency Visualizer

FileFlow analyzes a Python project directory and generates a visual diagram illustrating the relationships between `.py` files based on their import statements. The diagram maps which files import others and displays these dependencies as a directed graph.

## Features
- **Recursive Analysis**: Scans all `.py` files in the project, including nested directories.
- **File-to-File Import Mapping**: Focuses on file-level import relationships (not class/function calls).
- **Markdown Output**: Outputs a Markdown file listing all file-to-file import relationships.
- **Efficient**: Designed to handle large codebases efficiently.

## Requirements
- Python 3.7+
- No external dependencies. FileFlow uses only the Python standard library.

You do not need to install any additional packages.
## Usage
From the project directory, run:

```
python FileFlow.py <path_to_your_python_project>
```
- `<path_to_your_python_project>`: Root directory of the Python project you want to analyze.
- `--output`: (optional) Output Markdown file path. Default is `fileflow_output.md`.

Example:
```
python FileFlow.py ./myproject --output my_report.md
```

The resulting Markdown report will be saved to the specified file. It lists all file-to-file import relationships in your project.
## Notes
- Only imports between files within the specified project directory are shown as edges.
- External library imports are ignored.
- If a file contains syntax errors, it will be skipped.

## License
MIT License

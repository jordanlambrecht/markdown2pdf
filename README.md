# Markdown to PDF Converter

This project converts Markdown files to PDFs using Python.

## Libraries Used

- [markdown2](https://github.com/trentm/python-markdown2): Converts Markdown to HTML.
- [pdfkit](https://github.com/JazzCore/python-pdfkit): Converts HTML to PDF.

## Instructions

1. Navigate to Your Project Directory. Open Command Prompt and change to your project directory using the cd command.
   windows: `cd path\to\your\project`
   mac: `cd path/to/your/project`
2. Create virtual environment `python3 -m venv env`
3. Activate the virtual env
   windows: `env\Scripts\activate`
   mac: `source env/bin/activate`
4. Install the required libraries: `pip install -r requirements.txt`
5. Ensure `wkhtmltopdf` is installed: `brew install wkhtmltopdf` (on macOS)
6. Run the script: `python3 markdown2pdf.py`
7. Follow the prompts in your terminal.
8. Turn off the lights before you leave `deactivate`
9. Live laugh love

## To-Do

- Add more file format support.
- Implement a GUI for non-terminal users.

## Overview of Functions

The script includes functions for loading configuration, converting Markdown to PDF, and logging.

## Contributions

Idk wtf I'm doing so any help is great.

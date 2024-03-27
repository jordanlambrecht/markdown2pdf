#!/usr/bin/env python
import os
import pdfkit
import json
import logging
from pathlib import Path
import sys
from PyPDF2 import PdfMerger
import datetime
import tqdm
from prompt_toolkit import prompt
from prompt_toolkit.completion import FuzzyCompleter, WordCompleter
from prompt_toolkit.shortcuts import radiolist_dialog, prompt
from prompt_toolkit import Application
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.layout.containers import VSplit, HSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.widgets import RadioList, Button

# Additional imports for handling terminal interactions
import click  # For enhanced terminal interactions

class style:
    RED = '\033[31m'
    GREEN = '\033[32m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    YELLOW = '\033[33m'
    BOLD = '\033[1m'

# ASCII art for the welcome message
ascii_art = r"""
      ██            ██                        
    ██░░██        ██░░██                      
    ██░░▒▒████████▒▒░░██                ████  
  ██▒▒░░░░▒▒▒▒░░▒▒░░░░▒▒██            ██░░░░██
  ██░░░░░░░░░░░░░░░░░░░░██            ██  ░░██
██▒▒░░░░░░░░░░░░░░░░░░░░▒▒████████      ██▒▒██
██░░  ██  ░░██░░  ██  ░░  ▒▒  ▒▒  ██    ██░░██
██░░░░░░░░██░░██░░░░░░░░░░▒▒░░▒▒░░░░██████▒▒██
██░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░██░░██  
██░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░██░░██  
██░░░░░░░░░░░ Markdown2PDF ░░░░░░░░░░░░░██    
██▒▒░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░██    
██▒▒░░░░░░░░░░░░░ Jordan Lambrecht ░░░░░░██    
██▒▒░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▒▒██    
  ██▒▒░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▒▒██      
    ██▒▒░░▒▒▒▒░░▒▒░░░░░░▒▒░░▒▒▒▒░░▒▒██        
      ██░░████░░██████████░░████░░██          
      ██▓▓░░  ▓▓██░░  ░░██▓▓  ░░▓▓██          
"""

def initialize_logger(log_level):
    """Set up logging to file and console with a specified log level."""
    logs_dir = Path("logs")
    logs_dir.mkdir(parents=True, exist_ok=True)
    numeric_level = getattr(logging, log_level.upper(), None)
    
    if not isinstance(numeric_level, int):
        raise ValueError(f'{style.RED}🤬 Invalid log level: {log_level} {style.RESET}')
    
    log_file_path = logs_dir / "conversion.log"  # Use the Path object for the log file path
    
    logging.basicConfig(level=numeric_level,
                        format='%(asctime)s - %(levelname)s: %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        handlers=[logging.FileHandler(str(log_file_path), mode='a', encoding='utf-8'), logging.StreamHandler()])
    
def load_or_create_config():
    """Load or create a configuration file."""
    config_path = Path("config.json")
    if not config_path.exists():
        print(f"{style.YELLOW}Creating a new configuration file...{style.RESET}")
        config = {"output_directory": "./output/", "log_level": "WARN"}  # Set default log level to WARN
        with open(config_path, 'w', encoding='utf-8') as file:
            json.dump(config, file, indent=4)
        print(f"{style.CYAN}Log level set to WARN. You can change this in the config.json.{style.RESET}")  # Inform the user
        logging.info("Created a new configuration file with log level WARN.")
    else:
        with open(config_path, 'r', encoding='utf-8') as file:
            config = json.load(file)
            if 'log_level' not in config:  # Ensure log_level is always in the config
                config['log_level'] = 'WARN'
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=4)
                print(f"{style.CYAN}Log level set to WARN. You can change this in the config.json.{style.RESET}")  # Inform the user
    return config

def update_config(key, value):
    """Update a specific configuration key with a new value"""
    config = load_or_create_config()
    config[key] = value
    with open("config.json", "w") as config_file:
        json.dump(config, config_file)
        
def list_projects(base_path="./Projects"):
    """
    List existing projects within a specified base path.
    
    Args:
        base_path (str): The base directory path where projects are stored.
    
    Returns:
        list: A list of project names (str).
    """
    base_dir = Path(base_path)
    projects = [p.stem for p in base_dir.iterdir() if p.is_dir()]
    return projects

def create_project(project_name):
    """Create a new project directory structure"""
    base_path = Path(f"./Projects/{project_name}")
    base_path.mkdir(parents=True, exist_ok=True)
    (base_path / "input").mkdir(parents=True, exist_ok=True)
    print(f"{style.GREEN}💫 New project '{project_name}' created. Please insert your Markdown files into the 'input' folder.{style.RESET}")

    # Prompt for the next step using radio inputs
    next_step = radiolist_dialog(
        title="What's Next?",
        text="Choose your next step:",
        values=[
            ("later", "🤙 I'll do it later. Goodbye for now"),
            ("ready", "👌 I've placed the documents into the input folder and I'm ready to go"),
        ],
    ).run()
    
    if next_step == "later":
        display_goodbye()
        sys.exit(0)
    elif next_step == "ready":
        # Continue with the script if the user is ready
        return project_name
    else:
        # In case the dialog is canceled, treat it as "later"
        display_goodbye()
        sys.exit(0)
    
def validate_project_name(name, existing_projects=None):
    """
    Check if the provided name is valid for a project, allowing more characters and handling an existing projects list.
    
    Args:
        name (str): The name of the project to validate.
        existing_projects (list): An optional list of existing project names for validation.
    
    Returns:
        bool: True if the name is valid, False otherwise.
    """
    if existing_projects is None:
        existing_projects = list_projects()  # Use the default path or modify as needed
    
    # Allow spaces, hyphens, and underscores in project names
    valid_name = all(c.isalnum() or c in " -_" for c in name)
    # Perform a case-insensitive comparison
    return valid_name and name.lower() not in (project.lower() for project in existing_projects)


def validate_yes_no(prompt):
    """
    Prompts the user with a question and expects a 'yes' or 'no' response.
    Accepts variations of 'yes' and 'no', including 'y' and 'n', and returns a boolean value.
    Args:
        prompt (str): The prompt/question to display to the user.
    Returns:
        bool: True if the user inputs 'yes' or 'y', False if 'no' or 'n'.
    """
    valid_responses = {"yes": True, "y": True, "no": False, "n": False}
    while True:
        user_input = input(prompt).lower()
        if user_input in valid_responses:
            return valid_responses[user_input]
        else:
            print("Invalid response. Please answer with 'yes' or 'no' (or 'y' or 'n').")

def get_project_choice():
    """
    Prompt the user to select an existing project or create a new one using an interactive list.
    Use radiolist_dialog from prompt_toolkit for project selection.
    """
    projects = list_projects()
    projects_options = [(project, project) for project in projects]
    projects_options.append(('new', '👶 Create a new project'))  # Changed label for consistency
    
    # Show a radiolist dialog to let the user choose an existing project or create a new one
    project_choice = radiolist_dialog(
        title="Project Selection",
        text="Choose an existing project or create a new one:",
        values=projects_options,
    ).run()

    if not project_choice:
        print(f"{style.RED}🤬 No project selected. Exiting...{style.RESET}")
        sys.exit(0)
        
    if project_choice == 'new':
        project_name = prompt(f"{style.CYAN}✨ Enter the name of the new project: {style.RESET}", completer=FuzzyCompleter(WordCompleter(projects)))
        while not validate_project_name(project_name):
            print(f"{style.RED}🤬 Invalid project name. Please use alphanumeric characters and ensure the project does not already exist.{style.RESET}")
            project_name = prompt(f"{style.CYAN}👶 Enter the name of the new project: {style.RESET}", completer=FuzzyCompleter(WordCompleter(projects)))
        create_project(project_name)
        return project_name
    else:
        return project_choice
    
# def get_project_choice():
#     """Prompt the user to select an existing project or create a new one using an interactive list"""
#     """Use radiolist_dialog from prompt_toolkit for project selection."""
#     projects = list_projects()
#     projects_options = [(project, project) for project in projects]
#     projects_options.append(('new', 'Create a new project'))
    
#     project_choice = radiolist_dialog(
#         title="Project Selection",
#         text="Choose an existing project or create a new one:",
#         values=projects_options,
#     ).run()
    
#     if not project_choice:
#         print("{style.RED}🤬 No project selected. Exiting...")
#         sys.exit(0)
        
#     if project_choice == 'new':
#         project_name = input("Enter the name of the new project: ")  # Consider adding validation here as well
#         create_project(project_name)  # Make sure create_project doesn't call sys.exit() if you plan to continue the script
#         return project_name
#     else:
#         return project_choice
        
#     if projects:
#         # Add an option for creating a new project
#         projects.append('👶 Create a new project')
#         # Use radiolist_dialog to let the user select a project or create a new one
#         result = radiolist_dialog(
#             title="Project Selection",
#             text="Select an existing project or create a new one:",
#             values=[(project, project) for project in projects],
#         ).run()

#         if result == 'Create a new project':
#             project_name = prompt("{style.CYAN}✨ Enter the name of the new project: ", completer=FuzzyCompleter(WordCompleter(projects)))
#             while not validate_project_name(project_name):
#                 print(f"{style.RED}🤬 Invalid project name. Please use alphanumeric characters and ensure the project does not already exist.{style.RESET}")
#                 project_name = prompt("{style.CYAN}👶 Enter the name of the new project: ", completer=FuzzyCompleter(WordCompleter(projects)))
#             create_project(project_name)
#             return project_name
#         elif result:
#             return result
#         else:
#             print(f"{style.RED}🤬 Project not found or creation canceled. Please try again.{style.RESET}")
#             sys.exit()
#     else:
#         print("🧐 No existing projects found.")
#         project_name = prompt("Enter the name of the new project: ")
#         while not validate_project_name(project_name):
#             print(f"{style.RED}🤬 Invalid project name. Please use alphanumeric characters.{style.RESET}")
#             project_name = prompt("{style.CYAN}👶 Enter the name of the new project: ")
#         create_project(project_name)
#         return project_name
        
# Handle project selection or creation
def handle_project_directory():
    """Prompt the user for project selection or creation using an interactive list."""
    display_welcome()
    projects_path = Path("./Projects")
    projects_path.mkdir(exist_ok=True)
    existing_projects = list_projects()
    
    # Prepare project options for the radiolist dialog
    projects_options = [(project, project) for project in existing_projects]
    projects_options.append(('new', '👶 Create a new project'))
    
    # Show a radiolist dialog to let the user choose an existing project or create a new one
    project_choice = radiolist_dialog(
        title="Project Selection",
        text="Choose an existing project or create a new one:",
        values=projects_options,
    ).run()

    if project_choice == 'new':
        project_name = prompt("👶 Enter the name of the new project: ", completer=FuzzyCompleter(WordCompleter(existing_projects)))
        if not validate_project_name(project_name, existing_projects):
            print(f"{style.RED}Invalid project name. Please use alphanumeric characters and ensure the project does not already exist.{style.RESET}")
            # You might want to loop this or handle it differently depending on your needs.
            sys.exit(1)
        create_project(project_name)
        
        # Prompt for the next step after creating a new project
        next_step = radiolist_dialog(
            title="What's Next?",
            text="Choose your next step:",
            values=[
                ("later", "🤙 I'll do it later. Goodbye for now"),
                ("ready", "👌 I've placed the documents into the input folder and I'm ready to go"),
            ],
        ).run()

        if next_step == "later":
            display_goodbye()
            sys.exit(0)
        elif next_step == "ready":
            return Path(f"./Projects/{project_name}")  # Continue with the script
    elif project_choice and project_choice in existing_projects:
        return projects_path / project_choice
    else:
        print(f"{style.RED}🤬 No project selected or project not found. Exiting...{style.RESET}")
        sys.exit(1)
# def handle_project_directory():
#     """Prompt the user for project selection or creation."""
#     projects_path = Path("./Projects")
#     projects_path.mkdir(exist_ok=True)
#     existing_projects = [p.name for p in projects_path.iterdir() if p.is_dir()]
    
#     if existing_projects:
#         print(f"Existing projects: {', '.join(existing_projects)}")
#         project_choice = input("📋 Select a project or type 'new' to create one: ")
#     else:
#         print("🧐 No existing projects found.")
#         project_choice = 'new'
    
#     if project_choice.lower() == 'new':
#         new_project_name = input("👶 Enter the new project name: ")
#         project_path = projects_path / new_project_name
#         project_path.mkdir(parents=True, exist_ok=True)
#         (project_path / "input").mkdir()
#         print(f"{style.GREEN}🎁 New project created at: {project_path}. Please add your Markdown files to the 'input' folder.{style.RESET}")
#         sys.exit(0)
#     elif project_choice in existing_projects:
#         return projects_path / project_choice
#     else:
#         print(f"{style.RED}🤬 Project not found. Exiting...{style.RESET}")
#         sys.exit(1)

def convert_and_combine_md_to_pdf(project_name):
    """Convert Markdown files to PDF and optionally combine them"""
    try:
        input_path = Path(f"./Projects/{project_name}/input")
        output_path_individual = Path(f"./Projects/{project_name}/output/{project_name}/individual")
        output_path_combined = Path(f"./Projects/{project_name}/output/combined")

        output_path_individual.mkdir(parents=True, exist_ok=True)
        output_path_combined.mkdir(parents=True, exist_ok=True)

        pdf_files = []
        # Here we define markdown_files by listing all .md files in the input directory
        markdown_files = list(input_path.glob("*.md"))
        
        for md_file in tqdm(markdown_files, desc="Converting Markdown files", colour='blue'):
            try:
                with open(md_file, "r") as file:
                    content = file.read()
                    title = content.split('\n', 1)[0].replace("#", "").strip()
                    now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                    output_file_name = f"{project_name}_{title}_{now}.pdf"
                    output_file_path = output_path_individual / output_file_name

                    html_text = markdown2.markdown(content)
                    try:
                        pdfkit.from_string(html_text, str(output_file_path))
                    except:
                        print(f"{style.RED}Error: There was an issue using pdfkit 😞{style.RESET}")
                    finally:
                        pdf_files.append(str(output_file_path))
                        print(f"{style.GREEN}Successfully converted {md_file.name} to PDF. 🎉{style.RESET}")
            except Exception as e:
                logging.error(f"Failed to convert {md_file.name} to PDF. Error: {e}")
                print(f"{style.RED}Failed to convert {md_file.name} to PDF. 😞{style.RESET}")
                pass

        if click.confirm("Do you want to combine all the PDFs into one?", default=True):
            merger = PdfMerger()
            try:
                for pdf_file in pdf_files:
                    merger.append(pdf_file)
                    combined_pdf_path = output_path_combined / f"{project_name}_{now}.pdf"
                    merger.write(str(combined_pdf_path))
                    merger.close()
                    print(f"{style.GREEN}All PDFs combined into {combined_pdf_path}.{style.RESET}")
            except Exception as e:
                logging.error(f"Failed to merge files. Error: {e}")
                print(f"{style.RED}Failed to merge files 😞{style.RESET}")
    except KeyboardInterrupt:
        # Handle graceful exit for CTRL+C
        print(f"\n{style.RED}Operation was rudely interrupted by user 🤬.{style.RESET}")
        
def display_welcome():
    print(f"----------------------------------------------------------")
    print("        ")
    print("        ")
    print(style.CYAN + ascii_art + style.RESET)
    print("        ")
    print(f"{style.CYAN}Welcome to the Markdown to PDF Converter. Because why not?{style.RESET}")
    print(f"{style.YELLOW}We're transforming your Markdown files into PDFs, as if the world needed more PDFs...{style.RESET}")

def display_goodbye():
    print(f"\n{style.CYAN}----------------------------------------------------------{style.RESET}")
    print(f"\n{style.CYAN}  Program completed successfully. Have a blessed day! 👋  {style.RESET}")
    print(f"\n{style.CYAN}----------------------------------------------------------{style.RESET}")
    
def main(show_welcome):
    if show_welcome:
        display_welcome()
        
    try:
        config = load_or_create_config()
        initialize_logger(config['log_level'])
        project_path = handle_project_directory()
        
        convert_and_combine_md_to_pdf(project_path, config)
    except Exception as e:
        logging.critical("An unexpected error occurred", exc_info=True)
        print(f"{style.RED}😞 An unexpected error occurred: {e}. Please check the logs for more details.{style.RESET}")
    return False

if __name__ == "__main__":
    show_welcome = True  # Initially, we want to show the welcome message
    while True:
        try:
            show_welcome = main(show_welcome) 
            run_again = validate_yes_no("Do you want to run it again? (y/n): ")
            if not run_again:
                display_goodbye()
                break
        except KeyboardInterrupt:
            print(f"\n{style.RED}Operation was rudely interrupted by user 🤬.{style.RESET}")

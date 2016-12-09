# ODK Aggregation Tool


## Contents
- [Introduction](#introduction)
- [Todo](#todo)
- [Development Environment](#development-environment)


# Introduction
A Python GUI app for:

- Collating ODK Collect instance XML files
- Collating XLSForm metadata
- Writing Stata XML file with:
    - variable labels
    - variable data types
    - value labels for variables using integer-valued choice lists

The specifications document at [specs/specs.md](specs/specs.md) goes in to more detail on the features, overall design and background.


# Todo
Remaining:

- Prototype code amendments:
    - Split form processing to produce separate Stata XML per form def
    - Break down to_stata_xml into smaller, testable pieces
    - Add more cautious error handling so that resolutions can be suggested
- Copy over ODK Tools GUI components for the UI / tk / pyinstaller things
- Prepare UAT materials
- Write user guide

Completed:

- Write specs
- Copy in the ODK Tools GUI project structural bits
- Copy in the prototype code


# Development Environment
Complete the following:

- Install Python 3.5+
- Clone the repository: `git clone [URL] repo`
- Create a virtual environment: `python -m venv venv`
- Activate virtual environment: `call venv\scripts\activate`
    - These next two steps aren't really requirements, just optional hygiene
    - Ensure wheel is installed: `pip install wheel`
    - Update pip if needed: `python -m pip install --upgrade pip`
- Move into repo: `cd repo`
- Install requirements: `pip install -r requirements.txt`
- Run test suite: `python setup.py test`
- Start hacking

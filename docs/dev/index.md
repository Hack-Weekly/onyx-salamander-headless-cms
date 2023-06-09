# Developer Guide

## Getting Started

### Installation

    git clone https://github.com/Hack-Weekly/onyx-salamander-headless-cms.git
    cd onyx-salamander-headless-cms
    pip3 -m venv env
    source env/bin/activate
    pip3 install -r requirements.txt
    pip3 install -r docs/requirements.txt # (optional)

Project documentation is contained in the `docs/` folder, and the main application source code is found in the `src/` folder.

## Coding Conventions

Here are some general guiding principles for the development of this project. It's a good idea to familiarize yourself with them, but don't sweat it too much, we are n00b friendly. The most important thing is to ensure you document, document, document your code!

* A function should do one thing and do it well.
* [Follow PEP-8 standards](https://peps.python.org/pep-0008)!
* Indention is 4 spaces (No tabs!)
* Max line length 79 chars
* Line breaks come before operators
* ALL public methods, classes, and functions MUST have a docstring
* Document any bug fixes, 'hacks', and other non-obvious code using inline comments.
* Use descriptive names and follow CamelCase conventions for most things.
* Use inline and block comments for additional descriptive context if needed.
* Any GLOBAL variables should be ALL CAPS,
* Use the standard i, j, ... variable names for loop iters if needed.
* "Private" methods should start with an underscore ala: `_PrivateMethod(...)`
* Use PyLint to check your code for correctness before making pull requests, and try to get as high a score as you can: `pylint my_file.py`

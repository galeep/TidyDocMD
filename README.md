# TidyDocMD

TidyDocMD is a Python script designed to sort entries in a markdown file based on the last name of the entry. It is particularly useful for organizing markdown files with hierarchical sections, such as lists of people's names under different categories.

## How it works

TidyDocMD reads a markdown file and parses it into a tree of nested `Section` objects. Each `Section` represents a section in the markdown file, capturing its hierarchical organization, text content, and subsections.

The script then sorts the entries in the sections specified by the `--sections` argument. By default, these sections are `Speakers`, `Organizers`, `Mentors`, and `Getting Started`. The sorting is based on the last name of the entry, extracted using the `HumanName` parser from the `nameparser` library.

Finally, TidyDocMD writes the sorted sections back to a markdown file, preserving the original markdown structure.

## How to run it

You can run TidyDocMD from the command line with the following syntax:

```bash
python tidydocmd.py --input INPUT_FILE --output OUTPUT_FILE [--sections SECTION_NAMES] [--debug]
```

Where:

- `INPUT_FILE` is the path to the input markdown file.
- `OUTPUT_FILE` is the path to the output markdown file.
- `SECTION_NAMES` is a list of section names to sort. By default, it is `["Speakers", "Organizers", "Mentors", "Getting Started"]`.
- `--debug` is an optional argument to enable debug mode for additional output.

## Installing Dependencies

This Python script requires the `nameparser` package. Install it using pip:

`pip install nameparser`

(If you're using Python 3 specifically, you might need to use `pip3`.)

A `requirements.txt`` file will be added soon to simplify dependency management.

## Note

TidyDocMD is not related to the Tidy library for HTML/XML processing, nor is it related to Dr. Tinycat. It is a standalone Python script for sorting entries in markdown files. So, no, it won't look adorable in tiny scrubs or fix broken HTML tags. But it can make your markdown directory files and even awesome lists look great!

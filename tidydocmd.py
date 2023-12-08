"""
Sort entries in a markdown file.

This script sorts the entries in a markdown file based on the last name of the entry.
The script assumes that the entries are organized in sections, with each section
having a header that starts with a `#` character. The script sorts the entries
in the sections that are specified in the `--sections` argument. The default
sections are `Speakers`, `Organizers`, `Mentors`, and `Getting Started`.

The script is designed to work with the following markdown structure:
https://github.org/fempire/women-tech-speakers-organizers/blob/master/README.md
"""

import argparse
import logging
from nameparser import HumanName

# from datetime import datetime

# Configuring logging settings
logging.basicConfig(format="%(asctime)s %(message)s", level=logging.INFO)
log = logging.getLogger(__name__)  # Create a logger object


class Section:
    """
    Represents a section in a markdown-like file.

    The `Section` class captures the hierarchical organization
    of a document, with facilities to manage nested sections.

    Attributes:
        name (str): The name of the section.
        depth (int): The depth of the section in the hierarchy.
        text (list): The text content of the section.
        subsections (list): The list of subsections.
        parent (Section): The parent section.
        grandparent (Section): The grandparent section.
        sections_to_sort (list): The list of sections to sort.

    Methods:
        __init__(self, name, depth, parent=None, grandparent=None, sections_to_sort=None):
            Initializes a `Section` object.
        __repr__(self):
            Represents the `Section` object instance by its name and depth.
        _repr(self, depth):
            Helper method for generating string representation with proper indentation for nested sections.
        extract_last_name(self, section):
            Extracts the last name from the section name using the `HumanName` parser.
        sort_subsections(self):
            Sorts the subsections of h2 sections based on the last names of the section headers.
        to_markdownesque(self):
            Generates a string representation of a section, formatted in markdown-like structure to reflect the original file.
    """
    def __init__(
        self, name, depth, parent=None, grandparent=None, sections_to_sort=None
    ):
        """
        Initializes a `Section` object.

        :param name: name of the section
        :param depth: depth of the section in the hierarchy
        :param parent: parent section
        :param grandparent: grandparent section
        :param sections_to_sort: list of sections to sort
        """
        self.name = name
        self.depth = depth
        self.text = []
        self.subsections = []
        self.parent = parent
        self.grandparent = grandparent
        # Here, we ensure self.sections_to_sort is never None
        self.sections_to_sort = sections_to_sort if sections_to_sort is not None else []

    def __repr__(self):
        """
        Represents the `Section` object instance by its name and depth.
        """
        return self._repr(0)

    def _repr(self, depth):
        """
        Helper method for generating string representation with proper
        indentation for nested sections.

        :param depth: current section depth
        :return: string representation of the section
        """
        indent = " " * (depth * 2)
        result = f"Section(name: {self.name}, depth: {self.depth})\n"
        if self.text:
            result += f"{indent}Text: {self.text}\n"
        if self.subsections:
            result += f"{indent}Subsections:\n"
            result += "".join(
                [subsection._repr(depth + 1) for subsection in self.subsections]
            )
        return result

    def extract_last_name(self, section):
        """
        Extract the last name from the section name using the `HumanName` parser.
        If no last name found, use the first name.

        :param section: a `Section` object
        :return: lower-case last name or first name
        """
        parsed_name = HumanName(section.name)
        # Add an indented block here
        return (
            parsed_name.last.lower() if parsed_name.last else parsed_name.first.lower()
        )

    # def sort_subsections(self, parent_section_name, grandparent_section_name, sections_to_sort):
    def sort_subsections(self):
        """
        Sorts the subsections of h2 sections based on the last names of the section headers.
        """
        # Check whether this is an h3 section and its parent h2 section requires sorting
        if self.depth == 3 and self.parent in self.sections_to_sort:
            if self.subsections:
                # If there are h4 subsections
                gp_name = self.grandparent or "No grandparent"
                # First, collect the order of h4 subsections before sorting
                section_names_before = [sub.name for sub in self.subsections]
                # Sort the h4 subsections based on the last name in section names
                self.subsections.sort(key=self.extract_last_name)
                section_names_after = [sub.name for sub in self.subsections]
                # Print the order of the h4 subsections pre- and post-sorting
                log.info(
                    "Before sorting h4s in h3 section '%s', Parent: '%s', Grandparent: '%s': %s",
                    self.name,
                    self.parent,
                    gp_name,
                    section_names_before,
                )
                log.info(
                    "After sorting h4s in h3 section '%s', Parent: '%s', Grandparent: '%s': %s",
                    self.name,
                    self.parent,
                    gp_name,
                    section_names_after,
                )
            else:
                log.debug("No h4 subsections in h3 section '%s'", self.name)
        else:
            log.debug(
                "Not processing as a chosen H3: '%s' at depth %s with parent '%s'",
                self.name,
                self.depth,
                self.parent,
            )

        # Recursively call sort_subsections on each subsection
        for subsect in self.subsections:
            subsect.sort_subsections()

    def to_markdownesque(self):
        """
        Generate a string representation of a section, formatted in
        markdown-like structure to reflect the original file.

        :return: string with markdown headers based on section depth and the section text.
        """
        # Derived the markdown header based on depth
        header_line = "#" * self.depth + " " + self.name + "\n"
        # Maintain the original text intact
        text_content = "".join(self.text)
        # Generate the subsections content by applying the same formatting
        subsections_content = "".join(
            sub.to_markdownesque() for sub in self.subsections
        )
        # Combine header, text, and subsections without altering newlines
        return header_line + text_content + subsections_content


def parse_file(input_path, debug=False, sections_to_sort=None):
    """
    Parses an input file in markdown-esquire format to generate a tree of nested `Section` objects.

    :param input_path: Path to the input file.
    :param debug: Enable debug mode for additional output.
    :return: Root sections of the parsed file as a list of `Section` objects
    """
    with open(input_path, "r", encoding="utf-8") as file:
        # Original carriage returns are preserved
        lines = file.readlines()

    root_sections = []  # To hold top-level sections
    section_stack = []  # To keep track of the current section hierarchy

    for line in lines:
        if line.startswith("#"):
            header_level = len(line) - len(line.lstrip("#"))
            section_name = line[header_level + 1:].strip()

            # Instantiate a new section
            new_section = Section(
                section_name,
                header_level,
                section_stack[-1].name if section_stack else None,
                section_stack[-2].name if len(section_stack) > 1 else None,
                sections_to_sort,
            )

            # Pop sections from the stack until reaching the proper parent level
            while section_stack and section_stack[-1].depth >= header_level:
                section_stack.pop()

            # Add new_section as a subsection or as a root section
            if section_stack:
                section_stack[-1].subsections.append(new_section)
            else:
                root_sections.append(new_section)

            # New section is now the latest active section
            section_stack.append(new_section)
            log.debug(f"Added section: {new_section.name} at depth {new_section.depth}")

        else:
            # Text lines are assigned to the most recently active section
            if section_stack:
                section_stack[-1].text.append(line)

    # Debug option to log the original content of the file
    if debug:
        with open(input_path, "r", encoding="utf-8") as debug_file:
            content = debug_file.read()
            log.debug(
                f"\n--- Original Content of {input_path} ---\n{content}\n--- End of Original Content ---\n"
            )

    return root_sections


if __name__ == "__main__":
    # Prepare argument parser
    parser = argparse.ArgumentParser(description="Sorts entries in a markdown file.")
    parser.add_argument("--input", "-i", required=True, help="Input markdown file path")
    parser.add_argument(
        "--output", "-o", required=True, help="Output markdown file path"
    )
    parser.add_argument(
        "--sections",
        "-s",
        action="append",
        default=["Speakers", "Organizers", "Mentors", "Getting Started"],
        help="H2 sections to sort (default: Speakers, Organizers, Mentors, Getting Started)",
    )
    parser.add_argument("--debug", "-d", action="store_true", help="Enable debug mode")
    args = parser.parse_args()

    # Fetch arguments
    input_file = args.input
    output_file = args.output
    sections_to_sort = args.sections
    debug_mode = args.debug

    if debug_mode:
        log.setLevel(logging.DEBUG)
        log.debug("Debug mode enabled")

    sections = parse_file(
        input_file, debug=debug_mode, sections_to_sort=sections_to_sort
    )

    for section in sections:
        # Sort applicable subsections
        if section.depth == 1:
            for subsection in section.subsections:
                if subsection.depth == 2:
                    log.debug(
                        f"Processing subsections in h2 section '{subsection.name}'..."
                    )
                    subsection.sort_subsections()

    # Write the structured contents to the output markdown file
    with open(output_file, "w", encoding="utf-8") as out_file:
        for section in sections:
            formatted_section = section.to_markdownesque()
            out_file.write(formatted_section)

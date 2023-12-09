"""
Sort entries in a markdown file.

This script sorts the entries in a markdown file based on the last name of the
entry.  The script assumes that the entries are organized in sections, with
each section having a header that starts with a `#` character. The script
sorts the entries in the sections that are specified in the `--sections`
argument. The default sections are `Speakers`, `Organizers`, `Mentors`, and
`Getting Started`.

The script is designed to work with the following markdown structure:
https://github.org/fempire/women-tech-speakers-organizers/blob/master/README.md
"""

import argparse
import logging
import difflib
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
    """

    def __init__(self, name, depth):
        """
        Construct a new 'Section' object.

        :param name: The title of the section
        :param depth: Depth of the section to handle nested sections
        """
        self.name = name
        self.depth = depth  # Nested section depth
        self.text = []  # Placeholder for section text
        self.subsections = []  # Placeholder for nested sections

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

    def extract_last_name(self, sect):
        """
        Extract last name from the section name using the `HumanName` parser.
        If no last name found, use the first name.

        :param section: a `Section` object
        :return: lower-case last name or first name
        """
        parsed_name = HumanName(sect.name)
        # Split the line into multiple lines
        return (
            parsed_name.last.lower() if parsed_name.last else parsed_name.first.lower()
        )

    # The grandparent_section_name is passed as the parent_section_name for
    # H3 sections. Attempts to refactor this have not been successful thus
    # far. Leaving as is for now. The logic for sorting headers in general
    # should be refactored to be more generic and not specific to H3s.
    # "PRs welcome!" Really. Please. :)
    def sort_subsections(
        self, parent_section_name, grandparent_section_name, sects_to_sort
    ):
        """
        Sorts the subsections of h3 sections based on the last names of the
        section headers.  If the section depth is not 3 or the parent section
        is not meant to be sorted, it leaves as is.

        :param parent_section_name: the name of the parent h2 section
        """
        # Check whether this is an h3 section and its parent h2 section
        # requires sorting
        if self.depth == 3 and parent_section_name in sects_to_sort:
            if self.subsections:
                # If there are h4 subsections
                gp_name = grandparent_section_name or "No grandparent"
                # Ugly hack to avoid printing the grandparent name
                # when the grandparent is equivalent to the parent
                # section name. We still log this to debug, but we
                # don't print it to the console. We log that we are
                # setting the grandparent name to "base" instead.
                # /me hangs head in shame
                #
                # Compare parent_section_name and gp_name
                if parent_section_name == gp_name:
                    gp_name = "base"
                    log.debug(
                        "Grandparent and parent of %s are %s, setting to base",
                        self.name,
                        parent_section_name,
                    )
                # First, collect the order of h4 subsections before sorting
                section_names_before = [sub.name for sub in self.subsections]

                # Sort the h4 subsections based on the last name in
                # section names
                self.subsections.sort(key=self.extract_last_name)
                section_names_after = [sub.name for sub in self.subsections]
                # Print the order of the h4 subsections pre- and post-sorting
                # SOON: implement a less sprawling way of producing this output
                log.debug(
                    "Before sorting h4s in h3 section '%s', Parent: '%s', Grandparent: '%s': %s",
                    self.name,
                    parent_section_name,
                    gp_name,
                    section_names_before,
                )
                log.debug(
                    "After sorting h4s in h3 section '%s', Parent: '%s', Grandparent: '%s': %s",
                    self.name,
                    parent_section_name,
                    gp_name,
                    section_names_after,
                )
                if section_names_before != section_names_after:
                    log.info(
                        "Before sorting h4s in h3 section '%s', Parent: '%s', Grandparent: '%s': %s",
                        self.name,
                        parent_section_name,
                        gp_name,
                        section_names_before,
                    )
                    log.info(
                        "After sorting h4s in h3 section '%s', Parent: '%s', Grandparent: '%s': %s",
                        self.name,
                        parent_section_name,
                        gp_name,
                        section_names_after,
                    )
                    calculate_reshuffle_percentage(
                        self.name,
                        parent_section_name,
                        section_names_before,
                        section_names_after,
                    )
                else:
                    log.info(
                        "No change in order of h4s in h3 section '%s', Parent: '%s'",
                        self.name,
                        parent_section_name,
                    )
            else:
                log.debug("No h4 subsections in h3 section '%s'", self.name)
        else:
            log.debug(
                "Not processing as a chosen H3: '%s' at depth %s with parent '%s'",
                self.name,
                self.depth,
                parent_section_name,
            )

        # Recursively call sort_subsections on each subsection
        for subsect in self.subsections:
            # Pass the current section name as the parent,
            # and the current parent section name as the grandparent
            # for the next level.
            # Also, pass sections_to_sort as the last argument.
            subsect.sort_subsections(self.name, parent_section_name, sects_to_sort)
            # subsect.sort_subsections(
            #    self.name if self.depth == 2 else parent_section_name, self.name, sections_to_sort
            # )

    def to_markdownesque(self):
        """
        Generate a string representation of a section, formatted in
        markdown-like structure to reflect the original file.

        :return: string with markdown headers based on section depth
        and the section text.
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


def calculate_reshuffle_percentage(
    this_section, this_parent, section_name_before, section_name_after
):
    """Calculates the percentage of reshuffled names in a section.

    This function takes in the previous and current section names and calculates the percentage
    of names that have been reshuffled. It also prints the details of each reshuffled name.

    Args:
        this_section (str): The name of the current section.
        this_parent (str): The name of the parent section.
        section_name_before (list): The list of names before reshuffling.
        section_name_after (list): The list of names after reshuffling.
    """
    diff = difflib.ndiff(section_name_before, section_name_after)
    moved = set(
        line[2:] for line in diff if line.startswith("- ") or line.startswith("+ ")
    )
    reshuffled = len(moved)
    reshuffle_percentage = round(reshuffled / len(section_name_before) * 100)

    shuffle_mess = (
        f"{this_parent}:{this_section}: alphabetized {reshuffled} out of "
        f"{len(section_name_before)} names ({reshuffle_percentage}%):"
    )
    print(shuffle_mess)
    for name in moved:
        old_index = section_name_before.index(name)
        new_index = section_name_after.index(name)
        if old_index == 0:
            moved_info = f"* {name} (was first, now is after {section_name_after[new_index - 1]})"
        elif new_index == 0:
            moved_info = f"* {name} (was after {section_name_before[old_index - 1]}, now is first)"
        else:
            moved_info = f"* {name} (was after {section_name_before[old_index - 1]}, now is after {section_name_after[new_index - 1]})"
        print(moved_info)


def parse_file(input_path, debug=False):
    """
    Parses an input file in markdown-esquire format to generate a tree of
    nested `Section` objects.

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
            section_name = line[header_level + 1 :].strip()

            # Instantiate a new section
            new_section = Section(section_name, header_level)

            # Pop sections from the stack until reaching the proper
            # parent level
            while section_stack and section_stack[-1].depth >= header_level:
                section_stack.pop()

            # Add new_section as a subsection or as a root section
            if section_stack:
                section_stack[-1].subsections.append(new_section)
            else:
                root_sections.append(new_section)

            # New section is now the latest active section
            section_stack.append(new_section)
            log.debug(
                "Added section: %s at depth %s", new_section.name, new_section.depth
            )

        else:
            # Text lines are assigned to the most recently active section
            if section_stack:
                section_stack[-1].text.append(line)

    # Debug option to log the original content of the file
    if debug:
        with open(input_path, "r", encoding="utf-8") as debug_file:
            content = debug_file.read()
            log.debug(
                "\n--- Original Content of %s ---\n"
                "%s\n--- End of Original Content ---\n",
                input_path,
                content,
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

    # Generate nested Section objects from input file
    sections = parse_file(input_file, debug=debug_mode)

    for section in sections:
        # Sort applicable subsections
        for section in sections:
            if section.depth == 1:
                for subsection in section.subsections:
                    if subsection.depth == 2:
                        log.debug(
                            "Outer: Processing subsections in H2 section '%s'..."
                            % subsection.name
                        )
                        subsection.sort_subsections(
                            subsection.name, None, sections_to_sort
                        )

    # Write the structured contents to the output markdown file
    with open(output_file, "w", encoding="utf-8") as out_file:
        for section in sections:
            formatted_section = section.to_markdownesque()
            out_file.write(formatted_section)

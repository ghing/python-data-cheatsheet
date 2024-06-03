#!/usr/bin/env python
# The above line is a shebang line that tells the shell to execute the script
# using the python interpreter.
# Every Python script you intend to run from the command line should start with
# this line. However, not every .py file, for example files that contain
# code that you import into other filles, needs this line.

# This script is an example of a Python script for processing tabular data.
# It's commented very verbosely to explain what each block of code does.
# These are way more comments than you'll need, or want to write, in a real
# script, but I'm trying to explain what nearly every line or non-obvious
# argument does.

# This is a docstring. It doesn't *do* anything, but it tells someone
# reading the code what a file, function or class does and how to use it.
# Often, software developers will use tools to generate documentation
# websites from these docstrings.
# The docstring can be any text, but there are common conventions -
# especially if you want to automatically generate documentation from
# code. See https://stackoverflow.com/a/24385103 for some examples
# of popular conventions.
"""
Process eligibility changes for Section 1115 waivers for justice-involved
groups.

Process eligibility changes compiled by KFF at
https://datawrapper.dwcdn.net/HhnNo/52/.

"""

# Import the necessary modules or elements from modules
# These are libraries of Python code that provide specific functionality
# that's helpful for the script to work. It saves us from writing every
# single function from scratch.

# These are modules that are part of Python's standard library.
# argparse helps handling command-line arguments. Click is a
# popular alternative that may be easier to use, and has some additional
# affordances, but it's not built in.
import argparse

# re allows us to work with regular expressions - a syntax for using patterns
# to match, extract and manipulate text.
import re

# We'll need sys to write to standard output.
import sys

# These are third party packages that are not part of Python's standard library.
# They need to be installed with a package manager like pip.

# Pandas is used for manipulating and analyzing tabular data. It's doing the
# heavy lifting in this script.
# You can think of Pandas as equivalent to dplyr in R or Arquero in
# JavaScript.
import pandas as pd


# These are helper functions that will be used ("called") by the main function
# below.


def clean_column_name(column_name: str) -> str:
    """
    Clean a column name to make access easier.

    Args:
        column_name (str): Column name in the unprocessed data.

    Returns:
        str: Cleaned column name with whitespace replaced by spaces.

    """
    # First, strip whitespace from the beginning and end of the string.
    cleaned = column_name.strip()
    # Then, convert the string to lowercase.
    cleaned = cleaned.lower()
    # Next, replace any remaining whitespace with underscores.
    cleaned = re.sub(r"\s+", "_", cleaned)

    # Note that we could have done this all in one line with:
    # return re.sub(r"\s+", "_", column_name.strip().lower())

    return cleaned


def expand_tags(
    data: pd.DataFrame, tag_column: str = "tags", sep: str = "|", prefix: str = "tag_"
) -> pd.DataFrame:
    """
    Expand a column of tags into multiple columns.

    Args:
        data (pd.DataFrame): DataFrame containing the tags column.
        tag_column (str): Name of the column containing the tags.
        sep (str): Separator between tags. Default is a pipe character.
        prefix (str): Prefix for the new columns. Default is "tag_".

    Returns:
        pd.DataFrame: DataFrame with tags expanded into multiple columns.

    """
    # Split the tags column into a DataFrame of tags.
    tags = data[tag_column].str.split(
        sep,
        # The pattern is just a string to match exactly, not a regular expression.
        regex=False,
        # Expand the split strings into separate columns.
        expand=True,
    )
    # Name the expanded columns. By default they're just named 0, 1, 2, etc.
    # This line uses two Python features: a list comprehension and an f-string.
    # A list comprehension is a way to create a list by iterating over another list,
    # optionally transforming or filtering the elements.
    # An f-string is a way to embed variables and expressions in a string.
    tags.columns = [f"{prefix}{c}" for c in tags.columns]
    # Concatenate the expanded columns back to the original DataFrame.
    return pd.concat([data, tags], axis=1)


# This function is the main body of the program.
def process_eligibility_changes_cmd() -> None:
    """
    Process eligibility changes for Section 1115 waivers for justice-involved
    groups.

    """
    # Set up handling of the command-line arguments.
    # Some of the text is very similar to the docstrings, but they're for
    # for different audiences. The docstrings are for people reading the code,
    # the text in the argparse arguments is for people running the script
    # from the command line.
    parser = argparse.ArgumentParser(
        prog="process_section_1115_eligbility_changes",
        # Using parenthesis is a way to break long strings into multiple lines
        description=(
            "Process eligibility change data for Section 1115 waivers for "
            "justice-involved groups."
        ),
    )
    # We'll add both positional arguments and optional arguments.
    parser.add_argument(
        "input_file",
        help="Path to the input CSV file containing eligibility change data.",
        # Automatically convert the file path to a file object.
        type=argparse.FileType("r"),
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Path to output cleaned CSV. Default is to print to standard output.",
        type=argparse.FileType("w"),
        default=sys.stdout,
    )

    # Parse the command-line arguments.
    args = parser.parse_args()

    # Read the input CSV file into a Pandas DataFrame.
    eligibility_changes = pd.read_csv(
        args.input_file,
        # Part of the processing we need to do is to skip the header row
        # so the first row of data is the column names.
        skiprows=1,
    )

    # Clean the column names
    # Avoiding spaces and making all the column names lowercase makes it easier
    # to access the columns when analyzing the data.
    # Many Pandas DataFrame methods return a new DataFrame, so we need to
    # assign it back to the variable to keep the changes.
    eligibility_changes = eligibility_changes.rename(columns=clean_column_name)

    # Remove <br> HTML tags and newlines from the `tags` column and replace
    # with pipes.
    # This is useful for filtering in a simple data tool like a spreadsheet program.
    # Where we would just check if the tags field contains a particular substring.
    # Note that we're using the clean column name here, i.e. `tags` not `TAGS`.
    eligibility_changes["tags"] = eligibility_changes["tags"].str.strip().str.replace("<br>\n", "|")

    # Expand the `tags` column into one column per tag.
    # This might make it easier to filter the data in the future using certain tools.
    # It also allows more unambiguous filtering than the combined field.
    # Since this processing takes more code, I've broken it out into a separate function
    eligibility_changes = expand_tags(eligibility_changes)

    # The `population` and `benefits` columns can also contain <br> HTML tags. Remove them.
    # At the same time, remove trailing whitespace.
    for col in ["population", "benefits"]:
        eligibility_changes[col] = eligibility_changes[col].str.replace(
            # The r before the string indicates that it's a raw string, which
            # means that backslashes are treated as literal characters and not
            # as escape characters.
            # Raw strings are frequently used with regular expressions.
            # TODO: Explain this regular expression.
            # In the mean time, LLMs like ChatGPT are a good easy resource for explaining
            # a particular regular expression.
            r"(<br>)+",
            # Replace the tags with nothing.
            "",
            # In this case we are using a regular expression to match a pattern. 
            regex=True,
        ).str.strip()

    # The `population` column can also contain links in `<a>` tags. Reformat them
    # so the're like: "link text (link url)".
    eligibility_changes["population"] = eligibility_changes["population"].str.replace(
        # This regular expression uses a feature called "named groups" to identify
        # the URL portion of the pattern and the link text. Using the named groups
        # allows us to access these specific portions of the matched text when
        # determining the replacement text.
        r'<a .* href="(?P<url>.*)">(?P<link_text>.*)</a>',
        # Here we need to use a function for the replacement in order to access the
        # regex match groups.
        lambda m: f"{m.group('link_text')} ({m.group('url')})",
        # Use a regular expression.
        regex=True,
    )

    # The limitations column can contain some entry whitespace. Remove it.
    eligibility_changes["limitations"] = eligibility_changes["limitations"].str.strip()

    # Output the cleaned data to a CSV file.
    # index=False means we don't include the index that pandas automatically
    # generates. For simple cases like this, the index is essentially a line
    # number. However, for more complex cases, we can manipulate the index
    # for more advanced data manipulation or analysis.
    eligibility_changes.to_csv(args.output, index=False)


# This is another Python convention that you will find in most scripts
# you write to be run from the command line. It's a way to tell Python
# to only execute the code in this block if the script is being run
# from the command line. It allows a Python file to be used both as a
# script and as a module from which you can import code into
# other scripts.
if __name__ == "__main__":
    process_eligibility_changes_cmd()

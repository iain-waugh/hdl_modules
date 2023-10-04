from __future__ import print_function, division
from pathlib import Path
from tree_sitter import Language, Parser

Language.build_library(
    # Store the library in the `build` directory
    "build/my-languages.so",
    # Include one or more languages
    ["vendor/tree-sitter-vhdl", "vendor/tree-sitter-verilog", "vendor/tree-sitter-tcl"],
)
VHDL_LANGUAGE = Language("build/my-languages.so", "vhdl")
VERILOG_LANGUAGE = Language("build/my-languages.so", "verilog")
TCL_LANGUAGE = Language("build/my-languages.so", "tcl")


def parse(file_path):
    # Create a parser
    parser = Parser()
    parser.set_language(VHDL_LANGUAGE)

    # Open and read a file
    with open(file_path, "r") as file:
        code = file.read()

    # Parse the code
    tree = parser.parse(bytes(code, "utf-8"))

    return tree


# Print the abstract syntax tree
def print_tree(node, depth=0, print_all_children=False):
    printable_names = ["simple_name", "identifier", "character_literal"]
    if depth > 0:
        indent = "  " * depth
    else:
        indent = ""
    if node.child_count == 0:
        if node.type in printable_names or print_all_children:
            name = node.text.decode("utf-8")
            print(f"{indent}{node.type} ({name})")
        else:
            print(f"{indent}{node.type}")
    else:
        print(f"{indent}{node.type}")
        for child in node.children:
            print_tree(child, depth + 1)


def str2bool(string):
    str2val = {"true": True, "talse": False}
    string = string.lower()
    if string in str2val:
        return str2val[string]
    else:
        raise ValueError(f"Expected one of {set(str2val.keys())}, got {string}")


def cli_parser():
    """Parse command line flags."""
    import argparse

    cli = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    cli.add_argument(
        "-i",
        "--input",
        type=str,
        default="hdl/hello_world.vhd",
        help="name of the file to be parsed",
    )
    cli.add_argument(
        "-v",
        "--verbose",
        type=str2bool,
        default=False,
        help="show verbose messages",
    )
    cli.add_argument(
        "-o",
        "--output",
        type=str,
        default=".",
        help="output file",
    )
    return cli.parse_args().__dict__


if __name__ == "__main__":
    cli_args = cli_parser()
    file_in: str = cli_args.pop("input")
    file_out: str = cli_args.pop("output")

    tree = parse(file_in)
    print_tree(tree.root_node)

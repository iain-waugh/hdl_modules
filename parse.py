from __future__ import print_function, division
from pathlib import Path
from tree_sitter import Language, Parser

Language.build_library(
    # Store the library in the `build` directory
    "build/my-languages.so",
    # Include one or more languages
    [
        "vendor/tree-sitter-vhdl",
        "vendor/tree-sitter-verilog",
        'vendor/tree-sitter-tcl'
    ],
)
VHDL_LANGUAGE = Language("build/my-languages.so", "vhdl")
VERILOG_LANGUAGE = Language("build/my-languages.so", "verilog")
TCL_LANGUAGE = Language('build/my-languages.so', 'tcl')

# Create a parser
parser = Parser()
parser.set_language(VHDL_LANGUAGE)
printable_names = ["simple_name", "identifier", "character_literal"]

# Open and read a file
file_path = "hdl/hello_world.vhd"
with open(file_path, "r") as file:
    code = file.read()

# Parse the code
tree = parser.parse(bytes(code, "utf-8"))

print_all_children = False


# Print the abstract syntax tree
def print_tree(node, depth=0):
    indent = "  " * depth
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


print_tree(tree.root_node)

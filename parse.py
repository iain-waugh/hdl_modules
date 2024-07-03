from __future__ import print_function, division
from pathlib import Path
from tree_sitter import Language, Parser
# import hdl

Language.build_library(
    # Store the library in the `build` directory
    "build/my-languages.so",
    # Include one or more languages
    ["vendor/tree-sitter-vhdl", "vendor/tree-sitter-verilog", "vendor/tree-sitter-tcl"],
)
VHDL_LANGUAGE = Language("build/my-languages.so", "vhdl")
VERILOG_LANGUAGE = Language("build/my-languages.so", "verilog")
TCL_LANGUAGE = Language("build/my-languages.so", "tcl")

class HDLParser(object):
    def __init__(self, file_path):
        self.file_path = file_path
        self.language = self.hdl_format()
        return

    def hdl_format(self):
        if self.file_path.suffix.lower() in [".vhd", ".vhdl"]:
            language = "vhdl"
        elif self.file_path.suffix.lower() == ".v":
            language = "verilog"
        elif self.file_path.suffix.lower() == ".sv":
            language = "sv"
        else:
            raise ValueError("Unknown file type: " + self.file_path.suffix.lower())
        return language

    def parse(self):
        # Create a parser
        parser = Parser()
        if self.language == "vhdl":
            parser.set_language(VHDL_LANGUAGE)
        elif self.language in ["verilog", "sv"]:
            parser.set_language(VERILOG_LANGUAGE)

        # Open and read a file
        with open(self.file_path, "rb") as file:
            code = file.read()
    
        # Parse the code
        self.tree = parser.parse(bytes(code.decode("utf-8"), "utf-8"))
        return self.tree

    def get_modules(self):
        # Choose the right query for VHDL, Verilog or System Verilog
        if self.language == "vhdl":
            query = VHDL_LANGUAGE.query("""
            (entity_declaration (identifier)) @param_expression
            """)
        elif self.language in ["verilog", "sv"]:
            query = VERILOG_LANGUAGE.query("""
            (module_header (module_keyword) (simple_identifier) ) @param_expression
            """)
        captures = query.captures(self.tree.root_node)
        
        # Make a list of the module names
        module_names = []
        for capture in captures:
            #print_tree(capture[0], print_all_children=True)
            module_names.append(capture[0].children[1].text.decode("utf-8"))

        return module_names

    def get_package(self):
        return
        
    def get_rtl(self):
        return


# Print the abstract syntax tree
def print_tree(node, depth=0, print_all_children=False):
    printable_names = [
        "simple_name",
        "identifier",
        "simple_identifier", 
        "character_literal"
        ]
    if depth > 0:
        indent = "  " * depth
    else:
        indent = ""
    if node.child_count == 0:
        if (node.type in printable_names) or print_all_children:
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
        default=".",
        help="name of the file or folder to be parsed",
    )
    cli.add_argument(
        "-v",
        "--verbose",
        type=bool,
        default=False,
#        action=argparse.BooleanOptionalAction,
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

def get_files_with_suffix(path, suffixes=[".vhd", ".vhdl", ".v", ".sv"]):
    matching_files = []
    path = Path(path)

    if path.is_file() and path.suffix in suffixes:
        matching_files.append(path)

    if not path.exists():
        print("The specified path does not exist.")
        return matching_files
    
    if path.is_dir():
        for file in path.glob('**/*'):
            if file.is_file() and file.suffix in suffixes:
                matching_files.append(file)
    
    return matching_files

if __name__ == "__main__":
    cli_args = cli_parser()
    path_in = Path(cli_args.pop("input"))
    file_out = Path(cli_args.pop("output"))
    verbose = cli_args.pop("verbose")
    file_list = get_files_with_suffix(path_in)

    print("Files and their submodule definitions:")
    for file_name in file_list:
        hdl_file = HDLParser(file_name)
        hdl_file.parse()
        if verbose:
            print_tree(hdl_file.tree.root_node, print_all_children=True)
        modules = hdl_file.get_modules()
        print(file_name, modules)

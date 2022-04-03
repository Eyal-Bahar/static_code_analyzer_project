import re
import sys
import os
from collections import defaultdict



def print_msg(line_number, msg):
    global filename
    print(f"{filename}: Line {line_number}: {msg}")


def check_too_long(line, line_number, error_dict):
    if len(line) > 79:
        error_number = 1
        error_dict[line_number].append(error_number)
        msg = "S001 Too long"
        print_msg(line_number, msg) # print(f"Line {line_number}: S001 Too long")

def check_indentation(line, line_number, error_dict):
    import re
    indentation_length = len(re.findall("^ *", line)[0])
    if (indentation_length % 4) != 0:
        error_number = 2
        error_dict[line_number].append(error_number)
        msg = "S002 Indentation is not a multiple of four"
        print_msg(line_number, msg)

def numer_of_quotes_after(line, idx):
    pattern1 = "[\'\"]"
    pattern2 = '"""'
    patt_1_len = len(re.findall(pattern1, line[idx:]))
    patt_2_len = len(re.findall(pattern2, line[idx:]))
    return patt_1_len + patt_2_len


def check_if_in_a_comment(line, idx):
    hashs_list = [m.start() for m in re.finditer("#", line)]
    for hash_idx in hashs_list:
        if (numer_of_quotes_after(line, hash_idx) % 2) == 0:
            if idx > hash_idx:
                return True
    return False


def check_semi_col(line, line_number, error_dict):
    semi_col_list = [m.start() for m in re.finditer(";", line)]
    for semi_col_idx in semi_col_list:
        n_qoutes = numer_of_quotes_after(line, semi_col_idx)
        in_a_string = (n_qoutes % 2)
        in_a_comment = check_if_in_a_comment(line, semi_col_idx)  # if there is "#" before ";"
        if not in_a_string and not in_a_comment: # if its even its not part of a string
            error_number = 3
            error_dict[line_number].append(error_number)
            msg = "S003 Unnecessary semicolon"
            print_msg(line_number, msg)
            return


def check_hash_space(line, line_number, error_dict):
    hash_list = [m.start() for m in re.finditer("#", line)]
    is_comment_line = False
    for hash_idx in hash_list:
        if hash_idx == 0:
            is_comment_line = True
            continue
        in_a_string = numer_of_quotes_after(line, hash_idx) % 2
        in_a_comment = check_if_in_a_comment(line, hash_idx)
        if not in_a_string and not in_a_comment:
            if line[hash_idx - 1] != " " or line[hash_idx - 2] != line[hash_idx - 1]:
                error_number = 4
                error_dict[line_number].append(error_number)
                msg = "S004 At least two spaces required before inline comments"
                print_msg(line_number, msg)
                return is_comment_line
    return is_comment_line


def check_TODO(line, line_number, error_dict):
    pattern1 = "[Tt][Oo][Dd[Oo]"
    TODO_idxs = [m.start() for m in re.finditer(pattern1, line)]
    for TODO_idx in TODO_idxs:
        in_a_comment = check_if_in_a_comment(line, TODO_idx)
        if in_a_comment:
            error_number = 5
            error_dict[line_number].append(error_number)
            msg = "S005 TODO found"
            print_msg(line_number, msg)
            return


def check_blank_lines(line, line_number, blank_lines, error_dict):
    """ Docstring. """
    is_blank_line = (line == "\n")
    if is_blank_line:
        blank_lines.append(line_number)
    if (line_number-3) in blank_lines and (line_number-1) in blank_lines and (line_number-2) in blank_lines:
        error_number = 6
        error_dict[line_number].append(error_number)
        msg = "S006 More than two blank lines used before this line"
        print_msg(line_number, msg)


def class_construction_line(line):
    first_char_idx = len(line) - len(line.lstrip())
    if line[first_char_idx: (first_char_idx +5)] == "class":
        return True


def func_construction_line(line):
    first_char_idx = len(line) - len(line.lstrip())
    if line[first_char_idx: (first_char_idx + 3)] == "def":
        return True


def check_spaces_at_declaration(line, line_number, error_dict):
    if class_construction_line(line):
        striped_line = line.lstrip(" ").lstrip("class")
        if striped_line[0] == " " and striped_line[1] == " ":
            # error_number = 7
            msg = "S007 Too many spaces after 'class'"
            error_dict[line_number].append(msg)
            print_msg(line_number, msg)
    if func_construction_line(line):
        striped_line = line.lstrip(" ").lstrip("def")
        if striped_line[0] == " " and striped_line[1] == " ":
            msg = "S007 Too many spaces after 'def'"
            error_dict[line_number].append(msg)
            print_msg(line_number, msg)
    # I found also this "simpler" solution:
    #   def check_007(s):
            #return re.match(r"[ ]*(?:class|def) ( )+", s)

def list_files_from_input(input_path):
    """ Return a list of files to check on """
    input_path = rf"{input_path}"
    file_list = []
    # check if path leads to specific file or to directly
    if input_path[-2:] == "py":
        file_list.append(input_path)
        return file_list
    all_files = os.listdir(input_path)
    for file in all_files:
        if file.endswith(".py"):
            file_list.append("\\".join([input_path, file]))
    return file_list


def check_class_camel_case(line, line_number, error_dict):
    if class_construction_line(line):
        name_extracted = re.match(r"[ ]*class (?P<name>\w+)", line)
        if name_extracted:
            class_name = name_extracted["name"]
            camel_case_regex = r"(?:[A-Z][a-z0-9]+)+"
            if not re.match(camel_case_regex, class_name):
                msg = f"S008 Class name '{class_name}' should use CamelCase"
                # error_number = 8
                error_dict[line_number].append(msg)
                print_msg(line_number, msg)


def is_camel_case(*code):
    condition = r"[a-z_0-9]+"
    return all([bool(re.match(condition, snippet)) for snippet in list(code)])


def check_func_snake_case(line, line_number, error_dict):
    if func_construction_line(line):
        func_name = line.lstrip(" ").lstrip("def").lstrip(" ").split('(')[0]
        if not is_camel_case(func_name):
            msg = f"S009 Function name '{func_name}' should use snake_case"
            error_dict[line_number].append(msg)
            print_msg(line_number, msg)


def check_arg_name_snake_case(code, line_number, filename, error_dict):
    import ast
    with open(filename) as g:
        script = g.read()
        tree = ast.parse(script)
        nodes = ast.walk(tree)
        for node in nodes:
            if isinstance(node, ast.FunctionDef):
                if node.lineno == line_number:
                    arg_names = [a.arg for a in node.args.args]  # name [a.name for a in function.names]
                    for arg_name in arg_names:
                        if not is_camel_case(arg_name):
                            msg = f"S010 Argument name '{arg_name}' should use snake_case"
                            error_dict[line_number].append(msg)
                            print_msg(line_number, msg)


def check_var_name_snake_case(line, line_number, filename, error_dict):
    import ast
    with open(filename) as g:
        script = g.read()
        tree = ast.parse(script)
        nodes = ast.walk(tree)
        for node in nodes:
            if isinstance(node, ast.Name) and  isinstance(node.ctx, ast.Store):
                var_name = node.id
                if not is_camel_case(var_name) and node.lineno == line_number:
                        msg = f"S011 Variable '{var_name}' in function should be snake_case"
                        error_dict[line_number].append(msg)
                        print_msg(line_number, msg)


def check_default_mutable(line, line_number, error_dict):
    import ast
    with open(filename) as g:
        script = g.read()
        tree = ast.parse(script)
        nodes = ast.walk(tree)
        for node in nodes:
            if isinstance(node, ast.FunctionDef):
                if node.lineno == line_number:
                    for defaults in node.args.defaults:
                        if isinstance(defaults, ast.List) or isinstance(defaults, ast.Dict):
                            msg = f"S012 Default argument value is mutable"
                            error_dict[line_number].append(msg)
                            print_msg(line_number, msg)



def static_code_analyzer(file):
    error_dict = defaultdict(lambda: [])
    error_list = {1: "S001 Too long",
                  2: "S002 Indentation is not a multiple of four",
                  3: "S003 Unnecessary semicolon",
                  4: "S004 At least two spaces required before inline comments",
                  5: "S005 TODO found",
                  6: "S006 More than two blank lines used before this line",
                  }
    with open(file) as f:
        global filename
        filename = file
        Lines = f.readlines()
        line_number = 0
        blank_lines = []
        for line in Lines:
            line_number += 1
            check_too_long(line, line_number, error_dict) # S001
            check_indentation(line, line_number, error_dict) # S002
            check_semi_col(line, line_number, error_dict) # S003
            is_comment_line = check_hash_space(line, line_number, error_dict) # S004
            # if not is_comment_line:
            check_TODO(line, line_number, error_dict) # S005
            check_blank_lines(line, line_number, blank_lines, error_dict) # S006
            check_spaces_at_declaration(line, line_number, error_dict) # S007
            check_class_camel_case(line, line_number, error_dict) # S008
            check_func_snake_case(line, line_number, error_dict) # S009
            check_arg_name_snake_case(line, line_number, filename, error_dict) #S010
            check_var_name_snake_case(line, line_number,filename, error_dict)  # S011
            check_default_mutable(line,line_number, error_dict) # S012


def main():
    # test = r"C:\hyper_skill\static_code_analyzer_project\Static Code Analyzer\task\analyzer\test.txt"
    # code_path = input()
    input_path = r"C:\hyper_skill\static_code_analyzer_project\Static Code Analyzer\task\test\test_6.py"
     # can be directoy or file
    file_list = list_files_from_input(sys.argv[1])
    for file in file_list:
        static_code_analyzer(file)


if __name__ == '__main__':
    main()
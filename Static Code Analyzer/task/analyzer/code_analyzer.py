import re

def check_too_long(line, line_number):
    if len(line) > 79:
            print(f"Line {line_number}: S001 Too long")

def check_indentation(line, line_number):
    import re
    indentation_length = len(re.findall("^ *", line)[0])
    if (indentation_length % 4) != 0:
        print(f"Line {line_number}: S002 Indentation is not a multiple of four")

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


def check_semi_col(line, line_number):
    semi_col_list = [m.start() for m in re.finditer(";", line)]
    for semi_col_idx in semi_col_list:
        n_qoutes = numer_of_quotes_after(line, semi_col_idx)
        in_a_string = (n_qoutes % 2)
        in_a_comment = check_if_in_a_comment(line, semi_col_idx)  # if there is "#" before ";"
        if not in_a_string and not in_a_comment: # if its even its not part of a string
            print(f"Line {line_number}: S003 Unnecessary semicolon")
            return


def check_hash_space(line, line_number):
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
                print(f"Line {line_number}: S004 At least two spaces required before inline comments")
                return is_comment_line
    return is_comment_line


def check_TODO(line, line_number):
    pattern1 = "[Tt][Oo][Dd[Oo]"
    TODO_idxs = [m.start() for m in re.finditer(pattern1, line)]
    for TODO_idx in TODO_idxs:
        in_a_comment = check_if_in_a_comment(line, TODO_idx)
        if in_a_comment:
            print(f"Line {line_number}: S005 TODO found")
            return


def check_blank_lines(line, line_number, blank_lines):
    is_blank_line = (line == "\n")
    if is_blank_line:
        blank_lines.append(line_number)
    if (line_number-3) in blank_lines and (line_number-1) in blank_lines and (line_number-2) in blank_lines:
        print(f"Line {line_number}: S006 More than two blank lines used before this line")


def main():
    # test = r"C:\hyper_skill\static_code_analyzer_project\Static Code Analyzer\task\analyzer\test.txt"
    code_path = input()
    test = r"C:\hyper_skill\static_code_analyzer_project\Static Code Analyzer\task\test\test_6.py"
    with open(code_path) as f:
        Lines = f.readlines()
        line_number = 0
        blank_lines = []
        for line in Lines:
            line_number += 1
            check_too_long(line, line_number)
            check_indentation(line, line_number)
            check_semi_col(line, line_number)
            is_comment_line = check_hash_space(line, line_number)
            # if not is_comment_line:
            check_TODO(line, line_number)
            check_blank_lines(line, line_number, blank_lines)

if __name__ == '__main__':
    main()
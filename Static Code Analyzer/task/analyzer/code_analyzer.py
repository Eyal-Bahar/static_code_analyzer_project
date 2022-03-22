# write your code here
code_path = input()
with open(code_path) as f:
    Lines = f.readlines()
    line_number = 0
    for line in Lines:
        line_number += 1
        if len(line) > 79:
            print(f"Line {line_number}: S001 Too long")



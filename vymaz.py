x = """
INC


DEC


CALL


CALL



JMP


JMP



PUSH
--
"""


x = x.split("\n")
x = [i for i in x if i != ""]

output = []
for y in x:
    output.append((y, ""))

print(output)
from data import *



grp_things = {
    0x80: "Eb Ib",
    0x81: "Ev Iv",
    0x82: "Eb Ib",
    0x83: "Ev Ib",
    0xD0: "Eb 1",
    0xD1: "Ev 1",
    0xD2: "Eb CL",
    0xD3: "Ev CL",
    0xF6: "Eb",
    0xF7: "Ev",
    0xFE: "Eb",
    0xFF: "Ev"
}

new_updated = dict()


# # Fix parameters of grp instructions
# for name, instructions in INSTRUCTIONS_v2.items():
#     new_instructions = []
#     for props, info in instructions:
#         if info['opcode'] in grp_things:
#             new_instructions.append((grp_things[info['opcode']], info))
#         else:
#             new_instructions.append((props, info))

#     new_updated[name] = new_instructions


# Fix length of Jb/Jv instructions
for name, instructions in INSTRUCTIONS_v2.items():
    new_instructions = []
    for props, info in instructions:
        if 'Jb' in props in props:
            info['expected_length'] = 2
        elif 'Jv' in props:
            info['expected_length'] = 3
        new_instructions.append((props, info))


    new_updated[name] = new_instructions


print("-----------------")
print("-----------------")
print("-----------------")
print("-----------------")
print("-----------------")
print("-----------------")
print("-----------------")
print("-----------------")
print("-----------------")
print("-----------------")
print(new_updated)
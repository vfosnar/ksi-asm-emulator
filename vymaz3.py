from data import *




def calculate_expected_length(params: str) -> int:
    exp_length = 1
    has_modrm = False

    for param in params.split(" "):
        if len(param) < 2 or param[1].isupper():
            continue
        
        if param[0] in ["E", "G", "S", "M"]:
            has_modrm = True

        if param[1] == "p":
            exp_length += 4
        
        if param[0] == "O":
            exp_length += 2
        if param[0] == "I":
            exp_length += 1 if param[1] == "b" else 2
        if param[0] == "E":
            # ? Největší možný počet - není to úplně tak jak by to mělo být, ale není čas, takže tak no.
            exp_length += 2 
            # Jestli chcete něco lepšího, tak si to udělejte sami.
    
    # Snad by to mohlo být cajk
    return exp_length + 1 if has_modrm else exp_length


# for name, instrctions in INSTRUCTIONS_v2.items():
#     INSTRUCTIONS_v3[name] = []

#     for params, info in instrctions:
#         info["expected_length"] = calculate_expected_length(params)

#         INSTRUCTIONS_v3[name].append((params, info))

# print(INSTRUCTIONS_v3)


# Get name of all instructions, that take no argument (param == "")
# i = 0
# for name, instructions in INSTRUCTIONS_v2.items():
#     for params, info in instructions:
#         # i += 1
#         # print(i)
#         if params == "":
#             # print(name)
#             # break


# # print(len(INSTRUCTIONS_WITHOUT_PARAMETER))



# wiht_0 = set()
# for name, instructions in INSTRUCTIONS_v2.items():
#     if "0" in name and name[:-1] not in INSTRUCTIONS_WITHOUT_PARAMETER:
#         # print("----", name)
#         wiht_0.add(name)

# # print(INSTRUCTIONS_WITHOUT_PARAMETER - wiht_0)
# # print(wiht_0)


import re



# Example usage
assembly_string = "MOV ax, bx\nMOV labelbx, [clo+2]"
result = capitalize_registers(assembly_string)
print(result)

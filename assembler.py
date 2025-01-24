from data import *
from disassembler import *
import re


def get_byteslength(instruction, args):
    # 3 možnosti:
    # - Immutable
    # - Register
    # - Memmory
    #
    # Size:
    # byte/word/(none)
    #
    # Taky potřebuju vědět:
    # Který opcode

    output = Instruction()

    output.operation = "MOV"  # - TODO: extract from line
    output.size = 2  # Vyčíst z idk

    ...


def parse_param(p: str) -> 'Parameter':  # Part of assembler
    """
    ! Work in progress. Yet can't handle labels nor math (MOV [label + 2], 42)
    ? Perhaps regex would be usefull??
    pls help
    """
    # Register
    if p in REGISTERS:
        return Register(p)

    # Immutable
    try:
        print(parse_number(p))
        return Immutable(parse_number(p))
    except:
        pass

    # Memmory
    if p[0] == '[' and p[-1] == "]":
        p = p[1:-1]
        a = Memmory(None, None)
        for r in MOD_00_RM:
            if r in p:
                a.source = r
                p = p.replace(r + '+', "+")
                break
        else:
            raise Exception("Nebyl rozpoznán segment")

        if p[0] == "+":
            p = p.replace('+', '')
            # If is not ok, it's the users problem.
            a.displacement = parse_number(p)

        return a

    # Pointer
    if "PTR" in p:
        p.replace("PTR", "", 1)  # Hope not
        p.replace("FAR", "", 1)
        return Label(p, include_segment=True)

    raise Exception(f"Nebylo možné zpracovat parametr {p}")


def assemble(code: str) -> list[int]:
    labels = {}
    byte_length = 0  # TODO: rename

    templates = []
    segments_templates = []

    for i, line in enumerate(code.split("\n")):
        line = re.sub(r'\s+', ' ', line)  # Make all whitespace one space

        if line == "":
            continue

        if line.startswith("segment"):
            segment = line.split(" ")[1]
            labels[segment] = i
            segments_templates.append([])
            continue

        label, instr, args = parse_line_parts(line)
        size = get_instruction_size(args)

        if label != "":
            labels[label] = byte_length

        if instr+str(size) not in INSTRUCTIONS_v2:
            raise Exception(f"Unknown instruction {instr}")

        possible_codes = INSTRUCTIONS_v2[instr+str(size)]

        for instr_params, info in possible_codes:
            if matches_args(instr_params.split(" "), args):
                segments_templates[-1].append((instr_params, args, info))
                break
        else:
            raise Exception(f"Invalid arguments for instruction {instr}")

        byte_length += info.expected_bytes
    
    bytecode = []

    for templates in segments_templates:
        for params, args, info in templates:
            bytes = convert_to_bytes(args, params, info)

            if len(bytes) != info.expected_bytes:
                # 844 - random number, kdybych někde jinde přidával stejnou message
                raise Exception(f"Chyba emulátoru. Prosím napiš na Diskusní fórum úlohy. (ErrCode: 844)") 
            
            bytecode.append(bytes)
        
        # TODO: Doplnit None do nějakého násobku 2 nebo tak??
        bytecode.extend([None] * 42)
        
    ...


def eval_label(arg: str, labels: dict[str, int]) -> str:
    # TODO!!
    ...


def parse_line_parts(line: str) -> tuple[str, str, list[str]]:
    label, line = line.split(" ", 1)  # If no label, empty string
    instr, line = line.split(" ", 1)
    # regex to split by ';' but ignore semicolons within strings
    line = re.split(r'(?<!");', line, 1)[0]

    args = [l.strip() for l in line.split(",")]

    return label, instr, args


# def get_bytecode_info(instruction, args) -> dict[str, int]:
#     assert instruction in INSTRUCTIONS

#     possible_codes = INSTRUCTIONS[instruction]

#     prefix = None
#     for arg in args:
#         for test_prefix in PREFIXES:
#             if test_prefix in arg:
#                 prefix = prefix

#     if len(possible_codes) == 1:
#         # TODO: Ještě počítat s prefixy!!!!
#         return possible_codes[0][2]  # TODO: Upravit instructions table

#     # a) Memmory (obsahuje "[" a "]")
#     #  - a1) Z ModR/M (kód Eb/Ev/Ew)
#     #  - a2) Přímo encoded bez ModR/M (kód Ob/Ov) ((není Ow))
#     # b) Register (je to register)
#     #  - b1) General register (kód Gb/Gv/Gw)
#     #  - b2) Register form ModR/M (kód Eb/Ev/Ew)
#     #  - b3) Konkrétní registr (AX, AL, AH, ..., SI, BP, ...)
#     #  - b4) Segment register z modr/m (kód Sw)
#     # c) Immediate
#     #  - c1) Kód Ib/Iv/Iw
#     #  - c2) Pointer - JMP, CALL (kód Ap)
#     #  - c3) Relative - JMP, CALL (kód Jb/Jv)
#     #  - c4) 1 - INT (kód 1)
#     #  - c5) 3 - INT (kód 3)

#     # Get operation size (byte/word/none)

#     for code in possible_codes:
#         # Try to match args with code

#         ...
#     ...


def get_instruction_size(args: list[str]) -> int:
    """Returns 0/8/16"""
    if args == []:
        return 0

    size = None

    for arg in args:
        figured = None
        if "byte " in arg.lower():
            figured = 8
        elif "word " in arg.lower():
            figured = 16

        elif arg in RM_8_REGS:
            figured = 8
        elif arg in RM_16_REGS or arg in SEG_REGS:
            figured = 16

        if size is None:
            size = figured

        if figured is not None and size != figured:
            raise Exception("Incompatible sizes of arguments")

    if size is None:
        raise Exception("No size specified")

    return size


def matches_args(templates: list[str], args: list[str]):
    assert len(templates) == len(args), "Nevalidní počet argumentů"

    for i in range(len(templates)):
        templ, arg = templates[i], args[i].strip()

        # TODO: Tohle vypadá tak strašně. Acho jo. Musím to přepsat
        if arg in SEG_REGS:
            if templ not in SEG_REGS or templ[0] != "S":
                return False
            continue

        if arg in REGISTERS:
            # Is a general register:
            if templ[0] not in ["G", "E"] and templ not in REGISTERS:
                return False
            continue

        if "[" in arg and "]" in arg:
            # Is a memmory:
            if templ[0] not in ["G", "E"]:
                return False
            continue

        # Is an immediate:
        if templ[0] not in ["I", "J", "A"]:
            return False

    return True


# print(matches_args(["Ib"], ["42"]))
# print(matches_args(["Ev"], ["BX"]))
# print(matches_args(["Ev"], ["42"]))
# print(matches_args(["Ev"], ["[42]"]))
# print(matches_args(["Ev"], ["[BX+42]"]))
# print(matches_args(["Gb"], ["AL"]))
# print(matches_args(["Gb"], ["SS"]))
# print(matches_args(["Gb"], ["34"]))

# print("OK")

Template = dict[str, None | int | list[int]]


def convert_to_bytes(args: list[str], parameters: str, info: Template) -> list[int]:

    ...


if __name__ == "__main__":
    assemble("segment code \nllaabel MOV AX, 7")
    ...



from data import *
from disassembler import *
import re



def assemble(code: str) -> list[int]:
    labels = {}
    segment_length = 0
    total_length = 0  # TODO: rename

    templates = []
    segments_templates = []
    labels_segment = {}

    for i, line in enumerate(code.split("\n")):  # Pls keep enumberate for error line info (W.I.P.)
        line = re.sub(r'\s+', ' ', line)  # Make all whitespace one space

        if line.strip() == "":
            continue

        if line.startswith("segment"):
            if segment_length != 0:
                total_length += bytes_remaining_in_segment(segment_length)
        
            segment = line.split(" ")[1]
            segment_length = 0
            labels[segment] = total_length
            segments_templates.append([])

            continue

        label, instr, args = parse_line_parts(line)

        if label != "":
            labels[label] = segment_length
            labels_segment[label] = segment # Bolí mě z toho oči, ale nestíhám. TODO: Přepsat

        if instr in DATA_INSTRUCTIONS:
            match instr[-1]:
                case "B":
                    size = 8
                case "W":
                    size = 16
                case "D":
                    size = 32

            if instr[0] == "D":
                expected_length = len(args) * (size // 8) 
            elif "RES" in instr:
                expected_length = calculate_value(args[0], {}) * (size // 8) # Tady snad nikdo nebude dávat návěští. Hlavně delku potřebuju vědět už tu.
                
            info = {"expected_length": expected_length, 
                    "size": size, # This is so cursed (ale nestíhám, takže to budeš muset přežít)
                    "instruction": instr
            }
            segments_templates[-1].append(("skip", args, info))  # Code duplicity

        else:
            size = get_instruction_size(instr, args)
            if instr+str(size) not in INSTRUCTIONS_v2:
                raise Exception(f"Unknown instruction {instr}")
            possible_codes = INSTRUCTIONS_v2[instr+str(size)]
            for instr_params, info in possible_codes:
                if matches_args(instr_params.split(" "), args):
                    info = info.copy()
                    segments_templates[-1].append((instr_params, args, info))  # Code duplicity
                    break
            else:
                raise Exception(f"Invalid arguments for instruction {instr}")

        segment_length += info["expected_length"]
        total_length += info["expected_length"]

    bytecode = []

    for templates in segments_templates:
        segment_bytecode = []
        for params, args, info in templates:
            bytes = convert_to_bytes(args, params, info, labels, len(bytecode), labels_segment)

            if len(bytes) != info["expected_length"]:
                # 844 - random number, kdybych někde jinde přidával stejnou message
                raise Exception(f"Chyba emulátoru. Prosím napiš na Diskusní fórum úlohy. (ErrCode: 844 - neočekávaný počet bajtů)") 
            
            segment_bytecode.extend(bytes)
        

        segment_bytecode.extend([None for _ in range(bytes_remaining_in_segment(len(segment_bytecode)))])
        bytecode.extend(segment_bytecode)

    return bytecode


def bytes_remaining_in_segment(segment_length: int) -> int:
    # TODO: Write something meaningfull
    return 42  # Even tho 42 is an answer to everything, it is not for this.  

def parse_line_parts(line: str) -> tuple[str, str, list[str]]:
    line = capitalize_registers(line)

    label, line = line.split(" ", 1)  # If no label, empty string
    instr, line = split_on(line, " ")
    instr = instr.upper()
    line, _ = split_on(line, ";")

    args = [l.strip() for l in line.split(",")]

    return label, instr, args


def split_on(line: str, char: str) -> tuple[str, str]:
    return line.split(char, 1) if char in line else (line, "")


def capitalize_registers(assembly_code):
    pattern = r'\b(' + '|'.join(LOWERCASE_REGISTERS) + r')\b'
    return re.sub(pattern, lambda m: m.group(0).upper(), assembly_code)


def get_instruction_size(instruction: str, args: list[str]) -> int:
    """Returns 0/8/16"""
    if instruction in INSTRUCTIONS_WITHOUT_PARAMETER or instruction in DATA_INSTRUCTIONS:
        return 0
    
    if instruction == "INT": # Hnusný hardcode, ale zjistil jsem to pozdě
        return 0 if args[0] == "3" else 8
    
    if instruction in ["JMP", "CALL"]:
        if "SHORT" in args[0]:
            return 8
        if "FAR" in args[0]:
            return 32
        return 16

    if instruction[0] == "J":
        # JZ, JNZ, ...
        return 8

    if args == []:
        return 0

    size = None

    for i, arg in enumerate(args):
        figured = None
        if "byte " in arg.lower():
            figured = 8
            args[i] = arg.replace("byte ", "")
        elif "word " in arg.lower():
            figured = 16
            args[i] = arg.replace("word ", "")

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
    if len(templates) != len(args):
        return False
    # assert len(templates) == len(args), "Nevalidní počet argumentů"

    for i in range(len(templates)):
        templ, arg = templates[i], args[i].strip()

        if templ == "":
            continue

        if templ in ["1", "3"]:
            if arg != templ:
                return False
            continue

        if templ in REGISTERS:
            if arg != templ:
                return False 
            continue

        # TODO: Tohle vypadá tak strašně. Acho jo. Musím to přepsat
        if arg in SEG_REGS:
            if templ not in SEG_REGS and templ[0] != "S":
                return False
            continue

        if arg in REGISTERS:
            # Is a general register:
            if templ[0] not in ["G", "E"] and templ not in REGISTERS:
                return False
            continue

        if "[" in arg and "]" in arg:
            # Is a memmory:
            if templ[0] not in ["E"]:
                return False
            continue

        # Is an immediate:
        if templ[0] not in ["I", "J", "A"]:
            return False

    return True

Template = dict[str, None | int | list[int]]

MAX_SEGMENT_SIZE = 2**16

def convert_to_bytes(args: list[str], parameters: str, info: Template, 
                     labels: dict[str, int], # Hej už se to tu dost množí argumenty - chtělo by to přepracovat :-(
                     curr_instr_idx: int, # TODO: Lepší název
                     labels_segment: dict[str, str] # TODO: Tohle už je cursed. Vymyslet lepší label architecutre
                     ) -> list[int]:
    """Converts instruction to bytecode."""
    # ! NOT TESTED !
    output = []

    if "opcode" not in info: 
        # Is a DATA instruction (Like DB or RESB)

        if info["instruction"][0] == "D": # DB, DW, DD
            for arg in args:
                if arg == "?":

                    output.extend([None] * (info["size"] // 8))
                else: 
                    val = calculate_value(arg, labels)
                    output.extend(int_to_bytes(val, info["size"]))

        elif info["instruction"][0] == "R":  # RESB, RESW, RESD
            output.extend([None] * info["expected_length"])
            
        return output

    # --- 1) Vyplnit celé info
    info["data"] = []
    # Prefixes
    for prefix in PREFIXES:
        for i, arg in enumerate(args):
            if prefix in arg:
                args[i] = arg.replace(prefix, "")
                if prefix in info and info[prefix] is not None:
                    raise Exception("Can't have two prefixes or sth - problem")
                info["prefix"] = PREFIX_CODES[prefix]

    # Parse args
    for i, param in enumerate(parameters.split(" ")):
        arg = args[i]

        if param == "":
            continue

        if param in REGISTERS:
            # Encoded in opcode, no more details needed
            continue

        if "FAR" in arg: # Tohle určitě patří na lepší místo
            arg = arg.replace("FAR ", "")
            arg = arg.strip()

        match param[0]:
            case "A":
                if ":" in arg:
                    seg, off = [p.strip() for p in arg.split(":")]
                    output.extend(int_to_bytes(calculate_value(off, labels), 16))
                    output.extend(int_to_bytes(calculate_value(seg, labels), 16))
                else:
                    # FAR JMP/CALL 
                    if arg not in labels:
                        if "+" in arg:
                            raise Exception(f"Při FAR JMP/CALL prosím nepoužívejte matematiku. (kdyby něco, pište na DF)")
                    
                    output.extend(int_to_bytes(labels[arg], 16))
                    output.extend(int_to_bytes(labels[labels_segment[arg]], 16)) # So cursed
                    
            case "J":
                # Relative offset
                # Calculate distance, assert distance < 2**x
                desitny = calculate_value(arg, labels)
                dist = desitny - curr_instr_idx
                size = 8 if param[1] == "b" else 16
                bytes = int_to_bytes(dist, size)
                info["data"].extend(bytes)

            case "I":
                val = calculate_value(arg, labels)
                size = 8 if param[1] == "b" else 16
                info["data"].extend(int_to_bytes(val, size))

            case "G":
                reg_val = 0
                if param[1] == "b":
                    reg_val = RM_8_REGS.index(arg)
                else:
                    reg_val = RM_16_REGS.index(arg) 

                if "modrm" not in info: # Code triplicity
                    info["modrm"] = 0

                info["modrm"] += reg_val *8  # Reg part of modrm

            case "E":
                if "modrm" not in info: # Code triplicity
                    info["modrm"] = 0

                rm_val, mod_val = 0, 0
                is_special = False  # if mod=00 and rm=110 (only 16 displacement)
                if arg[0] == "[" and arg[-1] == "]":
                    # Assert arg is without prefix
                    arg = arg[1:-1]

                    for i, regref in enumerate(MOD_00_RM):
                        if regref in arg:
                            rm_val = i
                            arg = arg.replace(regref, "")
                            break
                    else:
                        is_special = True
                        rm_val = 6 # Only displacement - protože prostě někdo si řelk, jo, tohle je dobrý nápad. viz tabulka

                    if arg != "":
                        displ = calculate_value(arg, labels)
                        size = 8 if displ < 2**8 else 16
                        if not is_special:
                            info["data"].extend(int_to_bytes(displ, size))
                            mod_val = size // 8
                        else:
                            info["data"].extend(int_to_bytes(displ, 16))


                else:
                    mod_val = 3  # Selects register 
                    if param[1] == "b":
                        rm_val = RM_8_REGS.index(arg)
                    else:
                        rm_val = RM_16_REGS.index(arg)

                info["modrm"] += rm_val
                info["modrm"] += mod_val * 64

                
            case "S":
                # Segment register
                if "modrm" not in info: # Code triplicity
                    info["modrm"] = 0
                reg_val = SEG_REGS.index(arg)
                info["modrm"] += reg_val * 8
                # ? Snad je to správně

    if "E" in "".join(parameters):
        to_fill = info["expected_length"] - len(info["data"]) - (1 if "prefix" in info else 0) - (1 if "modrm" in info else 0) - 1
        info["data"].extend([0x90] * to_fill)
    # 1) Register / Memmory (=> ModR/M + možný displacement - taky podle toho upravid Mod) 
    # 2) Ap (pointer) -> uložit segment a offset
    # 3) I (immediate) -> uložit hodnotu


    # --- 2) Předělat info na bytecode
    if "prefix" in info and info["prefix"] is not None:
        output.append(info["prefix"])

    output.append(info["opcode"])

    if "modrm" in info:
        output.append(info["modrm"])

    output.extend(info["data"])

    return output


def calculate_value(arg: str, labels: dict[str, int]) -> int | None:
    """Returns the value of the argument."""
    parts = re.split(r"(?=[+-])", arg) # Splits by + and -, but keeps it in
    runnung_sum = 0

    for part in parts:
        if part == "":
            continue

        sign = "-" if part[0] == "-" else "+"
        part = part.replace(sign, "")
        part = part.strip()

        part_val = 0

        if part[0].isdigit():
            part_val = parse_number(part)
        else:
            assert part in labels, f"Label \"{part}\" is not defined"
            part_val = labels[part]

        runnung_sum += part_val if sign == "+" else -part_val

    return runnung_sum


def parse_number(s: str) -> int:
    # Parses sum of numbers and works with hex and binary
    # Like: "3+4" -> 7
    # "0Fh+4" -> 19
    if s[-1] == "h":
        return int(s[:-1], 16)
    if s[-1] == "b":
        return int(s[:-1], 2)
    return int(s)


def int_to_bytes(val: int, size: int) -> list[int]:
    """Returns list of bytes, of the number in little endian."""
    output = []

    for _ in range(size // 8):
        output.append(val % 2**8)
        val //= 2**8

    return output

if __name__ == "__main__":
    # print(matches_args(["Ib"], ["42"]))
    # print(matches_args(["Ev"], ["BX"]))
    # print(matches_args(["Ev"], ["42"]))
    # print(matches_args(["Ev"], ["[42]"]))
    # print(matches_args(["Ev"], ["[BX+42]"]))
    # print(matches_args(["Gb"], ["AL"]))
    # print(matches_args(["Gb"], ["SS"]))
    # print(matches_args(["Gb"], ["34"]))

    # print("OK")
    # print(calculate_value("42", {}))
    # print(calculate_value("42+42", {}))
    # print(calculate_value("42-42", {}))
    # print(calculate_value("42+42-42", {}))
    # print(calculate_value("lbl", {"lbl": 42}))
    # print(calculate_value("lbl+42", {"lbl": 42}))
    # print(calculate_value("lbl-42", {"lbl": 42}))
    # print(calculate_value("lbl- 42 + NoTomeUndefined", {"lbl": 42}))
    # print(matches_args(["3"], ["3"]))
    # print(matches_args(["Eb", "Gb"], ["AL", "[32]"]))
    # print(calculate_value("42+23-lbl", {"lbl": 42}))
    # print(calculate_value("", {"lbl": 42}))
    # print(matches_args(["AL"], ["AH"]))
    print(matches_args(["Sw", "Ew"], ["DS", "BX"]))


    code = """
segment code
label   MOV AX, 7
        MOV BX, 42
        ADD AX, BX
        INC AX
        HLT
    """

    code2 = """
segment code
        dec byte [bx+2]
label   DEC byte [BX+2]
        MOV AX, label

segment extra_segment
        MOV AX, 42
        MOV BX, 42
        ADD AX, BX
        INC AX
        
"""

    code3 = """
segment code
        MOV DS, BX
"""

    code4 = """
segment data
n        DB 42, n, navesti
navesti dd 42, n
"""

    code5 = """
segment code
        MOV BX, data
        MOV DS, BX
        MOV [n], byte 042

segment data
n       db 42
x       resb 4
y       db 0ABh
"""

    code6 = """
segment test
        JMP FAR [BX]
    
segment functions
        resb 42
label   HLT

"""

    code7 = """
segment code
        NOP
        NOP
        HLT

segment stack
        resb 16
        db 14
dno     db ?
n       db 42
"""


    # program = assemble("segment code \nllaabel ADD AX, BX")
    program = assemble(code7)
    print(program)
    # print([hex(b) for b in program if b is not None])

    # assemble("segment code \nllaabel JMP lbl_02")


    
    ...



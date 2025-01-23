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
    segments = {}
    byte_length = 0  # TODO: rename

    for i, line in enumerate(code.split("\n")):
        line = re.sub(r'\s+', ' ', line)  # Make all whitespace one space

        if line == "":
            continue

        if line.startswith("segment"):
            segment = line.split(" ")[1]
            segments[segment] = i
            continue

        label, instr, args, comment = parse_parts(line)

        if instr not in INSTRUCTIONS:
            raise Exception(f"Unknown instruction {instr}")

    ...


def parse_parts(line: str) -> tuple[str, str, list[str], str]:
    label, line = line.split(" ", 1)  # If no label, empty string
    instr, line = line.split(" ", 1)
    comment = ""

    if ";" in line:
        line, comment = line.split(";", 1)

    args = [l.strip() for l in line.split(",")]

    return label, instr, args, comment


def get_bytes_length(instruction, args):
    assert instruction in INSTRUCTIONS

    possible_codes = INSTRUCTIONS[instruction]

    if len(possible_codes) == 1:
        return possible_codes[0][2]  # TODO: Upravit instructions table

    # a) Memmory (obsahuje "[" a "]")
    #  - a1) Z ModR/M (kód Eb/Ev/Ew)
    #  - a2) Přímo encoded bez ModR/M (kód Ob/Ov) ((není Ow))
    # b) Register (je to register)
    #  - b1) General register (kód Gb/Gv/Gw)
    #  - b2) Register form ModR/M (kód Eb/Ev/Ew)
    #  - b3) Konkrétní registr (AX, AL, AH, ..., SI, BP, ...)
    #  - b4) Segment register z modr/m (kód Sw)
    # c) Immediate
    #  - c1) Kód Ib/Iv/Iw
    #  - c2) Pointer - JMP, CALL (kód Ap)
    #  - c3) Relative - JMP, CALL (kód Jb/Jv)
    #  - c4) 1 - INT (kód 1)
    #  - c5) 3 - INT (kód 3)

    # Get operation size (byte/word/none)

    for code in possible_codes:
        # Try to match args with code

        ...
    ...


def matches_args(templates: list[str], args: list[str]):
    assert len(templates) == len(args)

    for i in range(len(templates)):
        templ, arg = templates[i], args[i]

    ...


INSTRUCTIONS = {
    'ADD': [('Eb Gb', 0), ('Ev Gv', 1), ('Gb Eb', 2), ('Gv Ev', 3), ('AL Ib', 4), ('AX Iv', 5)],
    'PUSH': [('ES', 6), ('CS', 14), ('SS', 22), ('DS', 30), ('AX', 80), ('CX', 81), ('DX', 82), ('BX', 83), ('SP', 84), ('BP', 85), ('SI', 86), ('DI', 87)],
    'POP': [('ES', 7), ('SS', 23), ('DS', 31), ('AX', 88), ('CX', 89), ('DX', 90), ('BX', 91), ('SP', 92), ('BP', 93), ('SI', 94), ('DI', 95), ('Ev', 143)],
    'OR': [('Eb Gb', 8), ('Ev Gv', 9), ('Gb Eb', 10), ('Gv Ev', 11), ('AL Ib', 12), ('AX Iv', 13)],
    'ADC': [('Eb Gb', 16), ('Ev Gv', 17), ('Gb Eb', 18), ('Gv Ev', 19), ('AL Ib', 20), ('AX Iv', 21)],
    'SBB': [('Eb Gb', 24), ('Ev Gv', 25), ('Gb Eb', 26), ('Gv Ev', 27), ('AL Ib', 28), ('AX Iv', 29)],
    'AND': [('Eb Gb', 32), ('Ev Gv', 33), ('Gb Eb', 34), ('Gv Ev', 35), ('AL Ib', 36), ('AX Iv', 37)],
    'DAA': [('', 39)], 'SUB': [('Eb Gb', 40), ('Ev Gv', 41), ('Gb Eb', 42), ('Gv Ev', 43), ('AL Ib', 44), ('AX Iv', 45)],
    'DAS': [('', 47)], 'XOR': [('Eb Gb', 48), ('Ev Gv', 49), ('Gb Eb', 50), ('Gv Ev', 51), ('AL Ib', 52), ('AX Iv', 53)],
    'SS:': [('prefix', 54)],
    'AAA': [('', 55)],
    'CMP': [('Eb Gb', 56), ('Ev Gv', 57), ('Gb Eb', 58), ('Gv Ev', 59), ('AL Ib', 60), ('AX Iv', 61)],
    'AAS': [('', 63)],
    'INC': [('AX', 64), ('CX', 65), ('DX', 66), ('BX', 67), ('SP', 68), ('BP', 69), ('SI', 70), ('DI', 71)], 'DEC': [('AX', 72), ('CX', 73), ('DX', 74), ('BX', 75), ('SP', 76), ('BP', 77), ('SI', 78), ('DI', 79)],
    'JO': [('Jb', 112)],
    'JNO': [('Jb', 113)],
    'JB': [('Jb', 114)],
    'JNB': [('Jb', 115)],
    'JZ': [('Jb', 116)],
    'JNZ': [('Jb', 117)],
    'JBE': [('Jb', 118)],
    'JA': [('Jb', 119)],
    'JS': [('Jb', 120)],
    'JNS': [('Jb', 121)],
    'JPE': [('Jb', 122)],
    'JPO': [('Jb', 123)],
    'JL': [('Jb', 124)],
    'JGE': [('Jb', 125)],
    'JLE': [('Jb', 126)],
    'JG': [('Jb', 127)],
    'GRP1': [('Eb Ib', 128), ('Ev Iv', 129), ('Eb Ib', 130), ('Ev Ib', 131)],
    'TEST': [('Gb Eb', 132), ('Gv Ev', 133), ('AL Ib', 168), ('AX Iv', 169)],
    'XCHG': [('Gb Eb', 134), ('Gv Ev', 135), ('CX AX', 145), ('DX AX', 146), ('BX AX', 147), ('SP AX', 148), ('BP AX', 149), ('SI AX', 150), ('DI AX', 151)],
    'MOV': [('Eb Gb', 136), ('Ev Gv', 137), ('Gb Eb', 138), ('Gv Ev', 139), ('Ew Sw', 140), ('Sw Ew', 142), ('AL Ob', 160), ('AX Ov', 161), ('Ob AL', 162), ('Ov AX', 163), ('AL Ib', 176), ('CL Ib', 177), ('DL Ib', 178), ('BL Ib', 179), ('AH Ib', 180), ('CH Ib', 181), ('DH Ib', 182), ('BH Ib', 183), ('AX Iv', 184), ('CX Iv', 185), ('DX Iv', 186), ('BX Iv', 187), ('SP Iv', 188), ('BP Iv', 189), ('SI Iv', 190), ('DI Iv', 191), ('Eb Ib', 198), ('Ev Iv', 199)],
    'LEA': [('Gv M', 141)],
    'NOP': [('', 144)],
    'CBW': [('', 152)],
    'CWD': [('', 153)],
    'CALL': [('Ap', 154), ('Jv', 232)],
    'WAIT': [('', 155)], 'PUSHF': [('', 156)], 'POPF': [('', 157)], 'SAHF': [('', 158)], 'LAHF': [('', 159)], 'MOVSB': [('', 164)], 'MOVSW': [('', 165)], 'CMPSB': [('', 166)], 'CMPSW': [('', 167)], 'STOSB': [('', 170)], 'STOSW': [('', 171)], 'LODSB': [('', 172)], 'LODSW': [('', 173)], 'SCASB': [('', 174)],
    'SCASW': [('', 175)],
    'RET': [('Iw', 194), ('', 195)],
    'LES': [('Gv Mp', 196)],
    'LDS': [('Gv Mp', 197)],
    'RETF': [('Iw', 202), ('', 203)],
    'INT': [('3', 204), ('Ib', 205)],
    'INTO': [('', 206)],
    'IRET': [('', 207)],
    'GRP2': [('Eb 1', 208), ('Ev 1', 209), ('Eb CL', 210), ('Ev CL', 211)],
    'AAM': [('I0', 212)],
    'AAD': [('I0', 213)],
    'XLAT': [('', 215)],
    'LOOPNZ': [('Jb', 224)],
    'LOOPZ': [('Jb', 225)],
    'LOOP': [('Jb', 226)],
    'JCXZ': [('Jb', 227)],
    'IN': [('AL Ib', 228), ('AX Ib', 229), ('AL DX', 236), ('AX DX', 237)],
    'OUT': [('Ib AL', 230), ('Ib AX', 231), ('DX AL', 238), ('DX AX', 239)],
    'JMP': [('Jv', 233), ('Ap', 234), ('Jb', 235)],
    'LOCK': [('', 240)],
    'REPNZ': [('', 242)],
    'REPZ': [('', 243)],
    'HLT': [('', 244)],
    'CMC': [('', 245)],
    'GRP3a': [('Eb', 246)],
    'GRP3b': [('Ev', 247)],
    'CLC': [('', 248)],
    'STC': [('', 249)],
    'CLI': [('', 250)],
    'STI': [('', 251)],
    'CLD': [('', 252)],
    'STD': [('', 253)],
    'GRP4': [('Eb', 254)],
    'GRP5': [('Ev', 255)]
}

import re


def classify_instruction(instruction):
    # Patterns for 8-bit and 16-bit instructions
    pattern_8bit = re.compile(
        r'\b(?:AL|BL|CL|DL|AH|BH|CH|DH)\b|\bbyte\b', re.IGNORECASE)
    pattern_16bit = re.compile(
        r'\b(?:AX|BX|CX|DX|SI|DI|BP|SP)\b|\bword\b', re.IGNORECASE)

    if pattern_8bit.search(instruction) and pattern_16bit.search(instruction):
        print("aaaaaaaaa")
    # return

    # Check for invalid combinations (e.g., mixing 8-bit and 16-bit registers or mismatched types)
    invalid_combination = re.compile(r'(\b(?: AL | BL | CL | DL | AH | BH | CH | DH)\b.*\b(?: AX | BX | CX | DX | SI | DI | BP | SP)\b | b(?: AX | BX | CX | DX | SI | DI | BP | SP)\b.*\b(?: AL | BL | CL | DL | AH | BH | CH | DH)\b |                                         \b(?: AX | BX | CX | DX | SI | DI | BP | SP)\b.*\bbyte\b | b(?: AL | BL | CL | DL | AH | BH | CH | DH)\b.*\bword\b)', re.IGNORECASE | re.VERBOSE)

    if invalid_combination.search(instruction):
        return "error"

    # Check for matches
    if pattern_8bit.search(instruction):
        return "8-bits"
    elif pattern_16bit.search(instruction):
        return "16-bits"
    else:
        return "undefined"


# Examples
examples = [
    "AX, 7",
    "[label], AL",
    "[label], 42",
    "BL, CL",
    "BX, 15",
    "byte [label], 5",
    "word [label], 100",
    "AL, AX",  # Invalid combination
    "BX, CH",  # Invalid combination
    "BX, byte 4",  # Invalid combination
    "AL, word 5"   # Invalid combination
]

for example in examples:
    result = classify_instruction(example)
    print(f"Instruction: '{example}' - Classification: {result}")


# OPCODES = [
#     # Parsed from http://www.mlsite.net/8086/#tbl_map1
#     # 0x0_
#     ('ADD', 'Eb Gb'), ('ADD', 'Ev Gv'), ('ADD', 'Gb Eb'), ('ADD',
#                                                            'Gv Ev'), ('ADD', 'AL Ib'), ('ADD', 'AX Iv'), ('PUSH', 'ES'), ('POP', 'ES'),
#     ('OR', 'Eb Gb'), ('OR', 'Ev Gv'), ('OR', 'Gb Eb'), ('OR',
#                                                         'Gv Ev'), ('OR', 'AL Ib'), ('OR', 'AX Iv'), ('PUSH', 'CS'), ('', ''),

#     # 0x1_
#     ('ADC', 'Eb Gb'), ('ADC', 'Ev Gv'), ('ADC', 'Gb Eb'), ('ADC',
#                                                            'Gv Ev'), ('ADC', 'AL Ib'), ('ADC', 'AX Iv'), ('PUSH', 'SS'), ('POP', 'SS'),
#     ('SBB', 'Eb Gb'), ('SBB', 'Ev Gv'), ('SBB', 'Gb Eb'), ('SBB',
#                                                            'Gv Ev'), ('SBB', 'AL Ib'), ('SBB', 'AX Iv'), ('PUSH', 'DS'), ('POP', 'DS'),

#     # 0x2_
#     ('AND', 'Eb Gb'), ('AND', 'Ev Gv'), ('AND', 'Gb Eb'), ('AND',
#                                                            'Gv Ev'), ('AND', 'AL Ib'), ('AND', 'AX Iv'), ('ES:', 'prefix'), ('DAA', ''),
#     ('SUB', 'Eb Gb'), ('SUB', 'Ev Gv'), ('SUB', 'Gb Eb'), ('SUB',
#                                                            'Gv Ev'), ('SUB', 'AL Ib'), ('SUB', 'AX Iv'), ('CS:', 'prefix'), ('DAS', ''),

#     # 0x3_
#     ('XOR', 'Eb Gb'), ('XOR', 'Ev Gv'), ('XOR', 'Gb Eb'), ('XOR',
#                                                            'Gv Ev'), ('XOR', 'AL Ib'), ('XOR', 'AX Iv'), ('SS:', 'prefix'), ('AAA', ''),
#     ('CMP', 'Eb Gb'), ('CMP', 'Ev Gv'), ('CMP', 'Gb Eb'), ('CMP',
#                                                            'Gv Ev'), ('CMP', 'AL Ib'), ('CMP', 'AX Iv'), ('DS:', 'prefix'), ('AAS', ''),

#     # 0x4_
#     ('INC', 'AX'), ('INC', 'CX'), ('INC', 'DX'), ('INC',
#                                                   'BX'), ('INC', 'SP'), ('INC', 'BP'), ('INC', 'SI'), ('INC', 'DI'),
#     ('DEC', 'AX'), ('DEC', 'CX'), ('DEC', 'DX'), ('DEC',
#                                                   'BX'), ('DEC', 'SP'), ('DEC', 'BP'), ('DEC', 'SI'), ('DEC', 'DI'),

#     # 0x5_
#     ('PUSH', 'AX'), ('PUSH', 'CX'), ('PUSH', 'DX'), ('PUSH',
#                                                      'BX'), ('PUSH', 'SP'), ('PUSH', 'BP'), ('PUSH', 'SI'), ('PUSH', 'DI'),
#     ('POP', 'AX'), ('POP', 'CX'), ('POP', 'DX'), ('POP',
#                                                   'BX'), ('POP', 'SP'), ('POP', 'BP'), ('POP', 'SI'), ('POP', 'DI'),

#     # 0x6_  Not relevant for KSI emulator
#     ('--', ''), ('--', ''), ('--', ''), ('--',
#                                          ''), ('--', ''), ('--', ''), ('--', ''), ('--', ''),
#     ('--', ''), ('--', ''), ('--', ''), ('--',
#                                          ''), ('--', ''), ('--', ''), ('--', ''), ('--', ''),

#     # 0x7_
#     ('JO', 'Jb'), ('JNO', 'Jb'), ('JB', 'Jb'), ('JNB', 'Jb'), ('JZ',
#                                                                'Jb'), ('JNZ', 'Jb'), ('JBE', 'Jb'), ('JA', 'Jb'),
#     ('JS', 'Jb'), ('JNS', 'Jb'), ('JPE', 'Jb'), ('JPO',
#                                                  'Jb'), ('JL', 'Jb'), ('JGE', 'Jb'), ('JLE', 'Jb'), ('JG', 'Jb'),

#     # 0x8_
#     ('GRP1', 'Eb Ib'), ('GRP1', 'Ev Iv'), ('GRP1', 'Eb Ib'), ('GRP1', 'Ev Ib'), ('TEST',
#                                                                                  'Gb Eb'), ('TEST', 'Gv Ev'), ('XCHG', 'Gb Eb'), ('XCHG', 'Gv Ev'),
#     ('MOV', 'Eb Gb'), ('MOV', 'Ev Gv'), ('MOV', 'Gb Eb'), ('MOV',
#                                                            'Gv Ev'), ('MOV', 'Ew Sw'), ('LEA', 'Gv M'), ('MOV', 'Sw Ew'), ('POP', 'Ev'),

#     # 0x9_
#     ('NOP', ''), ('XCHG', 'CX AX'), ('XCHG', 'DX AX'), ('XCHG', 'BX AX'), ('XCHG',
#                                                                            'SP AX'), ('XCHG', 'BP AX'), ('XCHG', 'SI AX'), ('XCHG', 'DI AX'),
#     ('CBW', ''), ('CWD', ''), ('CALL', 'Ap'), ('WAIT',
#                                                ''), ('PUSHF', ''), ('POPF', ''), ('SAHF', ''), ('LAHF', ''),

#     # 0xA_
#     ('MOV', 'AL Ob'), ('MOV', 'AX Ov'), ('MOV', 'Ob AL'), ('MOV',
#                                                            'Ov AX'), ('MOVSB', ''), ('MOVSW', ''), ('CMPSB', ''), ('CMPSW', ''),
#     ('TEST', 'AL Ib'), ('TEST', 'AX Iv'), ('STOSB', ''), ('STOSW',
#                                                           ''), ('LODSB', ''), ('LODSW', ''), ('SCASB', ''), ('SCASW', ''),

#     # 0xB_
#     ('MOV', 'AL Ib'), ('MOV', 'CL Ib'), ('MOV', 'DL Ib'), ('MOV', 'BL Ib'), ('MOV',
#                                                                              'AH Ib'), ('MOV', 'CH Ib'), ('MOV', 'DH Ib'), ('MOV', 'BH Ib'),
#     ('MOV', 'AX Iv'), ('MOV', 'CX Iv'), ('MOV', 'DX Iv'), ('MOV', 'BX Iv'), ('MOV',
#                                                                              'SP Iv'), ('MOV', 'BP Iv'), ('MOV', 'SI Iv'), ('MOV', 'DI Iv'),

#     # 0xC_
#     ('', ''), ('', ''), ('RET', 'Iw'), ('RET', ''), ('LES',
#                                                      'Gv Mp'), ('LDS', 'Gv Mp'), ('MOV', 'Eb Ib'), ('MOV', 'Ev Iv'),
#     ('', ''), ('', ''), ('RETF', 'Iw'), ('RETF', ''), ('INT',
#                                                        '3'), ('INT', 'Ib'), ('INTO', ''), ('IRET', ''),

#     # 0xD_
#     ('GRP2', 'Eb 1'), ('GRP2', 'Ev 1'), ('GRP2', 'Eb CL'), ('GRP2',
#                                                             'Ev CL'), ('AAM', 'I0'), ('AAD', 'I0'), ('', ''), ('XLAT', ''),
#     ('CO-PROCESSOR INSTRUCTIONS', ''), ('--', ''), ('--',
#                                                     ''), ('--', ''), ('--', ''), ('--', ''), ('--', ''), ('--', ''),

#     # 0xE_
#     ('LOOPNZ', 'Jb'), ('LOOPZ', 'Jb'), ('LOOP', 'Jb'), ('JCXZ', 'Jb'), ('IN',
#                                                                         'AL Ib'), ('IN', 'AX Ib'), ('OUT', 'Ib AL'), ('OUT', 'Ib AX'),
#     ('CALL', 'Jv'), ('JMP', 'Jv'), ('JMP', 'Ap'), ('JMP', 'Jb'), ('IN',
#                                                                   'AL DX'), ('IN', 'AX DX'), ('OUT', 'DX AL'), ('OUT', 'DX AX'),

#     # 0xF_
#     ('LOCK', ''), ('', ''), ('REPNZ', ''), ('REPZ', ''), ('HLT',
#                                                           ''), ('CMC', ''), ('GRP3a', 'Eb'), ('GRP3b', 'Ev'),
#     ('CLC', ''), ('STC', ''), ('CLI', ''), ('STI', ''), ('CLD',
#                                                          ''), ('STD', ''), ('GRP4', 'Eb'), ('GRP5', 'Ev'),
# ]

# GRPs = {
#     "GRP1": [('ADD', ''), ('OR', ''), ('ADC', ''), ('SBB', ''), ('AND', ''), ('SUB', ''), ('XOR', ''), ('CMP', '')],
#     "GRP2": [('ROL', ''), ('ROR', ''), ('RCL', ''), ('RCR', ''), ('SHL', ''), ('SHR', ''), ('--', ''), ('SAR', '')],
#     "GRP3a": [('TEST', 'Eb Ib'), ('--', ''), ('NOT', ''), ('NEG', ''), ('MUL', ''), ('IMUL', ''), ('DIV', ''), ('IDIV', '')],
#     "GRP3b": [('TEST', 'Ev Iv'), ('--', ''), ('NOT', ''), ('NEG', ''), ('MUL', ''), ('IMUL', ''), ('DIV', ''), ('IDIV', '')],
#     "GRP4": [('INC', ''), ('DEC', ''), ('--', ''), ('--', ''), ('--', ''), ('--', ''), ('--', ''), ('--', '')],
#     "GRP5": [('INC', ''), ('DEC', ''), ('CALL', ''), ('CALL', 'Mp'), ('JMP', ''), ('JMP', 'Mp'), ('PUSH', ''), ('--', '')]
# }

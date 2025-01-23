from disassembler import *

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
    'GRP5': [('Ev', 255)]}

OPCODES = [
    # Parsed from http://www.mlsite.net/8086/#tbl_map1
    # 0x0_
    ('ADD', 'Eb Gb'), ('ADD', 'Ev Gv'), ('ADD', 'Gb Eb'), ('ADD',
                                                           'Gv Ev'), ('ADD', 'AL Ib'), ('ADD', 'AX Iv'), ('PUSH', 'ES'), ('POP', 'ES'),
    ('OR', 'Eb Gb'), ('OR', 'Ev Gv'), ('OR', 'Gb Eb'), ('OR',
                                                        'Gv Ev'), ('OR', 'AL Ib'), ('OR', 'AX Iv'), ('PUSH', 'CS'), ('', ''),

    # 0x1_
    ('ADC', 'Eb Gb'), ('ADC', 'Ev Gv'), ('ADC', 'Gb Eb'), ('ADC',
                                                           'Gv Ev'), ('ADC', 'AL Ib'), ('ADC', 'AX Iv'), ('PUSH', 'SS'), ('POP', 'SS'),
    ('SBB', 'Eb Gb'), ('SBB', 'Ev Gv'), ('SBB', 'Gb Eb'), ('SBB',
                                                           'Gv Ev'), ('SBB', 'AL Ib'), ('SBB', 'AX Iv'), ('PUSH', 'DS'), ('POP', 'DS'),

    # 0x2_
    ('AND', 'Eb Gb'), ('AND', 'Ev Gv'), ('AND', 'Gb Eb'), ('AND',
                                                           'Gv Ev'), ('AND', 'AL Ib'), ('AND', 'AX Iv'), ('ES:', 'prefix'), ('DAA', ''),
    ('SUB', 'Eb Gb'), ('SUB', 'Ev Gv'), ('SUB', 'Gb Eb'), ('SUB',
                                                           'Gv Ev'), ('SUB', 'AL Ib'), ('SUB', 'AX Iv'), ('CS:', 'prefix'), ('DAS', ''),

    # 0x3_
    ('XOR', 'Eb Gb'), ('XOR', 'Ev Gv'), ('XOR', 'Gb Eb'), ('XOR',
                                                           'Gv Ev'), ('XOR', 'AL Ib'), ('XOR', 'AX Iv'), ('SS:', 'prefix'), ('AAA', ''),
    ('CMP', 'Eb Gb'), ('CMP', 'Ev Gv'), ('CMP', 'Gb Eb'), ('CMP',
                                                           'Gv Ev'), ('CMP', 'AL Ib'), ('CMP', 'AX Iv'), ('DS:', 'prefix'), ('AAS', ''),

    # 0x4_
    ('INC', 'AX'), ('INC', 'CX'), ('INC', 'DX'), ('INC',
                                                  'BX'), ('INC', 'SP'), ('INC', 'BP'), ('INC', 'SI'), ('INC', 'DI'),
    ('DEC', 'AX'), ('DEC', 'CX'), ('DEC', 'DX'), ('DEC',
                                                  'BX'), ('DEC', 'SP'), ('DEC', 'BP'), ('DEC', 'SI'), ('DEC', 'DI'),

    # 0x5_
    ('PUSH', 'AX'), ('PUSH', 'CX'), ('PUSH', 'DX'), ('PUSH',
                                                     'BX'), ('PUSH', 'SP'), ('PUSH', 'BP'), ('PUSH', 'SI'), ('PUSH', 'DI'),
    ('POP', 'AX'), ('POP', 'CX'), ('POP', 'DX'), ('POP',
                                                  'BX'), ('POP', 'SP'), ('POP', 'BP'), ('POP', 'SI'), ('POP', 'DI'),

    # 0x6_  Not relevant for KSI emulator
    ('--', ''), ('--', ''), ('--', ''), ('--',
                                         ''), ('--', ''), ('--', ''), ('--', ''), ('--', ''),
    ('--', ''), ('--', ''), ('--', ''), ('--',
                                         ''), ('--', ''), ('--', ''), ('--', ''), ('--', ''),

    # 0x7_
    ('JO', 'Jb'), ('JNO', 'Jb'), ('JB', 'Jb'), ('JNB', 'Jb'), ('JZ',
                                                               'Jb'), ('JNZ', 'Jb'), ('JBE', 'Jb'), ('JA', 'Jb'),
    ('JS', 'Jb'), ('JNS', 'Jb'), ('JPE', 'Jb'), ('JPO',
                                                 'Jb'), ('JL', 'Jb'), ('JGE', 'Jb'), ('JLE', 'Jb'), ('JG', 'Jb'),

    # 0x8_
    ('GRP1', 'Eb Ib'), ('GRP1', 'Ev Iv'), ('GRP1', 'Eb Ib'), ('GRP1', 'Ev Ib'), ('TEST',
                                                                                 'Gb Eb'), ('TEST', 'Gv Ev'), ('XCHG', 'Gb Eb'), ('XCHG', 'Gv Ev'),
    ('MOV', 'Eb Gb'), ('MOV', 'Ev Gv'), ('MOV', 'Gb Eb'), ('MOV',
                                                           'Gv Ev'), ('MOV', 'Ew Sw'), ('LEA', 'Gv M'), ('MOV', 'Sw Ew'), ('POP', 'Ev'),

    # 0x9_
    ('NOP', ''), ('XCHG', 'CX AX'), ('XCHG', 'DX AX'), ('XCHG', 'BX AX'), ('XCHG',
                                                                           'SP AX'), ('XCHG', 'BP AX'), ('XCHG', 'SI AX'), ('XCHG', 'DI AX'),
    ('CBW', ''), ('CWD', ''), ('CALL', 'Ap'), ('WAIT',
                                               ''), ('PUSHF', ''), ('POPF', ''), ('SAHF', ''), ('LAHF', ''),

    # 0xA_
    ('MOV', 'AL Ob'), ('MOV', 'AX Ov'), ('MOV', 'Ob AL'), ('MOV',
                                                           'Ov AX'), ('MOVSB', ''), ('MOVSW', ''), ('CMPSB', ''), ('CMPSW', ''),
    ('TEST', 'AL Ib'), ('TEST', 'AX Iv'), ('STOSB', ''), ('STOSW',
                                                          ''), ('LODSB', ''), ('LODSW', ''), ('SCASB', ''), ('SCASW', ''),

    # 0xB_
    ('MOV', 'AL Ib'), ('MOV', 'CL Ib'), ('MOV', 'DL Ib'), ('MOV', 'BL Ib'), ('MOV',
                                                                             'AH Ib'), ('MOV', 'CH Ib'), ('MOV', 'DH Ib'), ('MOV', 'BH Ib'),
    ('MOV', 'AX Iv'), ('MOV', 'CX Iv'), ('MOV', 'DX Iv'), ('MOV', 'BX Iv'), ('MOV',
                                                                             'SP Iv'), ('MOV', 'BP Iv'), ('MOV', 'SI Iv'), ('MOV', 'DI Iv'),

    # 0xC_
    ('', ''), ('', ''), ('RET', 'Iw'), ('RET', ''), ('LES',
                                                     'Gv Mp'), ('LDS', 'Gv Mp'), ('MOV', 'Eb Ib'), ('MOV', 'Ev Iv'),
    ('', ''), ('', ''), ('RETF', 'Iw'), ('RETF', ''), ('INT',
                                                       '3'), ('INT', 'Ib'), ('INTO', ''), ('IRET', ''),

    # 0xD_
    ('GRP2', 'Eb 1'), ('GRP2', 'Ev 1'), ('GRP2', 'Eb CL'), ('GRP2',
                                                            'Ev CL'), ('AAM', 'I0'), ('AAD', 'I0'), ('', ''), ('XLAT', ''),
    ('CO-PROCESSOR INSTRUCTIONS', ''), ('--', ''), ('--',
                                                    ''), ('--', ''), ('--', ''), ('--', ''), ('--', ''), ('--', ''),

    # 0xE_
    ('LOOPNZ', 'Jb'), ('LOOPZ', 'Jb'), ('LOOP', 'Jb'), ('JCXZ', 'Jb'), ('IN',
                                                                        'AL Ib'), ('IN', 'AX Ib'), ('OUT', 'Ib AL'), ('OUT', 'Ib AX'),
    ('CALL', 'Jv'), ('JMP', 'Jv'), ('JMP', 'Ap'), ('JMP', 'Jb'), ('IN',
                                                                  'AL DX'), ('IN', 'AX DX'), ('OUT', 'DX AL'), ('OUT', 'DX AX'),

    # 0xF_
    ('LOCK', ''), ('', ''), ('REPNZ', ''), ('REPZ', ''), ('HLT',
                                                          ''), ('CMC', ''), ('GRP3a', 'Eb'), ('GRP3b', 'Ev'),
    ('CLC', ''), ('STC', ''), ('CLI', ''), ('STI', ''), ('CLD',
                                                         ''), ('STD', ''), ('GRP4', 'Eb'), ('GRP5', 'Ev'),
]


def calculate_bytes_length(params: str):
    has_modrm = False
    length = 1

    for p in params.split(" "):
        if p == "":
            continue

        if p in REGISTERS:
            continue
        elif p[0] in ["E", "G", "M", "S"]:
            has_modrm = True
        elif p[0] in ["A", "I", "J", "O"]:
            if p[1] == "b":
                length += 1
            elif p[1] in ["v", "w"]:
                length += 2
            elif p[1] == "p":
                length += 6

    return length + 1 if has_modrm else length


for i, (instr, params) in enumerate(OPCODES):
    print(i, instr, params, calculate_bytes_length(params))
